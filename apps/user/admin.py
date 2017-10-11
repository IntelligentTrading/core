from django.contrib import admin
from apps.user import models

class BaseAdmin(admin.ModelAdmin):
  exclude = ('created_at', 'modified_at',)


admin.site.register(models.User)
