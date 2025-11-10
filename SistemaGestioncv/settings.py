import os
from os import environ, path
from pathlib import Path

from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-8en#l3nj+8+22lh0ag-&7vbx@-t4t&ciuz3v)0qf_bl&k42tfr'

DEBUG = False
ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh',
    'localhost',
    '127.0.0.1',
]


INSTALLED_APPS = [
    "unfold",

    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.location_field",
    "unfold.contrib.constance",
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "django.contrib.humanize",
    'corsheaders',
    'simple_history',
    'import_export',
    "crispy_forms",
    "gestor.apps.GestorConfig"
]
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "django.middleware.locale.LocaleMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "simple_history.middleware.HistoryRequestMiddleware",
    "SistemaGestioncv.middleware.ReadonlyExceptionHandlerMiddleware",

]

ROOT_URLCONF = 'SistemaGestioncv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SistemaGestioncv.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

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

LOGIN_URL = "admin:login"

LOGIN_REDIRECT_URL = reverse_lazy("admin:index")

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

UNFOLD = {

    "STUDIO": {

        "header_variant": "dark",
        "sidebar_style": "minimal",
        "sidebar_variant": "dark",

    },
    "SITE_TITLE": "Sistema de Gestión de Obras",
    "SITE_HEADER": "Gestión de Obras Civiles",
    "SITE_URL": "/",
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("Unfold theme repository"),
            "link": "https://github.com/unfoldadmin/django-unfold",
        },
        {
            "icon": "rocket_launch",
            "title": _("Turbo boilerplate repository"),
            "link": "https://github.com/unfoldadmin/turbo",
        },
        {
            "icon": "description",
            "title": _("Technical documentation"),
            "link": "https://unfoldadmin.com/docs/",
        },
    ],
    "SHOW_HISTORY": True,

    "BORDER_RADIUS": "12px",
    "STYLES": [
        lambda request: static("css/styles.css"),
    ],
    "DASHBOARD_CALLBACK": "gestor.views.dashboard_callback",

    # Colores del tema
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
        "base": {
            "50": "oklch(98.5% 0 0)",  # slate-50
            "100": "oklch(96.7% 0.001 286.375)",  # slate-100
            "200": "oklch(92% 0.004 286.32)",  # slate-200
            "300": "oklch(87.1% 0.006 286.286)",  # slate-300
            "400": "oklch(70.5% 0.015 286.067)",  # slate-400
            "500": "oklch(55.2% 0.016 285.938)",  # slate-500
            "600": "oklch(44.2% 0.017 285.786)",  # slate-600
            "700": "oklch(37% 0.013 285.805)",  # slate-700
            "800": "oklch(27.4% 0.006 286.033)",  # slate-800
            "900": "oklch(21% 0.006 285.885)",  # slate-900
            "950": "oklch(14.1% 0.005 285.823)",  # slate-950
        },
        "font": {
            "subtle-light": "var(--color-base-500)",  # text-base-500
            "subtle-dark": "var(--color-base-400)",  # text-base-400
            "default-light": "var(--color-base-600)",  # text-base-600
            "default-dark": "var(--color-base-300)",  # text-base-300
            "important-light": "var(--color-base-900)",  # text-base-900
            "important-dark": "var(--color-base-100)",  # text-base-100
        },
    },

    # Sidebar
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,

        "navigation": [
            {
                "title": _("Dashboard"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {
                        "title": _("Panel Principal"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "permission": lambda request: request.user.is_staff,
                    },

                ],
            },

            {
                "title": _("Proyectos"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Todos los Proyectos"),
                        "icon": "business",
                        "link": reverse_lazy("admin:gestor_proyecto_changelist"),
                    },
                    {
                        "title": _("Elementos Constructivos"),
                        "icon": "construction",
                        "link": reverse_lazy("admin:gestor_elementoconstructivo_changelist"),
                    },
                    {
                        "title": _("Puntos de Control"),
                        "icon": "place",
                        "link": reverse_lazy("admin:gestor_puntocontrol_changelist"),
                    },
                ],
            },
            {
                "title": _("Operaciones"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Cuadrillas"),
                        "icon": "groups",
                        "link": reverse_lazy("admin:gestor_cuadrilla_changelist"),
                    },
                    {
                        "title": _("Reportes de Avance"),
                        "icon": "timeline",
                        "link": reverse_lazy("admin:gestor_reporteavance_changelist"),
                    },
                    {
                        "title": _("Volúmenes"),
                        "icon": "analytics",
                        "link": reverse_lazy("admin:gestor_volumenterraceria_changelist"),
                    },
                ],
            },

            {
                "title": _("Configuración"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Usuarios"),
                        "icon": "person",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Grupos"),
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                        "permission": lambda request: request.user.is_superuser,
                    },
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": [
                "gestor.proyecto",
            ],
            "items": [
                {
                    "title": _("Todos los Proyectos"),
                    "link": reverse_lazy("admin:gestor_proyecto_changelist"),
                },
                {
                    "title": _("Arbol de proyectos"),
                    "link": reverse_lazy("admin:proyecto_explorer"),
                },
            ],
        },

    ],

}

CRISPY_TEMPLATE_PACK = "unfold_crispy"

CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
