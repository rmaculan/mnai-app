# url for the subs app

from django.urls import path

from . import views

app_name = 'subs'

urlpatterns = [
    path('index/', views.subscribe, name='index'),
]