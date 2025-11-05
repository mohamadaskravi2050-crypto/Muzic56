from django.contrib import admin
from .models import CustomUser, Music

admin.site.register(CustomUser)
admin.site.register(Music)
