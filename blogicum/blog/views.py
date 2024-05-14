from typing import Any
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render, get_list_or_404, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView, UpdateView

import constants
from .models import Post, Category
from .forms import PostForm, CustomUserForm

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


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = 10

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        object_list = User.objects.get(
            username=self.kwargs['username'],
        ).author.all()
        context = super().get_context_data(object_list=object_list, **kwargs)
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


def index(request: HttpRequest) -> HttpResponse:
    template = 'blog/index.html'
    post_list = Post.filter_objects.all()[:constants.POSTS_BY_PAGE]
    context = {'post_list': post_list}
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.filter_objects.all(),
        pk=post_id,
    )
    context = {'post': post}
    return render(request, template, context)


# def category_posts(request: HttpRequest,
#                    category_slug: str) -> HttpResponse:
#     template = 'blog/category.html'
#     post_list = get_list_or_404(
#         Category.objects.get(
#             slug=category_slug,
#         ).category.all(),
#         pub_date__lte=timezone.now(),
#         is_published=True,
#         category__is_published=True,
#     )
#     category = Category.objects.get(slug=category_slug)
#     context = {'category': category, 'post_list': post_list}
#     return render(request, template, context)

# https://pocoz.gitbooks.io/django-v-primerah/content/glava-4-sozdanie-social-website/registratsiya-polzovatelei-i-profili-polzovatelei/rasshirenie-modeli-user.html