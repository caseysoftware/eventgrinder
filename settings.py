# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Django settings for google-app-engine-django project.

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Library'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'Apps'))


DEBUG = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')
TEMPLATE_DEBUG = DEBUG


ADMINS = (
     ('Ross Karchner', 'rosskarchner@gmail.com'),
)

MANAGERS = ADMINS

APPEND_SLASH=True

TIME_ZONE = 'UTC'

DATE_FORMAT='l, F j, Y'
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'hvhxfm5u=^*v&doo#oq8x*eg8+1&9sxbye@=umutgn^t_sg_nx'

# Ensure that email is not sent via SMTP by default to match the standard App
# Engine SDK behaviour. If you want to sent email via SMTP then add the name of
# your mailserver here.
EMAIL_HOST = ''
#CACHE_BACKEND = 'backend_cache://'
# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
MIDDLEWARE_CLASSES = (
#'django.middleware.cache.UpdateCacheMiddleware',
    #'google.appengine.ext.appstats.recording.AppStatsDjangoMiddleware'
    'django.middleware.common.CommonMiddleware',
    #'django.contrib.csrf.middleware.CsrfMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.middleware.doc.XViewMiddleware',
#'django.middleware.cache.FetchFromCacheMiddleware',
)
CACHE_BACKEND = 'egcache://'
TEMPLATE_CONTEXT_PROCESSORS = (
#   'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.contrib.messages.context_processors.messages',
#    'django.core.context_processors.media',  # 0.97 only.
#    'django.core.context_processors.request',
    'eventsite.context.site_context',
#    'account.context.account_context',
    #'messaging.messaging_context'
)

ROOT_URLCONF = 'django_urls'

ROOT_PATH = os.path.dirname(__file__)


TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates')
)


INSTALLED_APPS = (
		 'account',
		 'eventsite',
	     'events',
	     'sources',
	     'assets',
	     'django.contrib.formtools',
	     'django.contrib.messages',
	     
#    'django.contrib.auth',
#    'django.contrib.contenttypes',
#    'django.contrib.sessions',
#    'django.contrib.sites',
)
