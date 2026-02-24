#The Default Django apps that make auth work
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    #Django REST API 
    "rest_framework",

    #Our App
    "auth_api",
]