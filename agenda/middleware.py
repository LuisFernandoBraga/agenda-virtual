"""
Middleware para gerenciar a conexão com o SQLite Cloud.
"""
from django.conf import settings
from agenda.cloud_db import close_connection, execute_query
import logging

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