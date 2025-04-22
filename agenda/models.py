from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Genero(models.Model):
    class Meta:
        verbose_name = 'Gênero'
        verbose_name_plural = 'Gêneros'

    nome = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return self.nome
    
class Faixa_Etaria(models.Model):
    class Meta:
        verbose_name = 'Faixa Etária'
        verbose_name_plural = 'Faixa Etárias'

    nome = models.CharField(max_length=100)
    
    def __str__(self) -> str:
        return self.nome    

class Agenda(models.Model):
    class Meta:
        verbose_name = 'Agendamento'
        verbose_name_plural = 'Agendamentos'

    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100, blank=True)
    cpf = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True)
    contato = models.CharField(max_length=50)
    descricao_servico = models.TextField(max_length=500)
    data_hora = models.DateTimeField(default=timezone.now)
    valor = models.CharField(max_length=50)
    show = models.BooleanField(default=True)
    imagem = models.ImageField(blank=True, upload_to='imagens/%y/%m/')
    genero = models.ForeignKey(
        Genero, 
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    faixa_etaria = models.ForeignKey(
        Faixa_Etaria, 
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    '''proprietario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        blank=True, null=True
    )'''
    
def __str__(self) -> str:
    return f'{self.name} {self.sobrenome}'
