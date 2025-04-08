from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.search_icon_view, name='search_icon'),
    path('results/', views.search_view, name='search_view'),
    path('reindex/', views.reindex_search, name='reindex_search'),
]
