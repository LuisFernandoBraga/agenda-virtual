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
        WHERE a.show = 1 AND a.id IS NOT NULL AND a.id != ''
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
                
        result = execute_query(query, tuple(params) if params else None)
        
        # Log para depuração do resultado
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"SQLite Cloud query result count: {len(result) if result else 0}")
        if result and len(result) > 0:
            logger.info(f"First ID: {result[0][0]}")
            
        return result
    
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
        # Preparar os dados para inserção
        genero_id = data.get('genero')
        faixa_etaria_id = data.get('faixa_etaria')
        
        # Campos de imagem requerem tratamento especial
        imagem_path = ''
        if 'imagem' in data and hasattr(data['imagem'], 'name'):
            # Em uma implementação completa, você deve fazer upload do arquivo
            # para um serviço como S3 e salvar o caminho
            imagem_path = data['imagem'].name
        
        # Formatar a data e hora
        data_hora = data.get('data_hora', '')
        if hasattr(data_hora, 'strftime'):
            data_hora = data_hora.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
        INSERT INTO agenda_agenda (
            nome, sobrenome, cpf, email, contato, descricao_servico,
            data_hora, valor, show, imagem, genero_id, faixa_etaria_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
        """
        
        params = (
            data.get('nome', ''),
            data.get('sobrenome', ''),
            data.get('cpf', ''),
            data.get('email', ''),
            data.get('contato', ''),
            data.get('descricao_servico', ''),
            data_hora,
            data.get('valor', ''),
            imagem_path,
            genero_id if genero_id else None,
            faixa_etaria_id if faixa_etaria_id else None
        )
        
        execute_update(query, params)
        return True
        
    # Se não estiver usando SQLite Cloud, retorna False para usar o ORM normal
    return False

def update_agenda_item(data, item_id):
    """
    Atualiza um item existente da agenda no SQLite Cloud.
    
    Args:
        data (dict): Dados do item de agenda
        item_id (int): ID do item a ser atualizado
        
    Returns:
        bool: True se foi atualizado com sucesso, False caso contrário
    """
    if settings.SQLITECLOUD_ENABLED:
        # Preparar os dados para atualização
        genero_id = data.get('genero')
        faixa_etaria_id = data.get('faixa_etaria')
        
        # Campos de imagem requerem tratamento especial
        imagem_path = ''
        if 'imagem' in data and hasattr(data['imagem'], 'name'):
            # Em uma implementação completa, você deve fazer upload do arquivo
            # para um serviço como S3 e salvar o caminho
            imagem_path = data['imagem'].name
        
        # Formatar a data e hora
        data_hora = data.get('data_hora', '')
        if hasattr(data_hora, 'strftime'):
            data_hora = data_hora.strftime('%Y-%m-%d %H:%M:%S')
        
        query = """
        UPDATE agenda_agenda SET
            nome = ?,
            sobrenome = ?,
            cpf = ?,
            email = ?,
            contato = ?,
            descricao_servico = ?,
            data_hora = ?,
            valor = ?
        """
        
        params = [
            data.get('nome', ''),
            data.get('sobrenome', ''),
            data.get('cpf', ''),
            data.get('email', ''),
            data.get('contato', ''),
            data.get('descricao_servico', ''),
            data_hora,
            data.get('valor', '')
        ]
        
        # Adicionar campos opcionais se fornecidos
        if imagem_path:
            query += ", imagem = ?"
            params.append(imagem_path)
            
        if genero_id:
            query += ", genero_id = ?"
            params.append(genero_id)
            
        if faixa_etaria_id:
            query += ", faixa_etaria_id = ?"
            params.append(faixa_etaria_id)
        
        # Finalizar a query com a condição WHERE
        query += " WHERE id = ?"
        params.append(item_id)
        
        execute_update(query, tuple(params))
        return True
        
    # Se não estiver usando SQLite Cloud, retorna False
    return False

def delete_agenda_item(item_id):
    """
    Exclui um item da agenda no SQLite Cloud.
    
    Args:
        item_id (int): ID do item a ser excluído
        
    Returns:
        bool: True se foi excluído com sucesso, False caso contrário
    """
    if settings.SQLITECLOUD_ENABLED:
        query = "DELETE FROM agenda_agenda WHERE id = ?"
        execute_update(query, (item_id,))
        return True
        
    # Se não estiver usando SQLite Cloud, retorna False
    return False 