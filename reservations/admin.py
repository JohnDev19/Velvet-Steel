from django.contrib import admin
# MongoEngine Documents cannot be registered with Django admin.
# User management is handled via Django's built-in auth at /django-admin/