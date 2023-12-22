from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from core.models import PublishedModel
from blogicum.constants import CHARACTERS_IN_STRING, MAX_CHARACTERS


class Post(PublishedModel):
    title = models.CharField(
        'Заголовок',
        max_length=CHARACTERS_IN_STRING,
    )
    text = models.TextField(
        'Текст',
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем —'
            ' можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='author'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Местоположение',
        related_name='place'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
        related_name='posts'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        null=True,
        blank=True,
        upload_to='img_publications',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title[:MAX_CHARACTERS]

    def get_absolute_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.pk}
        )


class Category(PublishedModel):
    title = models.CharField(
        'Заголовок',
        max_length=CHARACTERS_IN_STRING,
    )
    description = models.TextField(
        'Описание',
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы,'
            ' цифры, дефис и подчёркивание.'
        )
    )

    class Meta(PublishedModel.Meta):
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:MAX_CHARACTERS]


class Location(PublishedModel):
    name = models.CharField(
        'Название места',
        max_length=CHARACTERS_IN_STRING,
    )

    class Meta(PublishedModel.Meta):
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:MAX_CHARACTERS]


class Comment(PublishedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий к посту',
        null=True,
        related_name='comments',
    )
    author = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        null=True,
        related_name='comments_author',
    )
    txt = models.TextField(
        verbose_name='Комментарий',
    )

    class Meta(PublishedModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий "{self.author}" на "{self.post}"'

    def get_absolute_url(self):
        return reverse_lazy('blog:post_detail', args=(self.post.id, ))
