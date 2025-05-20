"""
Django settings for speech_emotion_recognition project.
"""

import os
from pathlib import Path
from django.urls import reverse_lazy

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-key-for-development-only')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['0.0.0.0', 'localhost', '127.0.0.1', '.replit.dev', '.repl.co', '46b7beee-300e-4118-9b72-5c02355e0ae0-00-g7husjev3d93.worf.replit.dev']
#

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'social_django',
    'django.contrib.staticfiles',
    'emotion_recognition.apps.EmotionRecognitionConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'speech_emotion_recognition.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'speech_emotion_recognition.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # This creates the file in your project root
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files (Uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = reverse_lazy('emotion_recognition:login')
LOGIN_REDIRECT_URL = reverse_lazy('emotion_recognition:dashboard')
LOGOUT_REDIRECT_URL = reverse_lazy('emotion_recognition:login')

# Email settings for password reset
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Use your provider if not Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mahanteshchikkeri05@gmail.com'
EMAIL_HOST_PASSWORD = 'Mahantesh@1234'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Model directory
MODEL_DIR = os.path.join(BASE_DIR, 'model')

# ---
# IMPORTANT: To send email from Gmail, you MUST use an App Password, not your main password.
# 1. Go to https://myaccount.google.com/security > App Passwords.
# 2. Generate an app password for "Mail" and "Other (Custom name)" (e.g., Django).
# 3. Copy the 16-character app password (e.g., abcd efgh ijkl mnop).
# 4. In your PowerShell/terminal, set the environment variable before running Django:
#    $env:EMAIL_HOST_PASSWORD="abcd efgh ijkl mnop"
# 5. Then run:
#    python manage.py runserver
#
# If you do not set the environment variable, EMAIL_HOST_PASSWORD will be blank and email will NOT send.
# ---
