'''Test-only settings.

https://docs.djangoproject.com/en/2.0/topics/testing/advanced/#using-the-django-test-runner-to-test-reusable-applications
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}
SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    "tests",
]