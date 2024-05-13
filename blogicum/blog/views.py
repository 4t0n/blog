from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_list_or_404, get_object_or_404
from django.utils import timezone
from django.views.generic import CreateView

import constants
from .models import Post, Category
from .forms import PostForm


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


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


def category_posts(request: HttpRequest,
                   category_slug: str) -> HttpResponse:
    template = 'blog/category.html'
    post_list = get_list_or_404(
        Category.objects.get(
            slug=category_slug,
        ).category.all(),
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    category = Category.objects.get(slug=category_slug)
    context = {'category': category, 'post_list': post_list}
    return render(request, template, context)
