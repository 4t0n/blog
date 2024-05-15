from typing import Any
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView

from .models import Post, Category, Comment
from .forms import PostForm, CustomUserForm, CommentForm

User = get_user_model()


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostListView(ListView):
    model = Post
    ordering = '-pub_date'
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_queryset(self) -> QuerySet[Any]:
        return Post.published_posts.annotate(comment_count=models.Count('comments')).all()


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        return Post.objects.filter(author__username=self.kwargs['username']).annotate(comment_count=models.Count('comments')).all()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['profile'] = get_object_or_404(
            User,
            username=self.kwargs['username'],
        )
        return context


class ProfileUpdateView(UpdateView):
    model = User
    form_class = CustomUserForm
    template_name = 'blog/user.html'
    success_url = reverse_lazy('blog:index')

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return self.request.user


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm
        context['comments'] = self.get_object().comments.all()
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            if request.user != self.get_object().author:
                return redirect('blog:post_detail', self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.kwargs['pk']})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostCategoriesListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        object_list = get_list_or_404(
            Category.objects.get(
                slug=self.kwargs['category_slug']
            ).category.all(),
            category__is_published=True
        )
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['category'] = Category.objects.get(slug=self.kwargs['category_slug'])
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_object = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.post_object = get_object_or_404(Post, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form) -> HttpResponse:
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.post_object.pk})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
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
        return reverse('blog:post_detail', kwargs={'pk': self.get_object().post.pk})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(instance=self.object)
        return context

    def get_object(self, queryset: QuerySet[Any] | None = ...) -> Model:
        return get_object_or_404(
            Comment,
            post=self.kwargs['post_id'],
            pk=self.kwargs['comment_id']
        )

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.get_object().post.pk})
