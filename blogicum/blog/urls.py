from django.urls import path

from .views import (
    CategoryListView,
    CommentAdd,
    CommentDelete,
    CommentEdit,
    EditProfile,
    PostCreate,
    PostEdit,
    PostDelete,
    PostDetail,
    PostsListView,
    Profile,
)

app_name = 'blog'

urlpatterns = [
    path(
        '',
        PostsListView.as_view(),
        name='index'
    ),
    path(
        'category/<slug:slug>/',
        CategoryListView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        Profile.as_view(),
        name='profile'
    ),
    path(
        'profile/<str:username>/edit/',
        EditProfile.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/create/',
        PostCreate.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        PostEdit.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        PostDelete.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/',
        PostDetail.as_view(),
        name='post_detail'
    ),
    path(
        'posts/<int:post_id>/comment/',
        CommentAdd.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:comment_id>/',
        CommentEdit.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:comment_id>/',
        CommentDelete.as_view(),
        name='delete_comment'
    ),
]
