"""
For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
from pathlib import Path
from typing import Callable, Optional, TypeVar

# === UTILITIES ===
T = TypeVar("T")
is_prod = "PROD" in os.environ


def env(key: str, default: Optional[T] = None) -> T:
    """
    Get an environment variable and optionally cast it.

    Args:
        key: Name of the environment variable.
        default: Default value if the environment variable is not set. If None, an error will be raised.

    Returns:
        The environment value, cast if specified, or None if not set.
    """
    value = os.environ.get(key)

    # handle a missing env variable
    if value is None:
        if default is None:
            raise ValueError(f"The environment variable `{key}` was not set, but is required.")
        value = default

    return value


# === PATHS ===
BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"

# === CONFIGURATION ===

SECRET_KEY = env("SECRET_KEY")
DEBUG = not is_prod
CSRF_COOKIE_SECURE = is_prod
SECURE_SSL_REDIRECT = is_prod
SESSION_COOKIE_SECURE = is_prod

LOGIN_URL = "/login"
SELECT2_THEME = "bootstrap-5"

ALLOWED_HOSTS = [env("DOMAIN", "2975645s.eu.pythonanywhere.com"), "127.0.0.1", "localhost"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_bootstrap5',
    'django_select2',
    'setsearch'
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

ROOT_URLCONF = 'wad.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'wad.wsgi.application'

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [ASSETS_DIR]
