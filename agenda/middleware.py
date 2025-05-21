"""
Middleware para gerenciar a conexão com o SQLite Cloud.
"""
from django.conf import settings
from agenda.cloud_db import close_connection, execute_query
from django.contrib.auth import get_user_model
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser
import functools

UserModel = get_user_model()

def get_user(request):
    """
    Obtém o usuário para a requisição atual, seja do cache ou do SQLite Cloud.
    """
    # Se o usuário já foi buscado, retorna do cache
    if hasattr(request, '_cached_user'):
        return request._cached_user
        
    # Se não está autenticado (sem session_auth_hash), retorna usuário anônimo
    if not hasattr(request, 'session') or not request.session.get('_auth_user_id'):
        request._cached_user = AnonymousUser()
        return request._cached_user
        
    # Buscar usuário pelo ID
    user_id = request.session.get('_auth_user_id')
    
    # Se estiver no ambiente SQLite Cloud, busca diretamente
    if settings.SQLITECLOUD_ENABLED:
        # Busca o usuário no SQLite Cloud
        query = "SELECT * FROM auth_user WHERE id = ?"
        users = execute_query(query, (user_id,))
        
        if not users:
            request._cached_user = AnonymousUser()
            return request._cached_user
            
        user_data = users[0]
        
        # Criar um objeto User (não salvar no banco)
        user = UserModel()
        user.id = int(user_id)
        user.username = user_data[4]  # username field
        user.password = user_data[1]  # password field
        user.is_active = bool(user_data[9])  # is_active field
        user.is_staff = bool(user_data[8])   # is_staff field
        user.is_superuser = bool(user_data[3])  # is_superuser field
        
        # Preencher outros campos básicos
        user.email = user_data[7]  # email field
        user.first_name = user_data[5]  # first_name field
        user.last_name = user_data[6]   # last_name field
        
        # Cache o usuário para requisições futuras
        request._cached_user = user
        return user
    else:
        # Ambiente regular do Django, usar a abordagem padrão
        try:
            user = UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            user = AnonymousUser()
            
        request._cached_user = user
        return user

class SqliteCloudConnectionMiddleware:
    """
    Middleware para gerenciar o ciclo de vida da conexão com o SQLite Cloud.
    Fecha a conexão ao final de cada requisição.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Código a ser executado para cada requisição antes da view
        
        # Para ambientes Vercel, adicionar um usuário lazy que será carregado 
        # apenas quando necessário, sem depender do banco de dados
        if settings.SQLITECLOUD_ENABLED:
            request.user = SimpleLazyObject(functools.partial(get_user, request))
        
        # Chama a view
        response = self.get_response(request)
        
        # Código a ser executado para cada requisição após a view
        if settings.SQLITECLOUD_ENABLED:
            close_connection()
            
        return response 