"""
Django settings for bus_tracker project.
"""

from pathlib import Path
from datetime import timedelta
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================
# SECURITY
# =====================================================

SECRET_KEY = 'django-insecure-2=vmeox2m%+noodja(ga0p(=br3!n_4-&%=m%5=+@11(2g1^%z'

DEBUG = FALSE

ALLOWED_HOSTS = ['*']


# =====================================================
# APPLICATIONS
# =====================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',

    # Your app
    'core',
]

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-2=vmeox2m%+noodja(ga0p(=br3!n_4-&%=m%5=+@11(2g1^%z'
# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# =====================================================
# URL & TEMPLATES
# =====================================================

ROOT_URLCONF = 'bus_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bus_tracker.wsgi.application'
ASGI_APPLICATION = 'bus_tracker.asgi.application'


# =====================================================
# DATABASE
# =====================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# =====================================================
# AUTH
# =====================================================

AUTH_USER_MODEL = 'core.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =====================================================
# INTERNATIONALIZATION
# =====================================================

LANGUAGE_CODE = 'en-us'

# ✅ Indian Standard Time
TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True
USE_TZ = True


# =====================================================
# STATIC FILES
# =====================================================

STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# =====================================================
# REST FRAMEWORK
# =====================================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}


# =====================================================
# SIMPLE JWT SETTINGS
# =====================================================

SIMPLE_JWT = {
    # ✅ Admin stays logged in 6 hours
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),

    # Refresh token valid for 1 day
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),

    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}


# =====================================================
# CHANNELS (WebSocket Support)
# =====================================================

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    }
}
