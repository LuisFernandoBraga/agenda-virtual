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
    
    # === Verificar e criar Tabelas Essenciais ===
    
    # 1. Verificar se a tabela django_content_type existe
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
    
    # 2. Verificar se as tabelas agenda_genero e agenda_faixa_etaria existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agenda_genero'")
    genero_exists = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agenda_faixa_etaria'")
    faixa_etaria_exists = cursor.fetchone() is not None
    
    # Verificar se a tabela auth_user existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user'")
    auth_user_exists = cursor.fetchone() is not None
    
    # Criar tabela auth_user se não existir
    if not auth_user_exists:
        print("Criando tabela auth_user...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password VARCHAR(128) NOT NULL,
            last_login DATETIME NULL,
            is_superuser BOOLEAN NOT NULL,
            username VARCHAR(150) NOT NULL UNIQUE,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            email VARCHAR(254) NOT NULL,
            is_staff BOOLEAN NOT NULL,
            is_active BOOLEAN NOT NULL,
            date_joined DATETIME NOT NULL
        )
        """)
        
        # Adicionar usuário admin padrão
        from datetime import datetime
        import hashlib
        import base64
        
        # Hash simples para 'admin123' - em produção usar algo mais seguro
        hashed_password = "pbkdf2_sha256$720000$salt$hashedpassword"
        now = datetime.now().isoformat()
        
        cursor.execute("""
        INSERT INTO auth_user (
            password, last_login, is_superuser, username, 
            first_name, last_name, email, is_staff, 
            is_active, date_joined
        ) VALUES (?, NULL, 1, 'admin', 'Admin', 'User', 'admin@example.com', 1, 1, ?)
        """, (hashed_password, now))
        
        conn.commit()
        print("Tabela auth_user criada e admin padrão adicionado com sucesso!")
    else:
        print("Tabela auth_user já existe.")
        
        # Verificar se tem pelo menos um usuário admin
        cursor.execute("SELECT COUNT(*) FROM auth_user WHERE is_staff = 1")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("Nenhum admin encontrado. Adicionando admin padrão...")
            from datetime import datetime
            
            # Hash simples para 'admin123'
            hashed_password = "pbkdf2_sha256$720000$salt$hashedpassword"
            now = datetime.now().isoformat()
            
            cursor.execute("""
            INSERT INTO auth_user (
                password, last_login, is_superuser, username, 
                first_name, last_name, email, is_staff, 
                is_active, date_joined
            ) VALUES (?, NULL, 1, 'admin', 'Admin', 'User', 'admin@example.com', 1, 1, ?)
            """, (hashed_password, now))
            
            conn.commit()
            print("Admin padrão adicionado com sucesso!")
    
    # Criar tabela agenda_genero se não existir
    if not genero_exists:
        print("Criando tabela agenda_genero...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda_genero (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL
        )
        """)
        
        # Adicionar valores padrão
        generos = ['Masculino', 'Feminino', 'Não-binário', 'Outro']
        for genero in generos:
            cursor.execute("INSERT INTO agenda_genero (nome) VALUES (?)", (genero,))
        
        conn.commit()
        print("Tabela agenda_genero criada e populada com sucesso!")
    else:
        print("Tabela agenda_genero já existe.")
        
        # Verificar se tem dados
        cursor.execute("SELECT COUNT(*) FROM agenda_genero")
        genero_count = cursor.fetchone()[0]
        
        if genero_count == 0:
            print("Populando agenda_genero com valores padrão...")
            generos = ['Masculino', 'Feminino', 'Não-binário', 'Outro']
            for genero in generos:
                cursor.execute("INSERT INTO agenda_genero (nome) VALUES (?)", (genero,))
            
            conn.commit()
            print("Dados de gênero inseridos com sucesso!")
    
    # Criar tabela agenda_faixa_etaria se não existir
    if not faixa_etaria_exists:
        print("Criando tabela agenda_faixa_etaria...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda_faixa_etaria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL
        )
        """)
        
        # Adicionar valores padrão
        faixas = ['Criança (0-12)', 'Adolescente (13-17)', 'Adulto (18-59)', 'Idoso (60+)']
        for faixa in faixas:
            cursor.execute("INSERT INTO agenda_faixa_etaria (nome) VALUES (?)", (faixa,))
        
        conn.commit()
        print("Tabela agenda_faixa_etaria criada e populada com sucesso!")
    else:
        print("Tabela agenda_faixa_etaria já existe.")
        
        # Verificar se tem dados
        cursor.execute("SELECT COUNT(*) FROM agenda_faixa_etaria")
        faixa_count = cursor.fetchone()[0]
        
        if faixa_count == 0:
            print("Populando agenda_faixa_etaria com valores padrão...")
            faixas = ['Criança (0-12)', 'Adolescente (13-17)', 'Adulto (18-59)', 'Idoso (60+)']
            for faixa in faixas:
                cursor.execute("INSERT INTO agenda_faixa_etaria (nome) VALUES (?)", (faixa,))
            
            conn.commit()
            print("Dados de faixa etária inseridos com sucesso!")
    
    # Verificar quais content types existem
    cursor.execute("SELECT id, app_label, model FROM django_content_type")
    content_types = cursor.fetchall()
    print("\nContentTypes disponíveis:")
    for ct in content_types:
        print(f"ID: {ct[0]}, App: {ct[1]}, Model: {ct[2]}")
        
    # Verificar gêneros disponíveis
    cursor.execute("SELECT id, nome FROM agenda_genero")
    generos = cursor.fetchall()
    print("\nGêneros disponíveis:")
    for g in generos:
        print(f"ID: {g[0]}, Nome: {g[1]}")
        
    # Verificar faixas etárias disponíveis
    cursor.execute("SELECT id, nome FROM agenda_faixa_etaria")
    faixas = cursor.fetchall()
    print("\nFaixas etárias disponíveis:")
    for f in faixas:
        print(f"ID: {f[0]}, Nome: {f[1]}")
        
    # Verificar se a tabela agenda_agenda existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agenda_agenda'")
    agenda_agenda_exists = cursor.fetchone() is not None
    
    # Criar tabela agenda_agenda se não existir
    if not agenda_agenda_exists:
        print("Criando tabela agenda_agenda...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda_agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        )
        """)
        
        conn.commit()
        print("Tabela agenda_agenda criada com sucesso!")
    else:
        print("Tabela agenda_agenda já existe.")
    
    # Verificar se a tabela auth_permission existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_permission'")
    auth_permission_exists = cursor.fetchone() is not None
    
    # Criar tabela auth_permission se não existir
    if not auth_permission_exists:
        print("Criando tabela auth_permission...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_permission (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            content_type_id INTEGER NOT NULL,
            codename VARCHAR(100) NOT NULL,
            CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename),
            FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
        )
        """)
        
        conn.commit()
        print("Tabela auth_permission criada com sucesso!")
    else:
        print("Tabela auth_permission já existe.")
    
    # Verificar se a tabela auth_group existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_group'")
    auth_group_exists = cursor.fetchone() is not None
    
    # Criar tabela auth_group se não existir
    if not auth_group_exists:
        print("Criando tabela auth_group...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_group (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(150) NOT NULL UNIQUE
        )
        """)
        
        conn.commit()
        print("Tabela auth_group criada com sucesso!")
    else:
        print("Tabela auth_group já existe.")
    
    # Verificar se a tabela auth_group_permissions existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_group_permissions'")
    auth_group_permissions_exists = cursor.fetchone() is not None
    
    # Criar tabela auth_group_permissions se não existir
    if not auth_group_permissions_exists:
        print("Criando tabela auth_group_permissions...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_group_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id),
            FOREIGN KEY (group_id) REFERENCES auth_group (id),
            FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
        )
        """)
        
        conn.commit()
        print("Tabela auth_group_permissions criada com sucesso!")
    else:
        print("Tabela auth_group_permissions já existe.")
    
    # Verificar se a tabela auth_user_groups existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user_groups'")
    auth_user_groups_exists = cursor.fetchone() is not None
    
    # Criar tabela auth_user_groups se não existir
    if not auth_user_groups_exists:
        print("Criando tabela auth_user_groups...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_user_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id),
            FOREIGN KEY (user_id) REFERENCES auth_user (id),
            FOREIGN KEY (group_id) REFERENCES auth_group (id)
        )
        """)
        
        conn.commit()
        print("Tabela auth_user_groups criada com sucesso!")
    else:
        print("Tabela auth_user_groups já existe.")
    
    # Verificar se a tabela auth_user_user_permissions existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auth_user_user_permissions'")
    auth_user_user_permissions_exists = cursor.fetchone() is not None
    
    # Criar tabela auth_user_user_permissions se não existir
    if not auth_user_user_permissions_exists:
        print("Criando tabela auth_user_user_permissions...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id),
            FOREIGN KEY (user_id) REFERENCES auth_user (id),
            FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
        )
        """)
        
        conn.commit()
        print("Tabela auth_user_user_permissions criada com sucesso!")
    else:
        print("Tabela auth_user_user_permissions já existe.")
    
    # Fechar conexão
    conn.close()
    print("\nSetup do SQLite Cloud concluído com sucesso!")
    
except Exception as e:
    print(f"Erro durante o setup: {e}")
    sys.exit(1) 