from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

import blogicum.constants as constants
from .managers import PostManager

User = get_user_model()


class AvailabilityBaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.',
    )

    class Meta:
        abstract = True


class DateBaseModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Category(AvailabilityBaseModel, DateBaseModel):
    """Модель категории публикации."""

    title = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.',
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title[:constants.REPRESENTATION_LENGTH]


class Location(AvailabilityBaseModel, DateBaseModel):
    """Модель местоположения в публикации."""

    name = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Название места',
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self) -> str:
        return self.name[:constants.REPRESENTATION_LENGTH]


class Post(AvailabilityBaseModel, DateBaseModel):
    """Модель публикации."""

    title = models.CharField(
        max_length=constants.MAX_FIELD_LENGTH,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем '
        '— можно делать отложенные публикации.',
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='post_images',
        blank=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        blank=True,
        on_delete=models.SET_NULL,
        null=True,
        related_name='location',
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category',
        verbose_name='Категория',
    )
    objects = models.Manager()
    published_posts = PostManager()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse('blog:profile', kwargs={'username': self.author})

    def __str__(self) -> str:
        return self.title[:constants.REPRESENTATION_LENGTH]


class Comment(DateBaseModel):
    """Модель комментария публикации."""

    text = models.TextField('Текст комментария')
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментируемая публикация',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комментария',
        related_name='comments',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return self.text[:30]
