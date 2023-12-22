from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.edit import (
    BaseUpdateView,
    ModelFormMixin,
)
from django.views.generic.detail import BaseDetailView
from django.views.generic.base import TemplateResponseMixin

from .models import Category, Comment, Post
from .forms import CommentForm, PostForm
from blogicum.constants import NUMBER_POSTS_ON_PAGE


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

    def get(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            slug=self.kwargs['slug'],
            is_published=True,
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_queryset()
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            category__slug=self.kwargs['slug']
        )


class ProfileBaseMixin(TemplateResponseMixin):
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs['username']
        )


class Profile(ProfileBaseMixin, MultipleObjectMixin, BaseDetailView):
    paginate_by = NUMBER_POSTS_ON_PAGE

    def get_queryset(self):
        return Post.objects.filter(
            author__username=self.get_object()
        ).select_related(
            'author',
            'category',
            'location',
        ).order_by(
            '-pub_date',
        ).annotate(
            comment_count=Count('comments')
        )

    def get_context_data(self, **kwargs):
        if self.request.user == self.get_object():
            context = super().get_context_data(
                object_list=self.get_queryset(),
                **kwargs
            )
        else:
            context = super().get_context_data(
                object_list=self.get_queryset().filter(
                    is_published=True,
                    pub_date__lte=timezone.now(),
                ),
                **kwargs
            )
        context['profile'] = self.get_object()
        return context


class EditProfile(LoginRequiredMixin, ProfileBaseMixin, BaseUpdateView):
    template_name = 'blog/user.html'
    fields = ('username', 'first_name', 'last_name', 'email',)

    def get_success_url(self):
        return reverse_lazy('blog:index')


class ObjectPostMixin:
    def dispatch(self, request, *args, **kwargs):
        bound = Post.objects.select_related('author',)
        self.publish = get_object_or_404(
            bound,
            id=self.kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.publish.author != request.user:
            return HttpResponseRedirect(self.publish.get_absolute_url())
        return super().post(request, *args, **kwargs)

    def get_object(self):
        return self.publish


class PostDetail(ObjectPostMixin, ModelFormMixin, DetailView):
    template_name = 'blog/detail.html'
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        if (self.publish.is_published
            and self.publish.category.is_published
            and self.publish.pub_date < timezone.now()
        ):
            return super().get(request, *args, *kwargs)
        else:
            if self.publish.author == request.user:
                return super().get(request, *args, *kwargs)
            raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.publish.comments.select_related(
            'author'
        )
        return context


class PostBaseMixin(LoginRequiredMixin,):
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'


class PostCreate(PostBaseMixin, CreateView):

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


class PostEdit(ObjectPostMixin, PostCreate, UpdateView):

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDelete(ObjectPostMixin, PostCreate, DeleteView):

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


class CommentEdit(CommentEditDeleteMixin, UpdateView):
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().author == request.user:
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())


class CommentDelete(CommentEditDeleteMixin, DeleteView):

    def dispatch(self, request, *args, **kwargs):
        if (
            self.get_object().author == request.user
            or request.user.is_superuser
        ):
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())
