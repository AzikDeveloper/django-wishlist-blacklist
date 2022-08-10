from django.contrib import admin

from .models import ModelBind


@admin.register(ModelBind)
class AdminModelBind(admin.ModelAdmin):
    list_display = ['author', 'target', 'type']
    list_filter = ['type']
    search_fields = ['author', 'target']

