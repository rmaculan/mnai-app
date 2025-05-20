from django import forms
from .models import Profile, Post, Comment, Like, Follow
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
        fields = [
            'username', 
            'email', 
            'password1', 
            'password2'
            ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.save()
        Profile.objects.create(user=user)
        return user
    
class ProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input', 
                'placeholder': 'First Name'
                }
            ))
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input', 
                'placeholder': 'Last Name'
                }
            ))
    bio = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input', 
                'placeholder': 'Bio'
                }
            ))
    url = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input',                   
                'placeholder': 'URL'
                }), 
        required=False
        )
    location = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'input',              
                'placeholder': 'Address'
                }), 
        required=False
        )

    class Meta:
        model = Profile
        fields = [
            'image', 
            'first_name', 
            'last_name', 
            'bio', 
            'url', 
            'location'
            ]

class PostForm(forms.ModelForm):

    # region: post form regions
    # title = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'input', 
    #             'placeholder': 'Title'
    #             }), 
    #     required=True
    #     )
    # subtitle = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'input', 
    #             'placeholder': 'Subtitle'
    #             }), 
    #     required=True
    #     )
    # job_title = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'input', 
    #             'placeholder': 'Job Title'
    #             }), 
    #     required=True
    #     )
    # content = forms.CharField(
    #     widget=forms.Textarea(attrs={
    #         'class': 'input', 
    #         'placeholder': 'Content'
    #             }), 
    #     required=True
    #     )
    # picture = forms.ImageField(required=True)
    # caption = forms.CharField(
    #     widget=forms.TextInput(
    #         attrs={
    #             'class': 'input', 
    #             'placeholder': 'Caption'
    #             }), 
    #     required=True
    #     )
    # endregion
    
    class Meta:
        model = Post
        fields = [
            'title', 
            'subtitle', 
            'job_title',
            'content', 
            'picture', 
            'caption'
            ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class LikeForm(forms.ModelForm):
    class Meta:
        model = Like
        fields = ['post', 'user']
