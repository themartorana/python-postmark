# Django settings for demo project.

import os
settings_path, settings_module = os.path.split(__file__)

import sys
sys.path.append('../../')
 
DEBUG = True
#TEMPLATE_DEBUG = DEBUG

#TIME_ZONE = 'America/Chicago'
#LANGUAGE_CODE = 'en-us'
#
#SECRET_KEY = '8(o*lht586wqr9hp5env&n!h!gu@t5g4*$$uupbyd*f+61!xjh'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'demo.urls'

TEMPLATE_DIRS = (
    os.path.join(settings_path, 'templates'),
)

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_BACKEND = 'postmark.django_backend.EmailBackend'
POSTMARK_API_KEY = 'POSTMARK_API_TEST'
POSTMARK_SENDER = 'system@playcompete.com'
