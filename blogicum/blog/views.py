from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Prefetch
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)
from django.views.generic.edit import ModelFormMixin

from blogicum.constants import NUMBER_POSTS_ON_PAGE
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class BaseListMixin:
    paginate_by = NUMBER_POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True,
        ).annotate(
            comment_count=Count('comments')
        ).select_related(
            'author',
            'category',
            'location',
        ).order_by(
            '-pub_date'
        )


class PostsListView(BaseListMixin, ListView):
    template_name = 'blog/index.html'


class CategoryListView(BaseListMixin, ListView):
    template_name = 'blog/category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True,
        )
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs['slug'],
        )


'''
Не знаю на сколько правильно я понял применение класса Prefetch,
но получилась такая вот там простыня получилась)) в конце я обернул в try,
потому что тесты ругались

    @pytest.mark.django_db
    def test_profile(
            user, another_user, user_client, another_user_client,
            unlogged_client
    ):
        user_url = f"/profile/{user.username}/"
        printed_url = "/profile/<username>/"

        User = get_user_model()
        status_code_not_404_err_msg = (
            "Убедитесь, что при обращении к странице несуществующего "
            "пользователя возвращается статус 404."
        )
        try:
            response = user_client.get("/profile/this_is_unexisting_user_name
        except User.DoesNotExist:
>           raise AssertionError(status_code_not_404_err_msg)
E           AssertionError: Убедитесь, что при обращении к странице
несуществующего пользователя возвращается статус 404.


я так понял из за того что get_user_model() не через get_object_or_404
вызывался.

В методах get и  post я ведь могу логику запроса обрабатывать, кому что
показывать, кого куда переадресовать?

Как я понимаю каждый логический запрос, это обращение к базе данных,
посмотри то, сравни с тем, это ведь не хорошо, что мы кне часто обращаемся
так, что на практике с этим делают (я так думаю может, при первом обращении,
вытянуть из бд нужные данные сохранить их в переменные, и потом использовать
в логических операциях) ???
'''


class Profile(ListView):
    paginate_by = NUMBER_POSTS_ON_PAGE
    template_name = 'blog/profile.html'
    model = Post

    def get_object(self):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs['username']
        )

    def get_queryset(self):
        prefetch_for_all = Prefetch(
            'author',
            queryset=self.model.objects.select_related(
                'category',
                'location',
                ).filter(
                is_published=True,
                pub_date__lte=timezone.now(),
                category__is_published=True,
                ).annotate(
                    comment_count=Count('comments')
                ).order_by('-pub_date')
        )
        prefetch_for_author = Prefetch(
            'author',
            queryset=self.model.objects.select_related(
                'category',
                'location',
                ).filter(
                ).annotate(
                    comment_count=Count('comments')
                ).order_by('-pub_date')
        )
        try:
            if str(self.request.user) == self.kwargs['username']:
                return get_user_model().objects.prefetch_related(
                    prefetch_for_author
                ).get(username=self.kwargs['username']).author.all()
            return get_user_model().objects.prefetch_related(
                prefetch_for_all
                ).get(username=self.kwargs['username']).author.all()
        except ObjectDoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['profile'] = self.get_object()
        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email',)

    def get_object(self):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs['username']
        )

    def get_success_url(self):
        return reverse_lazy('blog:index')


class PostDetail(ModelFormMixin, DetailView):
    template_name = 'blog/detail.html'
    form_class = CommentForm
    model = Post

    def get_object(self):
        return get_object_or_404(
            self.model.objects.select_related('author'),
            id=self.kwargs['post_id']
        )

    def get(self, request, *args, **kwargs):
        if (
            self.get_object().is_published
            and self.get_object().category.is_published
            and self.get_object().pub_date < timezone.now()
        ):
            return super().get(request, *args, *kwargs)
        else:
            if self.get_object().author == request.user:
                return super().get(request, *args, *kwargs)
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            post=self.kwargs['post_id']
        ).select_related('author')
        return context


class CommonForPost(LoginRequiredMixin):
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_object(self):
        return get_object_or_404(
            Post,
            id=self.kwargs['post_id'],
        )


class RedirectMixin:
    def post(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super().post(request, *args, **kwargs)


class PostCreate(CommonForPost, CreateView):
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.image = form.cleaned_data['image']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class PostEdit(CommonForPost, RedirectMixin, UpdateView):
    ...


class PostDelete(CommonForPost, RedirectMixin, DeleteView):
    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user}
        )


class CommentAdd(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)


class CommentEditDeleteMixin(LoginRequiredMixin):
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            args=(self.kwargs['post_id'],)
        )

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs['comment_id']
        )


class CommentEdit(CommentEditDeleteMixin, RedirectMixin, UpdateView):
    form_class = CommentForm


class CommentDelete(CommentEditDeleteMixin, DeleteView):
    def post(self, request, *args, **kwargs):
        if (
            self.get_object().author == request.user
            or request.user.is_superuser
        ):
            return super().post(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())
