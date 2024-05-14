from django.urls import path

from . import views

app_name = 'blog'
urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('category/<slug:category_slug>/',
         views.PostCategoriesListView.as_view(),
         name='category_posts',
         ),
    path('posts/<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('profile/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile',
         ),
    path('profile/<username>/',
         views.ProfileListView.as_view(),
         name='profile',
         ),
]
