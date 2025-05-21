"""
Middleware para gerenciar a conexão com o SQLite Cloud.
"""
from django.conf import settings
from agenda.cloud_db import close_connection, execute_query
import logging
from django.forms import forms

logger = logging.getLogger(__name__)

class SqliteCloudConnectionMiddleware:
    """
    Middleware para gerenciar o ciclo de vida da conexão com o SQLite Cloud.
    Fecha a conexão ao final de cada requisição.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Código a ser executado para cada requisição antes da view
        
        # Se estivermos no admin e com SQLiteCloud ativado no Vercel, patchar o ContentType
        if settings.IS_VERCEL and settings.SQLITECLOUD_ENABLED and request.path.startswith('/admin/'):
            self.patch_content_type_for_admin()
            self.patch_model_choice_field()
            self.patch_admin_widgets()
            self.patch_model_form_meta()
        
        # Chama a view
        response = self.get_response(request)
        
        # Código a ser executado para cada requisição após a view
        if settings.SQLITECLOUD_ENABLED:
            close_connection()
            
        return response
    
    def patch_content_type_for_admin(self):
        """
        Patch temporal para ContentType durante requisições ao admin.
        Isso permite que o admin acesse o ContentType via SQLite Cloud.
        """
        try:
            from django.contrib.contenttypes.models import ContentType
            from django.db import OperationalError
            
            # Verificar se já foi patcheado
            if hasattr(ContentType.objects, '_cloud_patched'):
                return
                
            # Guardar o método original
            original_get = ContentType.objects.get
            
            def cloud_content_type_get(*args, **kwargs):
                """
                Tenta obter o ContentType primeiro pelo método normal,
                e se falhar, tenta obter via SQLite Cloud.
                """
                try:
                    # Tenta o método normal primeiro
                    return original_get(*args, **kwargs)
                except (OperationalError, ContentType.DoesNotExist):
                    # Se falhar, tenta via SQLite Cloud
                    if 'app_label' in kwargs and 'model' in kwargs:
                        app_label = kwargs['app_label']
                        model = kwargs['model']
                        
                        # Usar SQLite Cloud para obter o tipo de conteúdo
                        query = """
                        SELECT id FROM django_content_type 
                        WHERE app_label = ? AND model = ?
                        """
                        result = execute_query(query, (app_label, model))
                        
                        if result and len(result) > 0:
                            logger.info(f"ContentType encontrado via SQLiteCloud para {app_label}.{model}: {result[0][0]}")
                            # Criar uma instância de ContentType sem tocar no banco
                            content_type = ContentType(
                                id=result[0][0], 
                                app_label=app_label,
                                model=model
                            )
                            return content_type
                    
                    # Se não encontrar, propaga a exceção original
                    logger.error(f"ContentType não encontrado para {kwargs.get('app_label', '')}.{kwargs.get('model', '')}")
                    raise
            
            # Aplicar o patch
            ContentType.objects.get = cloud_content_type_get
            ContentType.objects._cloud_patched = True
            
            logger.info("ContentType patcheado com sucesso para uso com SQLite Cloud")
            
        except Exception as e:
            logger.error(f"Erro ao patchar ContentType: {e}") 

    def patch_model_choice_field(self):
        """
        Patcha o ModelChoiceField para usar uma versão personalizada quando não conseguir 
        carregar dados do banco de dados em memória (casos como 'no such table').
        """
        try:
            from django.forms.models import ModelChoiceField
            from django.db import OperationalError
            
            # Verificar se já foi patcheado
            if hasattr(ModelChoiceField, '_cloud_patched'):
                return
            
            # Guardar o método original
            original_get_choices = ModelChoiceField._get_choices
            
            def cloud_get_choices(self):
                """
                Versão patcheada do _get_choices que tenta usar o SQLite Cloud
                quando não consegue obter os dados do banco local.
                """
                try:
                    # Tenta o método normal primeiro
                    return original_get_choices(self)
                except OperationalError as e:
                    error_message = str(e).lower()
                    if 'no such table' in error_message:
                        # Se a tabela não existir, tenta obter de SQLite Cloud
                        model = self.queryset.model
                        
                        # Tratamento especial para o modelo User
                        if model.__name__ == 'User':
                            table_name = 'auth_user'
                            id_field = 'id'
                            label_field = 'username'
                        else:
                            # Para outros modelos, inferir o nome da tabela a partir do modelo
                            table_name = f"agenda_{model._meta.model_name}"
                            id_field = 'id'
                            label_field = 'nome'
                        
                        try:
                            from agenda.cloud_db import execute_query
                            
                            # Obter todos os registros da tabela
                            query = f"SELECT {id_field}, {label_field} FROM {table_name} ORDER BY {label_field}"
                            results = execute_query(query)
                            
                            if results:
                                logger.info(f"Obteve {len(results)} opções de {table_name} via SQLite Cloud")
                                
                                # Converter para o formato esperado pelo ModelChoiceField
                                from django.utils.datastructures import MultiValueDict
                                choices = [(self.prepare_value(None), self.empty_label)]
                                for item_id, nome in results:
                                    choices.append((str(item_id), nome))
                                    
                                return choices
                        except Exception as ex:
                            logger.error(f"Erro ao obter opções do SQLite Cloud: {ex}")
                    
                    # Se tudo falhar, retorna uma lista vazia (ou propaga a exceção original)
                    return [(None, self.empty_label)]
            
            # Aplicar o patch
            ModelChoiceField._get_choices = cloud_get_choices
            ModelChoiceField._cloud_patched = True
            
            logger.info("ModelChoiceField patcheado com sucesso para uso com SQLite Cloud")
            
        except Exception as e:
            logger.error(f"Erro ao patchar ModelChoiceField: {e}")
            return None 

    def patch_admin_widgets(self):
        """
        Patcha o RelatedFieldWidgetWrapper do Django admin para trabalhar com SQLite Cloud.
        """
        try:
            from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
            
            # Verificar se já foi patcheado
            if hasattr(RelatedFieldWidgetWrapper, '_cloud_patched'):
                return
            
            # Guardar o método original
            original_get_context = RelatedFieldWidgetWrapper.get_context
            
            def cloud_get_context(self, name, value, attrs):
                """
                Versão patcheada do get_context para evitar consultas ao banco local.
                """
                try:
                    return original_get_context(self, name, value, attrs)
                except OperationalError as e:
                    if 'no such table' in str(e).lower():
                        # Se a tabela não existir, cria um contexto mínimo sem consultar o banco
                        context = self.widget.get_context(name, value, attrs)
                        context['widget']['is_hidden'] = self.is_hidden
                        context['widget']['needs_multipart_form'] = self.needs_multipart_form
                        context['widget']['name'] = name
                        context['widget']['is_relation'] = True
                        
                        # Desativar os links de adicionar/editar/excluir
                        context['widget']['can_add_related'] = False
                        context['widget']['can_change_related'] = False
                        context['widget']['can_delete_related'] = False
                        
                        logger.info(f"RelatedFieldWidgetWrapper: criando contexto mínimo para {name}")
                        return context
                    raise
            
            # Aplicar o patch
            RelatedFieldWidgetWrapper.get_context = cloud_get_context
            RelatedFieldWidgetWrapper._cloud_patched = True
            
            logger.info("RelatedFieldWidgetWrapper patcheado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao patchar RelatedFieldWidgetWrapper: {e}") 

    def patch_model_form_meta(self):
        """
        Patcha o ModelFormMetaclass para evitar consultas de banco de dados problemáticas.
        """
        try:
            from django.forms.models import ModelFormMetaclass
            from django.db import OperationalError
            
            # Verificar se já foi patcheado
            if hasattr(ModelFormMetaclass, '_cloud_patched'):
                return
            
            # Armazenar a versão original do método
            original_new = ModelFormMetaclass.__new__
            
            def patched_new(mcs, name, bases, attrs):
                """
                Versão patcheada do __new__ para evitar consultas problematicas no SQLite Cloud.
                """
                try:
                    # Tentar a versão original primeiro
                    return original_new(mcs, name, bases, attrs)
                except OperationalError as e:
                    if 'no such table' in str(e).lower():
                        logger.error(f"Erro de banco de dados ao criar formulário {name}: {e}")
                        
                        # Tentar criar uma versão mais básica do formulário
                        # que não dependa de consultas ao banco
                        if 'Meta' in attrs and hasattr(attrs['Meta'], 'model'):
                            # Marca que este é um formulário de contingência
                            attrs['_is_fallback_form'] = True
                            
                            # Simplesmente crie um Form regular sem modelagem
                            form_class = type(name, (forms.Form,), attrs)
                            logger.info(f"Criado formulário de fallback para {name}")
                            return form_class
                        
                    # Se não podemos resolver, propagar a exceção
                    raise
            
            # Aplicar o patch
            ModelFormMetaclass.__new__ = patched_new
            ModelFormMetaclass._cloud_patched = True
            
            logger.info("ModelFormMetaclass patcheado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao patchar ModelFormMetaclass: {e}") 