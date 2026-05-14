"""
Django settings for Open Banking Marketplace Application.

Design and Implementation of an Open-Banking Marketplace for Loan Transactions
by ILOEGBUNAM VALERIAN CHIMDINDU
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-openbanking-marketplace-2024-secure-key-veritas-university')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third-party apps
    'widget_tweaks',
    
    # Project apps
    'apps.accounts',
    'apps.loans',
    'apps.marketplace',
    'apps.banking',
    'apps.notifications',
    'apps.analytics',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.accounts.middleware.UserActivityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'openbanking_marketplace.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.notifications.context_processors.notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'openbanking_marketplace.wsgi.application'
ASGI_APPLICATION = 'openbanking_marketplace.asgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'openbanking_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Fallback to SQLite for development
if os.environ.get('USE_SQLITE', 'True').lower() == 'true':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Cache configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Use database cache as fallback for development
if os.environ.get('USE_SQLITE', 'True').lower() == 'true':
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'django_cache',
        }
    }

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 1800  # 30 minutes
SESSION_SAVE_EVERY_REQUEST = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# Authentication
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'marketplace:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'openbanking.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Create logs directory
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Open Banking API Configuration (Mock settings for development)
OPEN_BANKING_CONFIG = {
    'API_VERSION': 'v3.1',
    'MAX_REQUESTS_PER_MINUTE': 100,
    'TOKEN_EXPIRY_MINUTES': 60,
    'SUPPORTED_BANKS': [
        {'id': 'first_bank', 'name': 'First Bank of Nigeria', 'logo': 'first_bank.png'},
        {'id': 'gtbank', 'name': 'Guaranty Trust Bank', 'logo': 'gtbank.png'},
        {'id': 'zenith', 'name': 'Zenith Bank', 'logo': 'zenith.png'},
        {'id': 'uba', 'name': 'United Bank for Africa', 'logo': 'uba.png'},
        {'id': 'access', 'name': 'Access Bank', 'logo': 'access.png'},
        {'id': 'ecobank', 'name': 'Ecobank Nigeria', 'logo': 'ecobank.png'},
    ],
}

# Credit Scoring Configuration
CREDIT_SCORING_CONFIG = {
    'MIN_SCORE': 300,
    'MAX_SCORE': 850,
    'RISK_CATEGORIES': {
        'excellent': {'min': 750, 'max': 850, 'label': 'Excellent', 'color': '#27ae60'},
        'good': {'min': 670, 'max': 749, 'label': 'Good', 'color': '#2980b9'},
        'fair': {'min': 580, 'max': 669, 'label': 'Fair', 'color': '#f39c12'},
        'poor': {'min': 300, 'max': 579, 'label': 'Poor', 'color': '#e74c3c'},
    },
    'WEIGHTS': {
        'payment_history': 0.35,
        'credit_utilization': 0.30,
        'credit_history_length': 0.15,
        'credit_mix': 0.10,
        'new_credit': 0.10,
    }
}

# Loan Configuration
LOAN_CONFIG = {
    'MIN_AMOUNT': 5000,
    'MAX_AMOUNT': 5000000,
    'MIN_DURATION_MONTHS': 1,
    'MAX_DURATION_MONTHS': 60,
    'INTEREST_RATE_RANGE': {
        'min': 5.0,
        'max': 35.0,
    },
    'PROCESSING_FEE_PERCENT': 1.0,
    'LATE_PAYMENT_PENALTY': 5.0,
}

# Notification Settings
NOTIFICATION_CONFIG = {
    'EMAIL_ENABLED': True,
    'SMS_ENABLED': False,
    'PUSH_ENABLED': True,
    'NOTIFICATION_RETENTION_DAYS': 90,
}

# Email configuration (for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@openbanking-marketplace.com'

# API Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# Data retention
DATA_RETENTION_DAYS = 2555  # 7 years for financial records
