from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.read_blog_posts, name='index'),
    path('follow/<str:username>', views.follow_user, name='follow'),
    path('unfollow/<str:username>', views.unfollow_user, name='unfollow'),
    path('following/', views.view_following, name='following'),
    path('followers/', views.view_followers, name='followers'),
    path('tag/<slug:tag_slug>', views.tags, name='tags'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('profile/<str:username>', views.profile_view, name='profile'),
    path('edit_profile/edit', views.edit_profile, name='edit_profile'),
    path('delete_profile/<str:username>', views.delete_profile, name='delete_profile'),
    path('my_posts/', views.read_my_posts, name='my_posts'),
    path('<uuid:post_id>/', views.read_blog_post, name='post_detail'),
    path('create_blog_post/', views.create_blog_post, name='create_blog_post'),
    path('delete/<uuid:post_id>/', views.delete_blog_post, name='delete_blog_post'),
    path('<uuid:post_id>/like/', views.like_post, name='like_post'),
    path('<uuid:post_id>/dislike/', views.dislike_post, name='dislike_post'),
    path('<uuid:post_id>/comment/', views.create_comment, name='create_comment'),
    path('<uuid:post_id>/comments/', views.read_comments, name='read_comments'),
    path('<uuid:post_id>/<int:comment_id>/edit/', views.update_comment, name='update_comment'),
    path('<uuid:post_id>/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Blog Messages
    path('messages/', views.blog_messages, name='messages'),
    path('contact_author/<uuid:post_id>/', views.contact_author_form, name='contact_author_form'),
    path('delete_conversation/<int:message_id>/', views.delete_blog_conversation, name='delete_conversation'),
]
