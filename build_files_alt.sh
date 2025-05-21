#!/bin/bash
# Script alternativo para build na Vercel que tenta encontrar o Python

# Identificar o caminho do Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "Usando python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "Usando python"
else
    echo "Python não encontrado"
    # Tentar encontrar Python em caminhos comuns da Vercel
    for path in /opt/vercel/python/bin/python /opt/python/bin/python /usr/bin/python3 /usr/bin/python
    do
        if [ -x "$path" ]; then
            PYTHON_CMD="$path"
            echo "Encontrado Python em: $path"
            break
        fi
    done
fi

# Se ainda não encontrou, abortar
if [ -z "$PYTHON_CMD" ]; then
    echo "Python não encontrado. Abortando."
    exit 1
fi

echo "Python command: $PYTHON_CMD"
echo "Python version: $($PYTHON_CMD --version)"

# Identificar o caminho do pip
if command -v pip3 &> /dev/null; then
    PIP_CMD=pip3
    echo "Usando pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD=pip
    echo "Usando pip"
else
    # Usar pip através do Python
    PIP_CMD="$PYTHON_CMD -m pip"
    echo "Usando $PIP_CMD"
fi

echo "Current directory: $(pwd)"
echo "Directory listing: $(ls -la)"

# Instalar dependências
$PIP_CMD install --upgrade pip
echo "Instalando apenas o SQLite Cloud para configuração inicial..."
$PIP_CMD install sqlitecloud

# Configurar o SQLite Cloud diretamente
if [ "$VERCEL" = "1" ]; then
    echo "Configurando o SQLite Cloud com script simplificado..."
    $PYTHON_CMD scripts/vercel_setup.py
fi

# Agora instalar o resto das dependências
echo "Instalando dependências da Vercel (sem mysqlclient)..."
$PIP_CMD install -r requirements-vercel.txt

# Criar diretório de saída staticfiles
mkdir -p staticfiles

# Coletar arquivos estáticos
$PYTHON_CMD manage.py collectstatic --noinput || {
    echo "Erro ao coletar arquivos estáticos, continuando mesmo assim..."
}

# Criar pasta media se não existir
mkdir -p media

# Garantir que o diretório staticfiles existe e não está vazio
if [ ! -d "staticfiles" ] || [ -z "$(ls -A staticfiles)" ]; then
    echo "Criando arquivo placeholder em staticfiles"
    mkdir -p staticfiles
    echo "Placeholder file for Vercel build" > staticfiles/placeholder.txt
fi

echo "Conteúdo do diretório staticfiles:"
ls -la staticfiles/

echo "Build script alternativo executado com sucesso!" 