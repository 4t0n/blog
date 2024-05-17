from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.db.models.base import Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import Http404, HttpResponse, HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .models import Category, Comment, Post
from .forms import CommentForm, CustomUserForm, PostForm

User = get_user_model()


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка авторства объекта."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание публикации."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostListView(ListView):
    """Вывод публикаций."""

    model = Post
    paginate_by = 10
    template_name = 'blog/index.html'
    queryset = Post.published_posts.all()


class PostInProfileListView(ListView):
    """Вывод публикаций пользователя."""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        if get_object_or_404(
            User,
            username=self.kwargs['username'],
        ) == self.request.user:
            return Post.objects.filter(
                author__username=self.kwargs['username'],
            ).annotate(
                comment_count=models.Count('comments'),
            ).order_by(
                '-pub_date',
            ).select_related(
                'author',
                'category',
                'location',
            )
        else:
            return Post.published_posts.filter(
                author__username=self.kwargs['username'],
            )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""

    model = User
    form_class = CustomUserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.user


class PostDetailView(DetailView):
    """Вывод публикации."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    queryset = Post.objects.select_related('author', 'category', 'location')

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        if request.user != self.get_object().author:
            self.queryset = Post.published_posts.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.get_object().comments.all()
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование публикации."""

    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        if request.user != self.get_object().author:
            return redirect('blog:post_detail', self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление публикации."""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostInCategoryListView(ListView):
    """Вывод публикаций в категории."""

    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def dispatch(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        if not Category.objects.get(
            slug=self.kwargs['category_slug']
        ).is_published:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Any]:
        return Post.published_posts.filter(
            category__slug=self.kwargs['category_slug'],
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.get(
            slug=self.kwargs['category_slug'])
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(
            Comment,
            post=self.kwargs['post_id'],
            pk=self.kwargs['comment_id']
        )

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(
            Comment,
            post=self.kwargs['post_id'],
            pk=self.kwargs['comment_id']
        )

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.kwargs['post_id']])
