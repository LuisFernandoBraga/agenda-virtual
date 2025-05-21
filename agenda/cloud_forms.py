"""
Formulários adaptados para o SQLite Cloud.
"""
from django import forms
from django.conf import settings
from agenda.models import Agenda
from agenda.cloud_db import execute_query

class CloudAgendaForm(forms.Form):
    """Versão do AgendaForm que funciona com SQLite Cloud.
    Usa Form em vez de ModelForm para evitar a validação com ORM."""
    
    # Campos padrão
    imagem = forms.ImageField(
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'image/*'
            }
        )
    )
    nome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Digite o nome do(a) cliente: ', 
            }
        )
    )
    sobrenome = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Digite o sobrenome do(a) cliente: ',
            }
        )
    )
    cpf = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Digite o CPF do(a) cliente: ',
            }
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'Digite o email do(a) cliente: ',
            }
        )
    )
    contato = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Digite o contato do(a) cliente: ',
            }
        )
    )
    descricao_servico = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Digite a descrição do serviço a ser:  ',
            }
        )
    )
    valor = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder': 'Digite o valor do serviço: ',
            }
        )
    )
    data_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
            }
        )
    )
    
    # Campos de chave estrangeira adaptados para o SQLite Cloud
    genero = forms.ChoiceField(choices=[], required=False)
    faixa_etaria = forms.ChoiceField(choices=[], required=False)
    
    def __init__(self, *args, **kwargs):
        # Remover instance para evitar conflito com Form (vs ModelForm)
        self.instance = kwargs.pop('instance', None)
        
        super().__init__(*args, **kwargs)
        
        # Preencher o formulário com os dados da instância, se fornecida
        if self.instance:
            for field_name in self.fields:
                if hasattr(self.instance, field_name):
                    field_value = getattr(self.instance, field_name)
                    # Para ForeignKeys, obter o ID
                    if field_name in ['genero', 'faixa_etaria'] and field_value:
                        self.initial[field_name] = str(field_value.id)
                    else:
                        self.initial[field_name] = field_value
        
        # Se o SQLite Cloud estiver habilitado, preenchemos as opções dos campos de seleção
        if settings.SQLITECLOUD_ENABLED:
            # Obter opções de gênero do SQLite Cloud
            generos = execute_query("SELECT id, nome FROM agenda_genero ORDER BY nome")
            genero_choices = [(str(g[0]), g[1]) for g in generos] if generos else []
            genero_choices.insert(0, ('', '---------'))  # Opção vazia
            self.fields['genero'].choices = genero_choices
            
            # Obter opções de faixa etária do SQLite Cloud
            faixas = execute_query("SELECT id, nome FROM agenda_faixa_etaria ORDER BY nome")
            faixa_choices = [(str(f[0]), f[1]) for f in faixas] if faixas else []
            faixa_choices.insert(0, ('', '---------'))  # Opção vazia
            self.fields['faixa_etaria'].choices = faixa_choices
    
    def save(self, commit=True):
        """
        Método de compatibilidade para permitir o mesmo comportamento de ModelForm.
        """
        if not settings.SQLITECLOUD_ENABLED:
            raise NotImplementedError("Este método só deve ser chamado em ambiente SQLite Cloud")
        
        # No SQLite Cloud, não fazemos nada aqui - apenas retornamos um dicionário de dados
        return self.cleaned_data 