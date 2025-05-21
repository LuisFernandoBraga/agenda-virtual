#!/usr/bin/env python
"""
Script para popular o banco de dados SQLite Cloud com dados iniciais.
Útil para o deploy na Vercel, onde o banco de dados é apenas leitura.

Execução:
python scripts/populate_sqlitecloud.py
"""
import os
import sys
import django
import sqlitecloud
from django.core.management import call_command

# Adiciona o diretório do projeto ao path do Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configura o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from agenda.models import Genero, Faixa_Etaria, Agenda

def create_tables():
    """
    Cria as tabelas no SQLite Cloud.
    """
    conn = sqlitecloud.connect(settings.SQLITECLOUD_CONNECTION_STRING)
    
    # Tabela de usuários
    conn.execute('''
    CREATE TABLE IF NOT EXISTS auth_user (
        id INTEGER PRIMARY KEY,
        password VARCHAR(128) NOT NULL,
        last_login DATETIME,
        is_superuser BOOLEAN NOT NULL,
        username VARCHAR(150) NOT NULL UNIQUE,
        first_name VARCHAR(150) NOT NULL,
        last_name VARCHAR(150) NOT NULL,
        email VARCHAR(254) NOT NULL,
        is_staff BOOLEAN NOT NULL,
        is_active BOOLEAN NOT NULL,
        date_joined DATETIME NOT NULL
    );
    ''')
    
    # Tabela de gêneros
    conn.execute('''
    CREATE TABLE IF NOT EXISTS agenda_genero (
        id INTEGER PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );
    ''')
    
    # Tabela de faixas etárias
    conn.execute('''
    CREATE TABLE IF NOT EXISTS agenda_faixa_etaria (
        id INTEGER PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );
    ''')
    
    # Tabela de agendamentos
    conn.execute('''
    CREATE TABLE IF NOT EXISTS agenda_agenda (
        id INTEGER PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        sobrenome VARCHAR(100) NOT NULL,
        cpf VARCHAR(50) NOT NULL,
        email VARCHAR(50) NOT NULL,
        contato VARCHAR(50) NOT NULL,
        descricao_servico TEXT NOT NULL,
        data_hora DATETIME NOT NULL,
        valor VARCHAR(50) NOT NULL,
        show BOOLEAN NOT NULL,
        imagem VARCHAR(100),
        genero_id INTEGER,
        faixa_etaria_id INTEGER,
        proprietario_id INTEGER,
        FOREIGN KEY (genero_id) REFERENCES agenda_genero (id),
        FOREIGN KEY (faixa_etaria_id) REFERENCES agenda_faixa_etaria (id),
        FOREIGN KEY (proprietario_id) REFERENCES auth_user (id)
    );
    ''')
    
    conn.close()
    print("Tabelas criadas com sucesso!")

def populate_data():
    """
    Popula o banco de dados SQLite Cloud com dados iniciais.
    """
    conn = sqlitecloud.connect(settings.SQLITECLOUD_CONNECTION_STRING)
    
    # Adicionar usuário admin
    admin_exists = conn.execute("SELECT COUNT(*) FROM auth_user WHERE username = 'admin';").fetchone()[0]
    if admin_exists == 0:
        conn.execute('''
        INSERT INTO auth_user (password, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
        ''', ('pbkdf2_sha256$720000$OQr82Oe63jLbztwSOMvdp3$9cA+JZvYWUEILl5ZICt0WLZ1smzhs4QgZ0Z/hbReYjw=', 1, 'admin', 'Admin', 'User', 'admin@example.com', 1, 1))
        print("Usuário admin criado com sucesso! Senha: admin123")
    
    # Adicionar gêneros
    generos = ['Masculino', 'Feminino', 'Não-binário', 'Outro']
    for genero in generos:
        genero_exists = conn.execute("SELECT COUNT(*) FROM agenda_genero WHERE nome = ?;", (genero,)).fetchone()[0]
        if genero_exists == 0:
            conn.execute("INSERT INTO agenda_genero (nome) VALUES (?);", (genero,))
    print("Gêneros adicionados com sucesso!")
    
    # Adicionar faixas etárias
    faixas = ['Criança (0-12)', 'Adolescente (13-17)', 'Adulto (18-59)', 'Idoso (60+)']
    for faixa in faixas:
        faixa_exists = conn.execute("SELECT COUNT(*) FROM agenda_faixa_etaria WHERE nome = ?;", (faixa,)).fetchone()[0]
        if faixa_exists == 0:
            conn.execute("INSERT INTO agenda_faixa_etaria (nome) VALUES (?);", (faixa,))
    print("Faixas etárias adicionadas com sucesso!")
    
    # Adicionar agendamentos de exemplo
    agendamentos = [
        ('João', 'Silva', '123.456.789-00', 'joao@example.com', '(11) 98765-4321', 'Corte de cabelo', '2023-05-20 14:30:00', '50,00', 1, 1, 3),
        ('Maria', 'Santos', '987.654.321-00', 'maria@example.com', '(11) 91234-5678', 'Manicure', '2023-05-21 10:00:00', '40,00', 2, 3, 1),
    ]
    
    for agenda in agendamentos:
        nome, sobrenome, cpf, email, contato, descricao, data_hora, valor, genero_id, faixa_id, proprietario_id = agenda
        agenda_exists = conn.execute("SELECT COUNT(*) FROM agenda_agenda WHERE nome = ? AND sobrenome = ? AND cpf = ?;", (nome, sobrenome, cpf)).fetchone()[0]
        if agenda_exists == 0:
            conn.execute('''
            INSERT INTO agenda_agenda (nome, sobrenome, cpf, email, contato, descricao_servico, data_hora, valor, show, genero_id, faixa_etaria_id, proprietario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?);
            ''', (nome, sobrenome, cpf, email, contato, descricao, data_hora, valor, genero_id, faixa_id, proprietario_id))
    print("Agendamentos de exemplo adicionados com sucesso!")
    
    conn.close()

if __name__ == "__main__":
    # Verifica se o SQLite Cloud está habilitado
    if not settings.SQLITECLOUD_ENABLED:
        os.environ['SQLITECLOUD_ENABLED'] = '1'
    
    create_tables()
    populate_data()
    print("Processo de população do banco de dados SQLite Cloud concluído com sucesso!") 