"""
Session backend personalizado que armazena os dados em cookies.
Isso evita a dependência de tabelas no banco de dados.
"""
from django.contrib.sessions.backends.signed_cookies import SessionStore as CookieStore

class VercelSessionStore(CookieStore):
    """
    Implementação de sessão baseada em cookies para ambiente Vercel.
    Sobrescreve alguns métodos para evitar chamadas ao banco de dados.
    """
    
    def exists(self, session_key):
        """
        Retorna sempre True para evitar verificações no banco de dados.
        """
        return True
    
    def create(self):
        """
        Cria uma nova sessão sem depender do banco de dados.
        """
        self._session_key = self._get_new_session_key()
        self._session_cache = {}
        self.modified = True
        self._session = self._session_cache
        
    def save(self, must_create=False):
        """
        Salva a sessão no cookie, ignorando o parâmetro must_create.
        """
        super().save(False)
        
    def delete(self, session_key=None):
        """
        Não faz nada ao excluir, já que não há tabela no banco.
        """
        self._session_cache = {}
        self.modified = True
        self._session_key = None 