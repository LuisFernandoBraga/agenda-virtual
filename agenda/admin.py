from django.contrib import admin
from agenda import models

@admin.register(models.Agenda)
class AgendaAdmin(admin.ModelAdmin):
    ...

