"""
Middleware para gerenciar a conexão com o SQLite Cloud.
"""
from django.conf import settings
from agenda.cloud_db import close_connection

class SqliteCloudConnectionMiddleware:
    """
    Middleware para gerenciar o ciclo de vida da conexão com o SQLite Cloud.
    Fecha a conexão ao final de cada requisição.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Código a ser executado para cada requisição antes da view
        
        # Chama a view
        response = self.get_response(request)
        
        # Código a ser executado para cada requisição após a view
        if settings.SQLITECLOUD_ENABLED:
            close_connection()
            
        return response 