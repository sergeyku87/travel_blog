from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
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
    model = Post

    def get_queryset(self):
        return self.model.objects.filter(
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
        print(self.kwargs['username'])

        return self.model.objects.filter(
            Q(author__username=self.request.user)
            | (
                Q(is_published=True)
                & Q(category__is_published=True)
                & Q(author__username=self.kwargs['username'])
                & Q(pub_date__lte=timezone.now())
            )
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )

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

    def get_queryset(self):
        return self.model.objects.filter(
            Q(author__username=self.request.user)
            | (
                Q(is_published=True)
                & Q(category__is_published=True)
                & Q(pub_date__lte=timezone.now())
            )
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            id=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = Comment.objects.filter(
            post=self.kwargs['post_id']
        ).select_related('author')
        return context


class CommonForPost():
    template_name = 'blog/create.html'
    form_class = PostForm

    def get_object(self):
        return get_object_or_404(
            Post,
            id=self.kwargs['post_id'],
        )


class PostCreate(LoginRequiredMixin, CommonForPost, CreateView):
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


class IsUser(UserPassesTestMixin):
    def test_func(self):
        return str(self.request.user) == self.get_object().author.username

    def get_login_url(self):
        return reverse_lazy(
            'blog:post_detail',
            args=(self.kwargs['post_id'],)
        )


'''
Привет, беда, печаль (((
В PostEdit я не могу подмешать IsUser, тесты выдают ошибку:

AssertionError: Убедитесь, что при отправке формы
редактирования поста неавторизованным пользователем он
перенаправляется на страницу публикации
(/posts/<int:post_id>/).

А с методом post внутри все проходит, как с этим быть ?

Не совсем понял по PermissionRequiredMixin, если классу
PostEdit установить permission_required = 'blog.change_post'
и разным пользователям дать права на редактирование,
то где происходит проверка на авторство, не могут же они,
имея одно лишь право change, менять любой контент,
даже себе не принадлежащий?
'''


class PostEdit(CommonForPost, UpdateView):
    def post(self, request, *args, **kwargs):
        if self.get_object().author != request.user:
            return HttpResponseRedirect(self.get_object().get_absolute_url())
        return super().post(request, *args, **kwargs)


class PostDelete(IsUser, CommonForPost, DeleteView):
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


class CommentEdit(IsUser, UpdateView):
    form_class = CommentForm
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


class CommentDelete(IsUser, DeleteView):
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
