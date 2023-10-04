import sys
import os
from dotenv import load_dotenv
# Django settings for daa project.

load_dotenv()
### This should probably be as environment variables?
# django-libage settings
# The URL of the api
LIBAGE_ENDPOINT = 'http://la.ageing-map.org/api'
# The URL of the site
LIBAGE_URL = 'http://la.ageing-map.org'
# The database short name to get the references for
LIBAGE_DATABASE = 'daa'
###

ABSOLUTE_PATH = '/srv/www/beta.ageing-map.org/daa'
sys.path.append(ABSOLUTE_PATH + '/lib')

ALLOWED_HOSTS = ['localhost', '.ageing-map.org']

DEBUG = True

TEMPLATE_DEBUG = True

# ADMINS = (
#    ('Daniel Thornton', 'daniel.thornton@liverpool.ac.uk'),
# )

# MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'beta_daa',
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': os.environ.get("POSTGRES_HOST"), #CHANGED FOR TESTING
        'PORT': '5432',
    },
    'libage': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'la',
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': os.environ.get("POSTGRES_HOST"),
        'PORT': '5432',
    },
    'ortholog': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_orthologs',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'genage_human': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_genage_human',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'genage_model': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_genage_models',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'anage': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_anage',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'gendr': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_gendr',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'longevity': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_longevity',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'drugage': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_drug_age',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    },
    'cellage': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dev_cell_age',
        'USER': os.environ.get("MYSQL_USER"),
        'PASSWORD': os.environ.get("MYSQL_PASSWORD"),
        'HOST': os.environ.get("MYSQL_HOST"),
        'PORT': '3306',
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ABSOLUTE_PATH + '/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ABSOLUTE_PATH + '/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ABSOLUTE_PATH + '/resources',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY")

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            ABSOLUTE_PATH + '/templates/',
            ABSOLUTE_PATH + '/atlas/templates/atlas/',
            ABSOLUTE_PATH + '/tools/templates/tools/',
            ABSOLUTE_PATH + '/go_db/templates/go_db/',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'daa.version.context_processors.version',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
]

ROOT_URLCONF = 'daa.urls'

INSTALLED_APPS = (
    'suit',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django_tables2',
    'django_filters',
    'markdown_deux',
    'django_markwhat',
    'mptt',
    'reversion',
    'debug_toolbar',
    'daa.atlas',
    'daa.genage_human',
    'daa.genage_model',
    'daa.anage',
    'daa.gendr',
    'daa.go_db',
    'daa.ortholog',
    'daa.django_libage',
    'daa.log_admin',
    'daa.drugage',
    'daa.cellage',
    'daa.longevity',
    'daa.submissions',
    'django.contrib.admindocs',
)

DATABASE_ROUTERS = ['daa.genage_human.router.GenageRouter', 'daa.genage_model.router.GenageRouter',
                    'daa.anage.router.AnageRouter', 'daa.gendr.router.GendrRouter',
                    'daa.django_libage.router.LibageRouter', 'daa.longevity.router.LongevityRouter',
                    'daa.ortholog.router.OrthologRouter', 'daa.drugage.router.DrugAgeRouter',
                    'daa.cellage.router.CellAgeRouter']  # , 'daa.go_db.router.GORouter']

SUIT_CONFIG = {
    'ADMIN_NAME': 'HAGR Curator',
    'LIST_PER_PAGE': 50,
    'MENU': (
        {'app': 'atlas', 'label': 'The Digital Ageing Atlas', 'models': (
            {'model': 'atlas.change', 'label': 'Changes'},
            {'model': 'atlas.relationship', 'label': 'Relationships'},
            {'model': 'atlas.gene', 'label': 'Genes'},
            {'model': 'atlas.tissue', 'label': 'Tissues'},
            {'url': 'admin:atlas_check', 'label': u'\u2611 Check changes for issues'},
            {'url': 'admin:atlas_check_references', 'label': u'\u2611 Check changes for referencing issues'},
            {'url': 'admin:atlas_check_genage', 'label': u'\u2611 Check and indicate genes in both GenAge and the DAA'},
            {'url': 'admin:atlas_import_changes', 'label': u'\u21F2 Import changes from CSV'},
        )},
        {'app': 'genage_human', 'label': 'GenAge', 'models': (
            {'model': 'genage_human.name', 'label': 'Human Ageing Genes'},
            {'model': 'genage_model.model', 'label': 'Model Organism Ageing Genes'},
            {'url': 'admin:genage_model_checks', 'label': u'\u2611 Check model organisms for issues'},
            {'url': 'admin:genage_csvimport', 'label': u'\u21f2 Import model organisms'},
            {'url': 'admin:genage_csvupdate', 'label': u'\u21f2 Update longevity entries in model organisms'},
            {'url': 'admin:genage_human_export', 'label': u'\u21f1 Export GenAge human entries'},
            {'url': 'admin:genage_models_export', 'label': u'\u21f1 Export GenAge model entries'},
        )},
        {'app': 'anage', 'label': 'AnAge', 'models': (
            {'model': 'anage.anagename', 'label': 'Species Longevity Entries'},
            {'model': 'anage.anagebiblio', 'label': 'Bibliographic References'},
        )},
        {'app': 'gendr', 'label': 'GenDR', 'models': (
            {'model': 'gendr.gene', 'label': 'Gene Manipulations'},
            {'model': 'gendr.expression', 'label': 'Gene Expressions'},
            {'url': 'admin:gene_manip_check', 'label': u'\u2611 Check gene manipulations for issues'},
            {'url': 'admin:gendr_manip_export', 'label': u'\u21f1 Export GenDR manipulations entries'},
            {'url': 'admin:gendr_exp_export', 'label': u'\u21f1 Export GenDR expression entries'},
        )},
        {'app': 'longevity', 'label': 'LongevityMap', 'models': (
            {'model': 'longevity.variant', 'label': 'Longevity Variant'},
            {'model': 'longevity.variantgroup', 'label': 'Longevity Variant Group'},
            {'model': 'longevity.gene', 'label': 'Genes'},
            {'model': 'longevity.population', 'label': 'Populations'},
            {'url': 'admin:longevity_csvimport', 'label': u'\u21f2 Import longevity entries'},
            {'url': 'admin:longevity_csvexport', 'label': u'\u21f1 Expport longevity entries'},
            {'url': 'admin:longevity_clearlibage', 'label': u'Delete citations from LibAge'},
        )},
        {'app': 'django_libage', 'label': 'LibAge', 'models': (
            {'model': 'django_libage.bibliographicentry', 'label': 'Bibliographic Entries'},
            {'model': 'django_libage.citation', 'label': 'Citations'},
            {'model': 'django_libage.source', 'label': 'Sources'},
        )},
        {'app': 'drugage', 'label': 'DrugAge', 'models': (
            {'model': 'drugage.drugagebiblio', 'label': 'Bibliographic Entries'},
            {'model': 'drugage.drugageresults', 'label': 'DrugAge Results'},
            {'model': 'drugage.drugagecompounds', 'label': 'DrugAge Compounds'},
            {'model': 'drugage.drugagecompoundsynonyms', 'label': 'DrugAge Compound Synonyms'},
            {'url': 'admin:drugage_csvimport', 'label': u'\u21f2 Import DrugAge'},
            {'url': 'admin:drugage_csvexport', 'label': u'\u21f1 Export DrugAge'},
        )},
        {'app': 'cellage', 'label': 'CellAge', 'models': (
            {'model': 'cellage.cellagebiblio', 'label': 'Bibliographic Entries'},
            {'model': 'cellage.cellagegeneinterventions', 'label': 'Gene Interventions'},
            {'model': 'cellage.cellagemethod', 'label': 'Methods'},
            {'model': 'cellage.cellagecell', 'label': 'Cells'},
            {'model': 'cellage.cellagecellline', 'label': 'Cell Lines'},
            {'model': 'cellage.cellagesenescence', 'label': 'Senescence Types'},
            {'model': 'cellage.cellagegene', 'label': 'Genes'},
            {'url': 'admin:cellage_csvimport', 'label': u'\u21f2 Import Interventions'},
            {'url': 'admin:cellage_csvexport', 'label': u'\u21f1 Export Interventions'},
            {'url': 'admin:cellage_clearlibage', 'label': u'Delete citations from LibAge'},
        )},
        '-',
        {'label': 'Submissions', 'icon': 'icon-inbox', 'models': ('submissions.submission',)},
        '-',
        {'label': 'Admin', 'icon': 'icon-cog', 'models': ('auth.user', 'auth.group', 'admin.logentry')},
    ),
}

INTERNAL_IPS = ('127.0.0.1',)
