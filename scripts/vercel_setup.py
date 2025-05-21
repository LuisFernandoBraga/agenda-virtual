#!/usr/bin/env python
"""
Script de preparação para a Vercel.
Este script verifica e configura o banco de dados SQLite Cloud para uso com Django.
"""
import os
import sys

# Adicionar o diretório raiz ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
os.environ.setdefault('VERCEL', '1')  # Forçar modo Vercel

# Não usar a configuração normal do Django para evitar imports circulares
# Apenas importar SQLiteCloud diretamente
import sqlitecloud

print("Iniciando setup para Vercel com SQLite Cloud...")

# Obter a string de conexão do ambiente ou usar o padrão
connection_string = os.environ.get(
    'SQLITECLOUD_CONNECTION_STRING', 
    "sqlitecloud://cixo5xlahz.g2.sqlite.cloud:8860/db.sqlite3?apikey=MqpRdbbYgBSYzHjjMHWUjnbAPkuNQ7bInQkxkw2bHbg"
)

try:
    # Conectar ao SQLite Cloud
    print(f"Conectando ao SQLite Cloud: {connection_string}")
    conn = sqlitecloud.connect(connection_string)
    cursor = conn.cursor()
    
    # Verificar se a tabela django_content_type existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_content_type'")
    content_type_exists = cursor.fetchone() is not None
    
    if not content_type_exists:
        print("Tabela django_content_type não encontrada. Criando...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS django_content_type (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_label VARCHAR(100) NOT NULL,
            model VARCHAR(100) NOT NULL,
            CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model)
        )
        """)
        
        # Inserir tipos de conteúdo essenciais para o admin
        content_types = [
            ('contenttypes', 'contenttype'),
            ('auth', 'permission'),
            ('auth', 'group'),
            ('auth', 'user'),
            ('admin', 'logentry'),
            ('sessions', 'session'),
            ('agenda', 'agenda'),
            ('agenda', 'genero'),
            ('agenda', 'faixa_etaria')
        ]
        
        for app_label, model in content_types:
            cursor.execute(
                "INSERT OR IGNORE INTO django_content_type (app_label, model) VALUES (?, ?)",
                (app_label, model)
            )
        
        conn.commit()
        print("ContentTypes criados com sucesso!")
    else:
        print("Tabela django_content_type já existe.")
        
        # Verificar se tem os types para a app agenda
        cursor.execute("SELECT id FROM django_content_type WHERE app_label='agenda' AND model='agenda'")
        agenda_type = cursor.fetchone()
        
        if not agenda_type:
            print("Inserindo content types para a app agenda...")
            types_to_add = [
                ('agenda', 'agenda'),
                ('agenda', 'genero'),
                ('agenda', 'faixa_etaria')
            ]
            
            for app_label, model in types_to_add:
                cursor.execute(
                    "INSERT OR IGNORE INTO django_content_type (app_label, model) VALUES (?, ?)",
                    (app_label, model)
                )
            
            conn.commit()
            print("Content types da agenda adicionados!")
    
    # Verificar quais content types existem
    cursor.execute("SELECT id, app_label, model FROM django_content_type")
    content_types = cursor.fetchall()
    print("\nContentTypes disponíveis:")
    for ct in content_types:
        print(f"ID: {ct[0]}, App: {ct[1]}, Model: {ct[2]}")
        
    # Fechar conexão
    conn.close()
    print("\nSetup do SQLite Cloud concluído com sucesso!")
    
except Exception as e:
    print(f"Erro durante o setup: {e}")
    sys.exit(1) 