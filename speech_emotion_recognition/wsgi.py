"""
WSGI config for speech_emotion_recognition project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech_emotion_recognition.settings')

application = get_wsgi_application()
