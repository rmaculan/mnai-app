from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# llm access
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY') 
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = []

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'emails')

from datetime import timedelta

# Authentication settings
AUTH_USER_MODEL = 'blog.User'

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
}

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

# Application definition
INSTALLED_APPS = [
    'search',
    'subs',
    'daphne',
    'channels',
    "django.contrib.humanize",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    'api.apps.ApiConfig',

    # my apps
    'chat',
    'notification',
    'chatbot',
    'polls',
    'blog',
    'marketplace',

    # third party apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.csrf',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'notification.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # Correct way to join paths
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

AUTH_USER_MODEL = 'auth.User'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

### change for production ###
# CORS_ALLOWED_ORIGINS = []: when you want to allow specific origins

CORS_ALLOW_ALL_ORIGINS = True

CSRF_COOKIE_SECURE = True  # If using HTTPS

# local host for now
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000/'] 

# Stripe Configuration (Payment System)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID', 'price_XXXX')  # Monthly subscription
PAY_AS_YOU_GO_RATE = 0.10  # USD per message
STRIPE_CURRENCY = 'usd'
FREE_TRIAL_DAYS = 7

# Blockchain payment configuration (temporarily disabled)
BLOCKCHAIN_ENABLED = False  # Feature flag to toggle blockchain payments
BLOCKCHAIN_NETWORK = os.environ.get('BLOCKCHAIN_NETWORK', 'ethereum')
WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI', 'https://mainnet.infura.io/v3/YOUR-PROJECT-ID')
PAYMENT_CONTRACT_ADDRESS = os.environ.get('PAYMENT_CONTRACT_ADDRESS', '0x...')
PAYMENT_CONTRACT_ABI = os.environ.get('PAYMENT_CONTRACT_ABI', '[]')
PAYMENT_WALLET_ADDRESS = os.environ.get('PAYMENT_WALLET_ADDRESS', '0x...')
PAYMENT_WALLET_PRIVATE_KEY = os.environ.get('PAYMENT_WALLET_PRIVATE_KEY', '')

# Validate required payment settings only when enabled
if BLOCKCHAIN_ENABLED and not PAYMENT_WALLET_PRIVATE_KEY:
    raise ValueError("Blockchain payments require PAYMENT_WALLET_PRIVATE_KEY when enabled")

# # Blockchain Payments (Ethereum Mainnet)
# BLOCKCHAIN_ENABLED = os.environ.get('BLOCKCHAIN_ENABLED', 'False') == 'True'
# WEB3_PROVIDER_URI = os.environ.get('WEB3_PROVIDER_URI', 'https://mainnet.infura.io/v3/YOUR-ID')
# PAYMENT_CONTRACT_ADDRESS = os.environ.get('PAYMENT_CONTRACT_ADDRESS', '0x...')

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# from decouple import config
