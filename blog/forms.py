from django import forms
from .models import Profile, Post, Comment, Likes, Follow

class ProfileForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Last Name'}))
    bio = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Bio'}))
    url = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'URL'}), required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Address'}), required=False)

    class Meta:
        model = Profile
        fields = ['image', 'first_name', 'last_name', 'bio', 'url', 'location']

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Title'}), required=True)
    subtitle = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Subtitle'}), required=True)
    job_title = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Job Title'}), required=True)
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'input', 'placeholder': 'Content'}), required=True)
    picture = forms.ImageField(required=True)
    caption = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Caption'}), required=True)
    
    class Meta:
        model = Post
        fields = ['title', 'subtitle', 'job_title','content', 'picture', 'caption']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class LikeForm(forms.ModelForm):
    class Meta:
        model = Likes
        fields = ['post', 'user']
