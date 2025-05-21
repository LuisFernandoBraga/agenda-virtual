"""
Utilidades para a aplicação agenda.
"""
from django.conf import settings
from agenda.cloud_db import execute_query, execute_update

def get_agenda_items(limit=None, offset=None, search=None):
    """
    Obtém itens da agenda do banco de dados.
    Se SQLite Cloud estiver habilitado, usa a conexão direta.
    Caso contrário, usa o ORM do Django.
    
    Args:
        limit (int, optional): Limite de itens a serem retornados
        offset (int, optional): Deslocamento da consulta
        search (str, optional): Termo de busca
        
    Returns:
        list: Lista de itens da agenda
    """
    if settings.SQLITECLOUD_ENABLED:
        # Construindo a consulta SQL
        query = """
        SELECT 
            a.id, a.nome, a.sobrenome, a.cpf, a.email, a.contato,
            a.descricao_servico, a.data_hora, a.valor, a.show,
            a.imagem, g.nome as genero, f.nome as faixa_etaria,
            u.username as proprietario
        FROM agenda_agenda a
        LEFT JOIN agenda_genero g ON a.genero_id = g.id
        LEFT JOIN agenda_faixa_etaria f ON a.faixa_etaria_id = f.id
        LEFT JOIN auth_user u ON a.proprietario_id = u.id
        WHERE a.show = 1
        """
        
        params = []
        
        if search:
            query += " AND (a.nome LIKE ? OR a.sobrenome LIKE ? OR a.cpf LIKE ?)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
            
        query += " ORDER BY a.id DESC"
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)
                
        return execute_query(query, tuple(params) if params else None)
    
    # Se não estiver usando SQLite Cloud, retorna None para usar o ORM normal
    return None

def create_agenda_item(data):
    """
    Cria um novo item de agenda.
    Se SQLite Cloud estiver habilitado, usa a conexão direta.
    Caso contrário, usa o ORM do Django.
    
    Args:
        data (dict): Dados do item de agenda
        
    Returns:
        bool: True se foi criado com sucesso, False caso contrário
    """
    if settings.SQLITECLOUD_ENABLED:
        query = """
        INSERT INTO agenda_agenda (
            nome, sobrenome, cpf, email, contato, descricao_servico,
            data_hora, valor, show, genero_id, faixa_etaria_id, proprietario_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            data.get('nome', ''),
            data.get('sobrenome', ''),
            data.get('cpf', ''),
            data.get('email', ''),
            data.get('contato', ''),
            data.get('descricao_servico', ''),
            data.get('data_hora', ''),
            data.get('valor', ''),
            1,  # show
            data.get('genero_id'),
            data.get('faixa_etaria_id'),
            data.get('proprietario_id')
        )
        
        execute_update(query, params)
        return True
        
    # Se não estiver usando SQLite Cloud, retorna False para usar o ORM normal
    return False 