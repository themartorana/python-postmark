# Django settings for demo project.

import os
settings_path, settings_module = os.path.split(__file__)

import sys
sys.path.append('../../')
 
DEBUG = True
#TEMPLATE_DEBUG = DEBUG

USE_TZ=True

#TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'

SECRET_KEY = '8(o*lht586wqr9hp5env&n!h!gu@t5g4*$$uupbyd*f+61!xjh'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
 )

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(settings_path, 'templates'),
)

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'

#Supply your own API KEY
POSTMARK_API_KEY = ''
assert len(POSTMARK_API_KEY) != 0

#Use the sender set up in your postmark account
POSTMARK_SENDER = ''
assert len(POSTMARK_SENDER) != 0

