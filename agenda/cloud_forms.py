"""
Formulários adaptados para o SQLite Cloud.
"""
from django import forms
from django.conf import settings
from agenda.models import Agenda
from agenda.cloud_db import execute_query
import logging

logger = logging.getLogger(__name__)

class CloudModelChoiceField(forms.ChoiceField):
    """
    A version of ModelChoiceField that fetches choices from SQLite Cloud.
    """
    def __init__(self, table_name, value_field='id', label_field='nome', empty_label="---------", *args, **kwargs):
        self.table_name = table_name
        self.value_field = value_field
        self.label_field = label_field
        
        # Get choices from SQLite Cloud
        choices = self.get_cloud_choices()
        
        # Add empty choice if requested
        if empty_label is not None:
            choices = [(None, empty_label)] + choices
            
        super().__init__(choices=choices, *args, **kwargs)
    
    def get_cloud_choices(self):
        try:
            query = f"SELECT {self.value_field}, {self.label_field} FROM {self.table_name} ORDER BY {self.label_field}"
            results = execute_query(query)
            
            # Convert results to choices format
            choices = [(str(item[0]), item[1]) for item in results] if results else []
            
            logger.info(f"CloudModelChoiceField: Got {len(choices)} choices for {self.table_name}")
            
            return choices
        except Exception as e:
            logger.error(f"Error fetching choices from SQLite Cloud for {self.table_name}: {e}")
            return []

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
    genero = CloudModelChoiceField(table_name='agenda_genero', required=False)
    faixa_etaria = CloudModelChoiceField(table_name='agenda_faixa_etaria', required=False)
    
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
    
    def save(self, commit=True):
        """
        Método de compatibilidade para permitir o mesmo comportamento de ModelForm.
        """
        if not settings.SQLITECLOUD_ENABLED:
            raise NotImplementedError("Este método só deve ser chamado em ambiente SQLite Cloud")
        
        # No SQLite Cloud, não fazemos nada aqui - apenas retornamos um dicionário de dados
        return self.cleaned_data 