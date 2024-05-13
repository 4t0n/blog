from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    # path('category/<slug:category_slug>/',
    #      views.category_posts,
    #      name='category_posts',
    #      ),
    path('profile/<slug:username>/',
         views.ProfileListView.as_view(),
         name='profile',
         ),
    path('profile/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile',
         ),
]
