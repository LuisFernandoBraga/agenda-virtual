#!/usr/bin/env python
"""
Script de seed para popular o banco de dados com dados iniciais.
Este script cria registros nas tabelas:
- agenda_faixa_etaria
- agenda_genero
- agenda_agenda
- auth_user
- django_session
"""
import os
import sys
import django
import sqlite3
from datetime import datetime
from django.utils import timezone
from django.db import connection

# Configurar o ambiente Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from agenda.models import Faixa_Etaria, Genero, Agenda
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

def reset_db_sequence(model, id_value=1):
    """
    Reseta a sequência de autoincremento para a tabela indicada.
    Importante após inserir registros com IDs específicos.
    """
    cursor = connection.cursor()
    table_name = model._meta.db_table
    sequence_name = f"sqlite_sequence"
    
    cursor.execute(f"UPDATE {sequence_name} SET seq = {id_value-1} WHERE name = '{table_name}'")
    cursor.close()

def reset_database():
    """Limpa todas as tabelas relevantes do banco de dados"""
    print("Resetando o banco de dados...")
    
    # Limpar dados em ordem para evitar violações de chave estrangeira
    print("- Limpando sessões...")
    Session.objects.all().delete()
    
    print("- Limpando agendamentos...")
    Agenda.objects.all().delete()
    
    print("- Limpando faixas etárias...")
    Faixa_Etaria.objects.all().delete()
    
    print("- Limpando gêneros...")
    Genero.objects.all().delete()
    
    # Não removemos os usuários para preservar o superusuário

def import_users_from_db():
    """Importa usuários do banco de dados atual"""
    print("\nImportando usuários do banco de dados atual...")
    
    try:
        # Verificar se o arquivo de banco existe
        if not os.path.exists('db.sqlite3'):
            print("Arquivo de banco de dados db.sqlite3 não encontrado! Usuários não serão importados.")
            return
        
        # Conectar ao banco atual
        conn = sqlite3.connect('db.sqlite3')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar se a tabela auth_user existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
        if not cursor.fetchone():
            print("Tabela auth_user não encontrada! Usuários não serão importados.")
            conn.close()
            return
        
        # Buscar usuários existentes
        cursor.execute("SELECT * FROM auth_user")
        users = cursor.fetchall()
        
        if not users:
            print("Nenhum usuário encontrado para importar.")
            conn.close()
            return
        
        for user_data in users:
            username = user_data['username']
            # Verificar se o usuário já existe
            if User.objects.filter(username=username).exists():
                print(f"- Usuário {username} já existe, ignorando.")
                continue
            
            print(f"- Importando usuário: {username}")
            user = User(
                id=user_data['id'],
                password=user_data['password'],
                last_login=user_data['last_login'],
                is_superuser=bool(user_data['is_superuser']),
                username=username,
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                is_staff=bool(user_data['is_staff']),
                is_active=bool(user_data['is_active']),
                date_joined=user_data['date_joined']
            )
            user.save()
        
        # Resetar sequência
        reset_db_sequence(User, max(user.id for user in User.objects.all()) + 1)
        
        print(f"Importação de usuários concluída. Total: {len(users)} usuários.")
        conn.close()
    except Exception as e:
        print(f"Erro ao importar usuários: {e}")
        
def import_sessions_from_db():
    """Importa sessões do banco de dados atual"""
    print("\nImportando sessões do banco de dados atual...")
    
    try:
        # Verificar se o arquivo de banco existe
        if not os.path.exists('db.sqlite3'):
            print("Arquivo de banco de dados db.sqlite3 não encontrado! Sessões não serão importadas.")
            return
        
        # Conectar ao banco atual
        conn = sqlite3.connect('db.sqlite3')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar se a tabela django_session existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_session'")
        if not cursor.fetchone():
            print("Tabela django_session não encontrada! Sessões não serão importadas.")
            conn.close()
            return
        
        # Buscar sessões existentes
        cursor.execute("SELECT * FROM django_session")
        sessions = cursor.fetchall()
        
        if not sessions:
            print("Nenhuma sessão encontrada para importar.")
            conn.close()
            return
        
        for session_data in sessions:
            session_key = session_data['session_key']
            # Verificar se a sessão já existe
            if Session.objects.filter(session_key=session_key).exists():
                print(f"- Sessão {session_key} já existe, ignorando.")
                continue
            
            print(f"- Importando sessão: {session_key}")
            session = Session(
                session_key=session_key,
                session_data=session_data['session_data'],
                expire_date=session_data['expire_date']
            )
            session.save()
        
        print(f"Importação de sessões concluída. Total: {len(sessions)} sessões.")
        conn.close()
    except Exception as e:
        print(f"Erro ao importar sessões: {e}")

def create_superuser():
    """Cria um superusuário se ele não existir"""
    try:
        admin_user = User.objects.get(username='admin')
        print("Usuário admin já existe, usando-o.")
    except User.DoesNotExist:
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superusuário 'admin' criado com senha 'admin123'.")
    
    return admin_user

def main():
    # Resetar o banco de dados
    reset_database()
    
    # Importar usuários e sessões
    import_users_from_db()
    import_sessions_from_db()
    
    # Verificar ou criar superusuário
    admin_user = create_superuser()
    
    # Criar faixas etárias
    print("\nCriando faixas etárias...")
    faixas_etarias = [
        {"id": 1, "nome": "Criança"},
        {"id": 2, "nome": "Adulto"},
        {"id": 3, "nome": "Idoso"},
        {"id": 4, "nome": "Criança (0-12)"},
        {"id": 5, "nome": "Adolescente (13-17)"},
        {"id": 6, "nome": "Adulto (18-59)"},
        {"id": 7, "nome": "Idoso (60+)"}
    ]
    
    faixa_objects = {}
    for faixa in faixas_etarias:
        print(f"Criando faixa etária: {faixa['nome']}")
        obj = Faixa_Etaria.objects.create(
            id=faixa['id'],
            nome=faixa['nome']
        )
        faixa_objects[faixa['id']] = obj
    
    # Resetar sequência de IDs
    reset_db_sequence(Faixa_Etaria, len(faixas_etarias) + 1)
    
    # Criar gêneros
    print("\nCriando gêneros...")
    generos = [
        {"id": 1, "nome": "Masculino"},
        {"id": 2, "nome": "Feminino"},
        {"id": 3, "nome": "Prefiro não responder"},
        {"id": 4, "nome": "Não-binário"},
        {"id": 5, "nome": "Outro"}
    ]
    
    genero_objects = {}
    for genero in generos:
        print(f"Criando gênero: {genero['nome']}")
        obj = Genero.objects.create(
            id=genero['id'],
            nome=genero['nome']
        )
        genero_objects[genero['id']] = obj
    
    # Resetar sequência de IDs
    reset_db_sequence(Genero, len(generos) + 1)
    
    # Criar agendamentos
    print("\nCriando agendamentos...")
    agendamentos = [
        {
            "id": 1,
            "nome": "Luis Fernando",
            "sobrenome": "Braga",
            "cpf": "123.456.789-00",
            "email": "luis@example.com",
            "contato": "(11) 98765-4321",
            "descricao_servico": "Corte de cabelo",
            "data_hora": timezone.make_aware(datetime(2025, 4, 6, 20, 0, 43)),
            "valor": "50,00",
            "genero_id": 1,
            "faixa_etaria_id": 6
        },
        {
            "id": 2,
            "nome": "Ana",
            "sobrenome": "Braga",
            "cpf": "987.654.321-00",
            "email": "ana@example.com",
            "contato": "(11) 91234-5678",
            "descricao_servico": "Manicure",
            "data_hora": timezone.make_aware(datetime(2025, 4, 6, 20, 13, 27)),
            "valor": "40,00",
            "genero_id": 2,
            "faixa_etaria_id": 6
        },
        {
            "id": 3,
            "nome": "Airto",
            "sobrenome": "Junior",
            "cpf": "456.789.123-00",
            "email": "airto@example.com",
            "contato": "(11) 95555-1234",
            "descricao_servico": "Corte e barba",
            "data_hora": timezone.make_aware(datetime(2025, 4, 6, 23, 14, 59)),
            "valor": "70,00",
            "genero_id": 1,
            "faixa_etaria_id": 6
        },
        {
            "id": 4,
            "nome": "Letícia",
            "sobrenome": "Murer",
            "cpf": "111.222.333-44",
            "email": "leticia@example.com",
            "contato": "(11) 97777-8888",
            "descricao_servico": "Coloração",
            "data_hora": timezone.make_aware(datetime(2025, 4, 6, 23, 59, 26)),
            "valor": "120,00",
            "genero_id": 2,
            "faixa_etaria_id": 6
        },
        {
            "id": 5,
            "nome": "Willians",
            "sobrenome": "Coral",
            "cpf": "555.666.777-88",
            "email": "willians@example.com",
            "contato": "(11) 96666-2222",
            "descricao_servico": "Corte moderno",
            "data_hora": timezone.make_aware(datetime(2025, 4, 7, 0, 0, 34)),
            "valor": "60,00",
            "genero_id": 1,
            "faixa_etaria_id": 6
        },
        {
            "id": 6,
            "nome": "Rodrigo",
            "sobrenome": "Menezes",
            "cpf": "999.888.777-66",
            "email": "rodrigo@example.com",
            "contato": "(11) 92222-3333",
            "descricao_servico": "Barba",
            "data_hora": timezone.make_aware(datetime(2025, 4, 7, 0, 2, 12)),
            "valor": "30,00",
            "genero_id": 1,
            "faixa_etaria_id": 6
        },
        {
            "id": 7,
            "nome": "Wellmmer",
            "sobrenome": "Lucas",
            "cpf": "123.123.123-12",
            "email": "wellmmer@example.com",
            "contato": "(11) 99999-9999",
            "descricao_servico": "Corte e tratamento capilar",
            "data_hora": timezone.make_aware(datetime(1995, 1, 20, 22, 16, 0)),
            "valor": "80,00",
            "genero_id": 1,
            "faixa_etaria_id": 6,
            "imagem": "WELLMMER_GUITAR.jpeg"
        }
    ]
    
    for agendamento_data in agendamentos:
        print(f"Criando agendamento: {agendamento_data['nome']} {agendamento_data['sobrenome']}")
        
        # Obter objetos relacionados
        genero = genero_objects.get(agendamento_data.get('genero_id'))
        faixa_etaria = faixa_objects.get(agendamento_data.get('faixa_etaria_id'))
        
        # Criar o agendamento
        agendamento = Agenda(
            id=agendamento_data['id'],
            nome=agendamento_data['nome'],
            sobrenome=agendamento_data['sobrenome'],
            cpf=agendamento_data.get('cpf', ''),
            email=agendamento_data.get('email', ''),
            contato=agendamento_data['contato'],
            descricao_servico=agendamento_data['descricao_servico'],
            data_hora=agendamento_data['data_hora'],
            valor=agendamento_data['valor'],
            show=True,
            genero=genero,
            faixa_etaria=faixa_etaria,
            proprietario=admin_user
        )
        
        # Observação sobre imagem
        if 'imagem' in agendamento_data and agendamento_data['imagem']:
            print(f"Atenção: Este agendamento deveria ter uma imagem ({agendamento_data['imagem']}), mas o seeder não configura imagens.")
        
        agendamento.save()
    
    # Resetar sequência de IDs
    reset_db_sequence(Agenda, len(agendamentos) + 1)
    
    print("\nPopulação de dados concluída com sucesso!")

if __name__ == "__main__":
    main() 