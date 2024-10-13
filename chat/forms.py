from django import forms
from blog.models import Likes
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Username', 
                   'class': 'prompt srch_explore'
                   }), 
            max_length=50, 
            required=True
            )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Email', 
                   'class': 'prompt srch_explore'
                   }
            ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Enter Password', 
                   'class': 'prompt srch_explore'
                   }
            ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'placeholder': 'Confirm Password', 
                   'class': 'prompt srch_explore'
                   }
            ))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LikeForm(forms.ModelForm):
    class Meta:
        model = Likes
        fields = ['post', 'user']