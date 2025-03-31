from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import landing_page
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    
    path("", landing_page, name="landing_page"),
    path("admin/", admin.site.urls),
    path('chat/', include('chat.urls'), name='chat'),
    path("api/", include("api.urls")),
    path('chatbot/', include('chatbot.urls')),
    path('polls/', include('polls.urls', namespace='polls')),
    path('notifications/', include('notification.urls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('accounts/', include('django.contrib.auth.urls'), name='accounts'),

    # region: add later
    # path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path("comments/", include("comments.urls")),
    # endregion
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
