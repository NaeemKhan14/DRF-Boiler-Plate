from django.contrib import admin
from .models import UserAccount

# Register our custom user account model to appear in django's admin panel
admin.site.register(UserAccount)
