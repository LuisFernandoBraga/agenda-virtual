"""
Context processors personalizados para a aplicação agenda.
"""
from django.conf import settings

def cloud_settings(request):
    """
    Adiciona variáveis relacionadas ao SQLite Cloud ao contexto dos templates.
    """
    return {
        'SQLITECLOUD_ENABLED': settings.SQLITECLOUD_ENABLED,
    } 