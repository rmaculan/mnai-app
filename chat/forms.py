from django import forms
from .models import Room
from blog.models import Likes
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Username', 
                'class': 'prompt srch_explore'
                }), 
            max_length=50, 
            required=True
            )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Email', 
                'class': 'prompt srch_explore'
                }
            ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter Password', 
                'class': 'prompt srch_explore'
                }
            ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm Password', 
                'class': 'prompt srch_explore'
                }
            ))
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password1', 
            'password2'
            ]
class RoomCreationForm(forms.ModelForm):
    room_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Room Name',
                'class': 'prompt srch_explore'
                }
            ))
    
    class Meta:
        model = Room
        fields = ['room_name']

    def __init__(self, *args, **kwargs):
        self.creator = kwargs.pop('creator', None)
        super(RoomCreationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(RoomCreationForm, self).save(commit=False)
        instance.creator = self.creator
        if commit:
            instance.save()
        return instance

class LikeForm(forms.ModelForm):
    class Meta:
        model = Likes
        fields = ['post', 'user']