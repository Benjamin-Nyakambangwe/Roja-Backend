from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this BASE_DIR  'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-o5&@&gj(16x%)54lgfo9#%+aa)phv&7u9y9j(qdd@47ge^m0p3'

# SECURITY WARNING don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Create logs directory if not exists
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOGS_DIR, 'django.log'),
            'maxBytes': 52428800,  # 50MB
            'backupCount': 5,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'social_django',
    'corsheaders',
    'django_filters',
    'djoser',
    'accounts',
    'api',
    'channels',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Make sure this is correct
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# httpsdocs.djangoproject.comen5.0refsettings#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roja_db',
        'USER': 'postgres',
        'PASSWORD': '123456seven',
        'HOST': 'localhost'
    }
}


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'roja_db',
        'USER': 'ben',
        'PASSWORD': '123456seven',
        'HOST': 'localhost'
    }
}

# EMAIL GMAIL

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'benjaminnyakambangwe@gmail.com'
# EMAIL_HOST_PASSWORD = 'oqjezmvwhpizbpei'


# ZOHO Mail Settings
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.zoho.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'no-reply@ro-ja.com'
# EMAIL_HOST_PASSWORD = 'No-reply@roja1'

# # Required additional settings to prevent relay errors
# DEFAULT_FROM_EMAIL = 'no-reply@ro-ja.com'
# SERVER_EMAIL = 'no-reply@ro-ja.com'


# Email Settings NAMECHEAP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.privateemail.com'  # Namecheap's SMTP server
EMAIL_PORT = 587  # Use TLS
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'no-reply@ro-ja.com'  # Your full email address
EMAIL_HOST_PASSWORD = 'No-reply@roja1*'  # Your email password

# Optional: Set default "from" email address
DEFAULT_FROM_EMAIL = 'no-reply@ro-ja.com'


# AUTH
AUTH_USER_MODEL = 'accounts.UserAccount'

# For development only. Be more specific in production.
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'https://api.ro-ja.com',
    'https://beta.ro-ja.com',
    'https://ro-ja.com',
    'http://localhost:3000',
]

# Password validation
# httpsdocs.djangoproject.comen5.0refsettings#auth-password-validators

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
# httpsdocs.djangoproject.comen5.0topicsi18n

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# httpsdocs.djangoproject.comen5.0howtostatic-files

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DOMAIN = 'ro-ja.com'
# DOMAIN = 'localhost3000'

SITE_NAME = 'RO-JA ACCOMODATION'

# Default primary key field type
# httpsdocs.djangoproject.comen5.0refsettings#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


AUTHENTICATION_BACKENDS = [
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

# JWT
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES':    (
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
        'accounts.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES':    (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES':     ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}


# DJOSER
DJOSER = {
    'LOGIN_FIELD': 'email',
    'USER_CREATE_PASSWORD_RETYPE': True,
    'SEND_ACTIVATION_EMAIL': True,
    'SEND_CONFIRMATION_EMAIL': True,
    'SET_USERNAME_CHANGED_EMAIL_CONFIRMATION': True,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': True,
    'SET_PASSWORD_RETYPE': True,
    'SET_USERNAME_RETYPE': True,
    'PASSWORD_RESET_CONFIRM_URL': 'reset-password/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': 'email-reset/{uid}/{token}',
    'ACTIVATION_URL': 'activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': True,
    'SOCIAL_AUTH_ALLOWED_REDIRECT_URIS': ['httplocalhost3000authgoogle', 'httplocalhost3000authfacebook'],
    'SERIALIZERS': {
        'user_create': 'accounts.serializers.CustomUserSerializer',
        'user': 'accounts.serializers.CustomUserSerializer',
        'current_user': 'accounts.serializers.CustomUserSerializer',
        'user_delete': 'djoser.serializers.UserDeleteSerializer',
    },
    'EMAIL': {
        'activation': 'accounts.email.ActivationEmail',
        'confirmation': 'accounts.email.ConfirmationEmail',
        'password_reset': 'accounts.email.PasswordResetEmail',
        'password_changed_confirmation': 'accounts.email.PasswordChangedConfirmationEmail',
    },
    'TEMPLATES': {
        'activation': 'emailactivation.html',
        'confirmation': 'emailconfirmation.html',
        'password_reset': 'emailpassword_reset.html',
        'password_changed': 'emailpassword_changed.html',
    },
    'EMAIL_SUBJECT_PREFIX': '',
}

AUTH_COOKIE = 'access'
AUTH_COOKIE_ACCESS_MAX_AGE = 60 * 60 * 2  # 2 Hours
AUTH_COOKIE_REFRESH_MAX_AGE = 60 * 60 * 24 * 2  # 2 days
AUTH_COOKIE_SECURE = False
AUTH_COOKIE_HTTP_ONLY = True
AUTH_COOKIE_PATH = '/'
AUTH_COOKIE_SAMESITE = 'None'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '6824691756-2pv2q4ndt75vg5v3j59b7qototdv9khv.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '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'
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'httpswww.googleapis.comauthuserinfo.email',
    'httpswww.googleapis.comauthuserinfo.profile'
]
SOCIAL_AUTH_GOOGLE_OAUTH2_EXTRA_DATA = ['first_name', 'last_name']

SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'email,first_name,last_name'
}


# PAYNOW_INTEGRATION_ID = '19317'
# PAYNOW_INTEGRATION_KEY = '95a0ccfa-ed1a-4b46-aa63-33f4b04c0539'

PAYNOW_INTEGRATION_ID = os.getenv('PAYNOW_INTEGRATION_ID')
PAYNOW_INTEGRATION_KEY = os.getenv('PAYNOW_INTEGRATION_KEY')
PAYNOW_RESULT_URL = os.getenv('PAYNOW_RESULT_URL')
PAYNOW_RETURN_URL = os.getenv('PAYNOW_RETURN_URL')

# Add Channels configuration
ASGI_APPLICATION = 'core.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TWILIO_MESSAGING_SERVICE_SID = os.getenv('TWILIO_MESSAGING_SERVICE_SID')

SUPPORT_EMAIL = 'support@ro-ja.com'  # Update this with your actual support email
