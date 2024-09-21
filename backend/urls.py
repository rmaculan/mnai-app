from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from .views import landing_page

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", landing_page, name="landing_page"),
    path('chat/', include('chat.urls', namespace='chat')),
    path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    path('polls/', include('polls.urls', namespace='polls')),
    path('notifications/', include('notification.urls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('accounts/', include('django.contrib.auth.urls'), name='accounts'),

    # # add later
    # path("comments/", include("comments.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
