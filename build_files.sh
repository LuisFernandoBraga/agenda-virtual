#!/bin/bash
# Build script para Vercel

# Usar o Python do ambiente Vercel
export PATH="$VERCEL_PYTHON_PATH:$PATH"

# Mostrar versões para debug
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current directory: $(pwd)"
echo "Directory listing: $(ls -la)"

# Instalar dependências
python -m pip install --upgrade pip
pip install -r requirements.txt

# Executar script de debug
echo "Executing debug script..."
python scripts/debug_vercel.py

# Criar diretório de saída staticfiles
mkdir -p staticfiles

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

# Garantir que o diretório staticfiles existe e não está vazio
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles)" ]; then
    echo "Criando arquivo placeholder em staticfiles"
    mkdir -p staticfiles
    echo "Placeholder file for Vercel build" > staticfiles/placeholder.txt
fi

echo "Conteúdo do diretório staticfiles:"
ls -la staticfiles/

echo "Build script executado com sucesso!" 