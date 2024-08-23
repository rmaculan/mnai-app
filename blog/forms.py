from django import forms
from .models import Post, Comment, Likes, Follow

class PostForm(forms.ModelForm):
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