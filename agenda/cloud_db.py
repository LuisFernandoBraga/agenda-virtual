"""
Módulo para gerenciar a conexão com o SQLite Cloud.
Usado em ambientes de produção como a Vercel.
"""
import sqlitecloud
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import threading

# Variável para armazenar a conexão por thread
_local = threading.local()

def get_connection():
    """
    Retorna uma conexão com o SQLite Cloud.
    Mantém uma conexão por thread para evitar problemas de concorrência.
    """
    if not hasattr(_local, 'connection') or _local.connection is None:
        if not settings.SQLITECLOUD_ENABLED:
            raise ImproperlyConfigured("SQLite Cloud não está habilitado nas configurações.")
        
        _local.connection = sqlitecloud.connect(settings.SQLITECLOUD_CONNECTION_STRING)
    
    return _local.connection

def close_connection():
    """
    Fecha a conexão com o SQLite Cloud se estiver aberta.
    """
    if hasattr(_local, 'connection') and _local.connection is not None:
        _local.connection.close()
        _local.connection = None

def execute_query(query, params=None):
    """
    Executa uma consulta no SQLite Cloud e retorna o resultado.
    
    Args:
        query (str): A consulta SQL a ser executada
        params (tuple, optional): Parâmetros para a consulta
        
    Returns:
        list: Resultado da consulta
    """
    conn = get_connection()
    
    try:
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)
        
        return cursor.fetchall()
    except Exception as e:
        # Fechar e reabrir conexão em caso de erro
        close_connection()
        raise e

def execute_update(query, params=None):
    """
    Executa uma atualização no SQLite Cloud.
    
    Args:
        query (str): A consulta SQL a ser executada
        params (tuple, optional): Parâmetros para a consulta
        
    Returns:
        int: Número de linhas afetadas
    """
    conn = get_connection()
    
    try:
        if params:
            cursor = conn.execute(query, params)
        else:
            cursor = conn.execute(query)
        
        return cursor.rowcount
    except Exception as e:
        # Fechar e reabrir conexão em caso de erro
        close_connection()
        raise e 