from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

from .models import Post

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('is_published', 'author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CustomUserForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )
