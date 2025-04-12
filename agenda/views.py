# type: ignore
from django.shortcuts import render, redirect, get_object_or_404
from agenda.models import Agenda
from django.db.models import Q
from django.core.paginator import Paginator
from django import forms
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages




class AgendaForm(forms.ModelForm):
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

    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


    class Meta:
        model = Agenda
        fields = (
            'nome', 'sobrenome', 'cpf', 'email', 'contato', 
            'descricao_servico', 'data_hora', 'valor', 
            'genero', 'faixa_etaria', 'imagem', 
        )

def index(request, methods=["GET", "POST"]):
    agendas = Agenda.objects \
        .filter(show=True)\
        .order_by('-id')
    
    paginator = Paginator(agendas, 4)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
        'site_title': 'Área do Profissional - '
    }

    
    return render(
        request, 
        'agenda/index.html', 
        contexto
    )

def cadastro(request, cadastro_id):
    inserir_cadastro = Agenda.objects.get(pk=cadastro_id)
        
    contexto = {
        'cadastro':inserir_cadastro ,
        'site_title': 'Cadastro - '
    }
    return render(
        request,
        'agenda/cadastro.html',
        contexto
    )

def pesquisa(request):
    
    pesquisa_valor = request.GET.get('q', '').strip()
    
    if pesquisa_valor == '':
        return redirect('index')

    agendas = Agenda.objects \
        .filter(show=True)\
        .filter(
            Q(nome__icontains=pesquisa_valor) |
            Q(sobrenome__icontains=pesquisa_valor) |
            Q(data_hora__icontains=pesquisa_valor)
        )\
        .order_by('-id')
    
    paginator = Paginator(agendas, 4)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    contexto = {
        'page_obj': page_obj,
        'site_title': 'Pesquisa - ',
        'pesquisa_valor': pesquisa_valor,
    }

    
    return render(
        request, 
        'agenda/index.html', 
        contexto
    )

def inserir_cadastro(request):    
    form_action = reverse('inserir_cadastro')

    if request.method == 'POST':
        form = AgendaForm(request.POST, request.FILES)

        contexto = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('index')

        return render(
            request,
            'agenda/inserir_cadastro.html',
            contexto
        )
        
    contexto = {
        'form': AgendaForm(),
        'form_action': form_action,
    }
    return render(
        request,
        'agenda/inserir_cadastro.html',
        contexto
    )

def atualiza(request, cadastro_id):
    cadastro = get_object_or_404(Agenda, pk=cadastro_id, show=True)
    form_action = reverse('atualiza', args=(cadastro_id,))

    if request.method == 'POST':
        form = AgendaForm(request.POST, request.FILES, instance=cadastro)

        contexto = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            cadastro = form.save()
            messages.success(request, 'Cadastro atualizado com sucesso!')
            return redirect('index')

        return render(
            request,
            'agenda/inserir_cadastro.html',
            contexto
        )
        
    contexto = {
        'form': AgendaForm(instance=cadastro),
        'form_action': form_action,
    }
    return render(
        request,
        'agenda/inserir_cadastro.html',
        contexto
    )

def excluir(request, cadastro_id):
    cadastro = get_object_or_404(Agenda, pk=cadastro_id, show=True)

    cadastro.delete()
    messages.warning(request, 'Cadastro excluído com sucesso!')
    
    return redirect(
       'index'
    )

class RegistroForm(UserCreationForm):
    nome = forms.CharField(
        required=True,
        min_length=3
    )
    sobrenome = forms.CharField(
        required=True,
        min_length=3
    )
    email = forms.EmailField(
            error_messages={
            'required': 'Email inválido'
        }
    )




    class Meta:
        model = User
        fields = (
            'nome', 'sobrenome', 'email',
            'username', 'password1', 'password2',
        )
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            self.add_error(
                'email',
                ValidationError('Email já existe, por favor insira outro email!', code='invalid')
            )

        return email


def registro(request):
    form = RegistroForm()

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('index')
        
    return render(
        request, 
        'agenda/registro.html',
        {
            'form': form
        } 
    )
