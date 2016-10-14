# Django settings for frontend project.

import os
import common
from autotest_lib.client.common_lib import global_config

DEBUG = True
TEMPLATE_DEBUG = DEBUG

FULL_ADMIN = False

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'      # 'postgresql_psycopg2', 'postgresql',
                               # 'mysql', 'sqlite3' or 'ado_mssql'.
DATABASE_PORT = ''             # Set to empty string for default.
                               # Not used with sqlite3.

c = global_config.global_config
_section = 'AUTOTEST_WEB'
DATABASE_HOST = c.get_config_value(_section, "host")
# Or path to database file if using sqlite3.
DATABASE_NAME = c.get_config_value(_section, "database")
# The following not used with sqlite3.
DATABASE_USER = c.get_config_value(_section, "user")
DATABASE_PASSWORD = c.get_config_value(_section, "password", default='')

DATABASE_READONLY_HOST = c.get_config_value(_section, "readonly_host",
                                            default=DATABASE_HOST)
DATABASE_READONLY_USER = c.get_config_value(_section, "readonly_user",
                                            default=DATABASE_USER)
if DATABASE_READONLY_USER != DATABASE_USER:
    DATABASE_READONLY_PASSWORD = c.get_config_value(_section,
                                                    "readonly_password",
                                                    default='')
else:
    DATABASE_READONLY_PASSWORD = DATABASE_PASSWORD

# prefix applied to all URLs - useful if requests are coming through apache,
# and you need this app to coexist with others
URL_PREFIX = 'afe/server/'
TKO_URL_PREFIX = 'new_tko/server/'
PLANNER_URL_PREFIX = 'planner/server/'

# Local time zone for this installation. Choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# although not all variations may be possible on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Los_Angeles'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'pn-t15u(epetamdflb%dqaaxw+5u&2#0u-jah70w1l*_9*)=n7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'frontend.apache_auth.ApacheAuthMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'frontend.shared.json_html_formatter.JsonToHtmlMiddleware',
)

ROOT_URLCONF = 'frontend.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.

    os.path.abspath(os.path.dirname(__file__) + '/templates')
)

INSTALLED_APPS = (
    'frontend.afe',
    'frontend.tko',
    'frontend.planner',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
)

AUTHENTICATION_BACKENDS = (
    'frontend.apache_auth.SimpleAuthBackend',
)
