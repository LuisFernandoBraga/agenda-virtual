# Agenda Virtual

Sistema de agendamento desenvolvido com Django.

## Instalação Local

1. Clone o repositório
   ```
   git clone https://github.com/seu-usuario/agenda-virtual.git
   cd agenda-virtual
   ```

2. Crie um ambiente virtual
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências
   ```
   pip install -r requirements.txt
   ```

4. Configure o banco de dados
   ```
   python manage.py migrate
   ```

5. Execute o servidor
   ```
   python manage.py runserver
   ```

## Deploy na Vercel

Este projeto está configurado para deploy na Vercel com SQLite Cloud.

### Pré-requisitos

- Conta na Vercel
- Conta no SQLite Cloud

### Configuração da Vercel

1. Importe o repositório na Vercel

2. Configure as seguintes variáveis de ambiente:
   - `DJANGO_SECRET_KEY`: Chave secreta para o Django
   - `DEBUG`: False
   - `VERCEL`: 1
   - `SQLITECLOUD_ENABLED`: True
   - `SQLITECLOUD_CONNECTION_STRING`: Sua string de conexão do SQLite Cloud

### SQLite Cloud

O projeto usa SQLite Cloud como banco de dados na Vercel. Durante o build, um script automatizado criará as tabelas e populará o banco com dados iniciais.

Para desenvolvimento local, o projeto usa MySQL. Você pode habilitar o SQLite Cloud localmente definindo a variável de ambiente `SQLITECLOUD_ENABLED=True`.

## Estrutura do Projeto

- `agenda/`: Aplicação principal
- `project/`: Configurações do projeto
- `scripts/`: Scripts utilitários
- `static/`, `media/`: Arquivos estáticos e uploads 