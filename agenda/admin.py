from django.contrib import admin
from agenda import models

@admin.register(models.Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = 'id', 'nome', 'sobrenome', 'cpf', 'email', 'contato', 'descricao_servico', 'data_hora', 'valor',
    ordering = 'data_hora',
    list_filter = 'data_hora',
    search_fields = 'nome', 'sobrenome',
    list_per_page = 10  
    list_max_show_all = 1000
    list_display_links = 'nome',

@admin.register(models.Genero)
class SexoAdmin(admin.ModelAdmin):
    list_display = 'nome',

@admin.register(models.Faixa_Etaria)
class Faixa_EtariaAdmin(admin.ModelAdmin):
    list_display = 'nome',

@admin.register(models.Proprietario)
class ProprietarioAdmin(admin.ModelAdmin):
    list_display = 'nome',
