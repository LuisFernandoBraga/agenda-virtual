"""
Template tags personalizados para buscar logs do admin do SQLite Cloud.
"""
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from agenda.cloud_db import execute_query
from django.utils.encoding import force_str
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def get_admin_log_from_cloud(limit, user=None):
    """
    Busca os logs do admin diretamente do SQLite Cloud.
    
    Este template tag substitui o {% get_admin_log %} padrão do Django
    quando estamos usando SQLite Cloud no ambiente Vercel.
    """
    # Se não estiver usando SQLite Cloud, retorna lista vazia
    if not settings.SQLITECLOUD_ENABLED:
        return []
    
    # Condições da consulta
    conditions = []
    params = []
    
    # Filtrar por usuário, se especificado
    if user and user.is_authenticated:
        conditions.append("user_id = ?")
        params.append(user.id)
    
    # Montar a cláusula WHERE
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Consulta SQL para buscar logs do admin
    query = f"""
    SELECT 
        dl.id, 
        dl.action_time, 
        dl.user_id, 
        dl.content_type_id, 
        dl.object_id, 
        dl.object_repr, 
        dl.action_flag, 
        dl.change_message,
        ct.app_label,
        ct.model
    FROM 
        django_admin_log dl
    LEFT JOIN 
        django_content_type ct ON dl.content_type_id = ct.id
    WHERE 
        {where_clause}
    ORDER BY 
        dl.action_time DESC
    LIMIT ?
    """
    
    params.append(limit)
    
    try:
        # Executar a consulta
        results = execute_query(query, tuple(params))
        
        # Transformar os resultados em objetos do tipo LogEntry personalizado
        log_entries = []
        for row in results:
            entry = CloudLogEntry()
            entry.id = row[0]
            entry.action_time = row[1]
            entry.user_id = row[2]
            entry.content_type_id = row[3]
            entry.object_id = row[4]
            entry.object_repr = row[5]
            entry.action_flag = row[6]
            entry.change_message = row[7]
            
            # Informações de content_type
            if row[3]:  # Se tiver content_type_id
                entry._content_type = CloudContentType()
                entry._content_type.id = row[3]
                entry._content_type.app_label = row[8]
                entry._content_type.model = row[9]
                entry._content_type.name = f"{row[8]}.{row[9]}"
            
            log_entries.append(entry)
        
        return log_entries
    except Exception as e:
        if settings.DEBUG:
            return [f"Erro ao buscar logs: {str(e)}"]
        return []

# Classes simplificadas para simular os modelos Django
class CloudLogEntry:
    """Classe simplificada para simular LogEntry."""
    
    def __init__(self):
        self.id = None
        self.action_time = None
        self.user_id = None
        self.content_type_id = None
        self._content_type = None
        self.object_id = None
        self.object_repr = None
        self.action_flag = None
        self.change_message = None
    
    @property
    def is_addition(self):
        return self.action_flag == 1
    
    @property
    def is_change(self):
        return self.action_flag == 2
    
    @property
    def is_deletion(self):
        return self.action_flag == 3
    
    @property
    def content_type(self):
        return self._content_type
    
    def get_admin_url(self):
        if not self.content_type or not self.object_id:
            return None
        
        # Construir URL relativa para o objeto no admin
        # Formato: /admin/{app_label}/{model}/{object_id}/change/
        if self.is_addition or self.is_change:
            return f"/admin/{self.content_type.app_label}/{self.content_type.model}/{self.object_id}/change/"
        return None

class CloudContentType:
    """Classe simplificada para simular ContentType."""
    
    def __init__(self):
        self.id = None
        self.app_label = None
        self.model = None
        self.name = None 