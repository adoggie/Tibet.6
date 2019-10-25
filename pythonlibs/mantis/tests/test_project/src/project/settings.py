#-- coding:utf-8 --
# Django settings for showbox project.
import os

DEBUG = False
DEBUG = True
TEMPLATE_DEBUG = DEBUG

SESSION_COOKIE_AGE = 60*30*30
# SESSION_COOKIE_AGE = 30
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

ALLOWED_HOSTS = ['*']



ADMINS = (
	# ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
	'default': {
		#'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		# 'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		# 'ENGINE': 'django_db_geventpool.backends.postgresql_psycopg2',
		# gevent-pool supported or no-pool

		'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		# 'NAME': 'cloudfish',                      # Or path to database file if using sqlite3.
		'NAME': os.path.dirname(os.path.abspath(__file__))+'/../test.db',
		# 'USER': 'postgres',                      # Not used with sqlite3.
		# 'PASSWORD': '111111',                  # Not used with sqlite3.
		# 'HOST': '172.16.10.64',                      # Set to empty string for localhost. Not used with sqlite3.
		# 'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
		# 'PORT': '5432',                      # Set to empty string for default. Not used with sqlite3.

		# pgsql-db-gevent-pool supported as following
		# 'ATOMIC_REQUESTS': False,
		# 'CONN_MAX_AGE':0,
		# 'OPTIONS':{
		# 	'MAX_CONNS':50
		# }
		# end pgdql-db-gevent-pool
	}
}

#TIME_ZONE = 'America/Chicago'
TIME_ZONE = 'Asia/Shanghai'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
#USE_TZ = True
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
STATIC_ROOT =os.path.dirname(os.path.abspath(__file__))+'/../../../src/web/'
# STATIC_ROOT ='/mnt/web'
# STATIC_ROOT =os.path.dirname(os.path.abspath(__file__))+'/../../../test/file/'

# Additional locations of static files
STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'w%aokr#a!bx4rlx%xem#x)e9vvxs%o=%b_(@_6isqof17gq@k^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (

	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	# 'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.transaction.TransactionMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',

	#'service.middleware.cors.CorsHandler',
	# 'service.middleware.auth.SessionMiddleware',
	# 'corsheaders.middleware.CorsMiddleware',



)



CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_METHODS = (
	'GET',
	'POST',
	'PUT',
	'PATCH',
	'DELETE',
	'OPTIONS'
)
CORS_ALLOW_CREDENTIALS = False
CORS_ALLOW_HEADERS = (
	'x-requested-with',
	'content-type',
	'accept',
	'origin',
	'authorization',
	'x-csrftoken',
	'if-version',
	'session-token',
	'token'
)

# APPEND_SLASH=False

ROOT_URLCONF = 'service.urls'
# ROOT_URLCONF = 'database.showbox.showbox.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'model.django.project.wsgi.application'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	STATIC_ROOT,
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'project.rhino',
	# 'rest_framework',
	# 'nosql'
	# Uncomment the next line to enable the admin:
	# 'django.contrib.admin',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		},
		'console':{
			'level':'DEBUG',
			'class':'logging.StreamHandler',
		},
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
		# 'django.db.backends': {
		# 	'handlers': ['console'],
		# 	'propagate': True,
		# 	'level':'DEBUG',
		# },
	}
}



REST_FRAMEWORK = {
	'DEFAULT_RENDERER_CLASSES': (
		'rest_framework.renderers.JSONRenderer',
		'rest_framework.renderers.BrowsableAPIRenderer',
	)
}