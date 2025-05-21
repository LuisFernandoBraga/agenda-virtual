#!/bin/bash
# Build script para Vercel

# Instalar dependências
pip install -r requirements.txt

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Criar pasta media se não existir
mkdir -p media

# Criar e popular tabelas no SQLite Cloud se estiver em ambiente Vercel
if [ "$VERCEL" = "1" ]; then
    echo "Criando e populando tabelas no SQLite Cloud..."
    python scripts/populate_sqlitecloud.py
fi

# Crie um .gitignore específico para a Vercel
if [ ! -f .vercelignore ]; then
    echo "venv" >> .vercelignore
    echo "__pycache__" >> .vercelignore
    echo "db.sqlite3" >> .vercelignore
fi

echo "Build script executado com sucesso!" 