"""
URL configuration for speech_emotion_recognition project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('', include('emotion_recognition.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve media files during development

