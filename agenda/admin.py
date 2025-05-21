from django.contrib import admin
from agenda.models import Agenda, Genero, Faixa_Etaria
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError
import logging
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

logger = logging.getLogger(__name__)

class AgendaAdminForm(forms.ModelForm):
    """Custom form for Agenda admin that uses direct SQLite Cloud queries for foreign keys."""
    
    class Meta:
        model = Agenda
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # If using SQLite Cloud in Vercel, replace the ModelChoiceField for foreign keys
        if settings.IS_VERCEL and settings.SQLITECLOUD_ENABLED:
            logger.info("Using CloudModelChoiceField for AgendaAdminForm")
            
            try:
                # Import here to avoid circular imports
                from agenda.cloud_forms import CloudModelChoiceField
                
                # Replace the genero field
                choices = self._get_choices_from_sqlitecloud('agenda_genero')
                self.fields['genero'] = forms.ChoiceField(
                    choices=[('', '---------')] + choices, 
                    required=False,
                    label=self.fields['genero'].label
                )
                
                # Replace the faixa_etaria field
                choices = self._get_choices_from_sqlitecloud('agenda_faixa_etaria')
                self.fields['faixa_etaria'] = forms.ChoiceField(
                    choices=[('', '---------')] + choices, 
                    required=False,
                    label=self.fields['faixa_etaria'].label
                )
                
                # Replace the proprietario field (User model)
                choices = self._get_choices_from_sqlitecloud('auth_user', label_field='username')
                self.fields['proprietario'] = forms.ChoiceField(
                    choices=[('', '---------')] + choices, 
                    required=False,
                    label=self.fields['proprietario'].label
                )
                
                # Set initial values
                if self.instance and self.instance.pk:
                    if self.instance.genero_id:
                        self.initial['genero'] = self.instance.genero_id
                    if self.instance.faixa_etaria_id:
                        self.initial['faixa_etaria'] = self.instance.faixa_etaria_id
                    if self.instance.proprietario_id:
                        self.initial['proprietario'] = self.instance.proprietario_id
                
            except Exception as e:
                logger.error(f"Error setting up CloudModelChoiceField: {e}")
    
    def _get_choices_from_sqlitecloud(self, table_name, value_field='id', label_field='nome'):
        """Helper method to get choices from SQLite Cloud."""
        try:
            from agenda.cloud_db import execute_query
            query = f"SELECT {value_field}, {label_field} FROM {table_name} ORDER BY {label_field}"
            results = execute_query(query)
            return [(str(item[0]), item[1]) for item in results] if results else []
        except Exception as e:
            logger.error(f"Error fetching choices from SQLite Cloud for {table_name}: {e}")
            return []

class AgendaAdmin(admin.ModelAdmin):
    form = AgendaAdminForm
    list_display = ('id', 'nome', 'sobrenome', 'contato', 'data_hora', 'valor')
    list_display_links = ('nome',)
    search_fields = ('nome', 'sobrenome', 'contato')
    list_per_page = 10
    ordering = ('-id',)
    
    def add_view(self, request, form_url='', extra_context=None):
        if settings.IS_VERCEL and settings.SQLITECLOUD_ENABLED:
            logger.info("Usando SQLiteCloud para o admin Agenda")
            # Se houver erros de ContentType, vamos tentar injetar um contenttype
            try:
                # Obtém o ID do ContentType usando SQLiteCloud
                from agenda.cloud_db import execute_query
                query = """
                SELECT id FROM django_content_type 
                WHERE app_label = 'agenda' AND model = 'agenda'
                """
                result = execute_query(query, ())
                if result and len(result) > 0:
                    logger.info(f"ContentType ID obtido: {result[0][0]}")
            except Exception as e:
                logger.error(f"Erro ao obter ContentType: {e}")
        
        return super().add_view(request, form_url, extra_context)
    
    def save_model(self, request, obj, form, change):
        # Se estivermos no Vercel e usando SQLiteCloud, salvar diretamente no SQLite Cloud
        if settings.IS_VERCEL and settings.SQLITECLOUD_ENABLED:
            try:
                from agenda.utils import create_agenda_item, update_agenda_item
                
                # Converter o objeto do formulário em um dicionário para as funções do SQLiteCloud
                data = form.cleaned_data.copy()
                
                # Convert genero and faixa_etaria from string to int if needed
                if 'genero' in data and data['genero']:
                    data['genero'] = int(data['genero'])
                
                if 'faixa_etaria' in data and data['faixa_etaria']:
                    data['faixa_etaria'] = int(data['faixa_etaria'])
                
                if change:  # Atualizando um existente
                    update_agenda_item(data, obj.id)
                else:  # Criando um novo
                    create_agenda_item(data)
                
                # Log para debug
                logger.info(f"Operação SQLiteCloud para {'atualização' if change else 'criação'} concluída")
                
            except Exception as e:
                logger.error(f"Erro ao salvar no SQLiteCloud: {e}")
                # Ainda tenta o método padrão como fallback
                super().save_model(request, obj, form, change)
        else:
            # Comportamento padrão para ambiente local
            super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        # Se estivermos no Vercel e usando SQLiteCloud, excluir diretamente do SQLite Cloud
        if settings.IS_VERCEL and settings.SQLITECLOUD_ENABLED:
            try:
                from agenda.utils import delete_agenda_item
                delete_agenda_item(obj.id)
                logger.info(f"Excluído registro com ID {obj.id} via SQLiteCloud")
            except Exception as e:
                logger.error(f"Erro ao excluir do SQLiteCloud: {e}")
                # Ainda tenta o método padrão como fallback
                super().delete_model(request, obj)
        else:
            # Comportamento padrão para ambiente local
            super().delete_model(request, obj)

class GeneroAdmin(admin.ModelAdmin):
    list_display = ('nome',)

class Faixa_EtariaAdmin(admin.ModelAdmin):
    list_display = ('nome',)

admin.site.register(Agenda, AgendaAdmin)
admin.site.register(Genero, GeneroAdmin)
admin.site.register(Faixa_Etaria, Faixa_EtariaAdmin)

# Patch ContentType to work with SQLite Cloud in Vercel
if settings.IS_VERCEL and settings.SQLITECLOUD_ENABLED:
    from agenda.cloud_db import execute_query
    
    # Override get method to check SQLite Cloud when the local DB fails
    original_get = ContentType.objects.get
    
    def cloud_content_type_get(*args, **kwargs):
        try:
            # Try the normal get method first
            return original_get(*args, **kwargs)
        except (OperationalError, ContentType.DoesNotExist):
            # If normal get fails, try to get from SQLite Cloud
            if 'app_label' in kwargs and 'model' in kwargs:
                app_label = kwargs['app_label']
                model = kwargs['model']
                
                # Use SQLite Cloud to get the content type
                query = """
                SELECT id FROM django_content_type 
                WHERE app_label = ? AND model = ?
                """
                result = execute_query(query, (app_label, model))
                
                if result and len(result) > 0:
                    # Create a ContentType instance without touching the database
                    content_type = ContentType(
                        id=result[0][0], 
                        app_label=app_label,
                        model=model
                    )
                    return content_type
                    
            # If we can't find it, let the original exception propagate
            raise
    
    # Apply the patch
    ContentType.objects.get = cloud_content_type_get
    
    # Patch ContentType.objects.get_for_model to use our custom get method
    original_get_for_model = ContentType.objects.get_for_model
    
    def cloud_get_for_model(model, for_concrete_model=True):
        try:
            return original_get_for_model(model, for_concrete_model)
        except (OperationalError, ContentType.DoesNotExist):
            # Get model info
            opts = model._meta
            app_label = opts.app_label
            model_name = opts.model_name
            
            # Try to get from SQLite Cloud
            try:
                # Use our patched get method which will check SQLite Cloud
                return ContentType.objects.get(app_label=app_label, model=model_name)
            except Exception:
                # If all fails, create a dummy ContentType
                content_type = ContentType(app_label=app_label, model=model_name)
                # Set an arbitrary ID (only for rendering, won't be saved)
                content_type.id = 1
                return content_type
    
    # Apply the patch
    ContentType.objects.get_for_model = cloud_get_for_model
