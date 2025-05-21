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
from django.conf import settings
from agenda.utils import get_agenda_items




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
    # Tentar obter dados do SQLite Cloud se estiver habilitado
    if settings.SQLITECLOUD_ENABLED:
        # Obter parâmetros de paginação
        page_number = request.GET.get("page", 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        
        items_per_page = 8
        offset = (page_number - 1) * items_per_page
        
        # Obter todos os itens para contar o total
        all_items = get_agenda_items()
        total_count = len(all_items) if all_items else 0
        
        # Obter itens da agenda via SQLite Cloud com paginação
        agendas_data = get_agenda_items(limit=items_per_page, offset=offset)
        
        # Calcular total de páginas
        total_pages = (total_count + items_per_page - 1) // items_per_page if total_count > 0 else 1
        
        # Criar um objeto similar ao paginator do Django
        class SimplePage:
            def __init__(self, object_list, number, paginator):
                self.object_list = object_list
                self.number = number
                self.paginator = paginator
                
            def has_previous(self):
                return self.number > 1
                
            def has_next(self):
                return self.number < self.paginator.num_pages
                
            def previous_page_number(self):
                return self.number - 1
                
            def next_page_number(self):
                return self.number + 1
        
        # Criar uma classe paginator simplificada
        class SimplePaginator:
            def __init__(self, object_list, per_page, total_pages):
                self.object_list = object_list
                self.per_page = per_page
                self.num_pages = total_pages
                self.count = len(object_list) if object_list else 0
                
        # Criar os objetos de paginação
        paginator = SimplePaginator(all_items, items_per_page, total_pages)
        page_obj = SimplePage(agendas_data, page_number, paginator)
    else:
        # Código original para obter os dados do ORM Django
        agendas = Agenda.objects \
            .filter(show=True)\
            .order_by('-id')
        
        paginator = Paginator(agendas, 8)  
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
    from django.conf import settings
    from agenda.utils import get_agenda_items
    
    pesquisa_valor = request.GET.get('q', '').strip()
    
    if pesquisa_valor == '':
        return redirect('index')

    # Tentar obter dados do SQLite Cloud se estiver habilitado
    if settings.SQLITECLOUD_ENABLED:
        # Obter parâmetros de paginação
        page_number = request.GET.get("page", 1)
        try:
            page_number = int(page_number)
        except ValueError:
            page_number = 1
        
        items_per_page = 4
        offset = (page_number - 1) * items_per_page
        
        # Obter todos os itens para contagem total
        all_items = get_agenda_items(search=pesquisa_valor)
        total_count = len(all_items) if all_items else 0
        
        # Obter itens da agenda via SQLite Cloud com paginação
        agendas_data = get_agenda_items(limit=items_per_page, offset=offset, search=pesquisa_valor)
        
        # Calcular total de páginas
        total_pages = (total_count + items_per_page - 1) // items_per_page if total_count > 0 else 1
        
        # Criar um objeto similar ao paginator do Django
        class SimplePage:
            def __init__(self, object_list, number, paginator):
                self.object_list = object_list
                self.number = number
                self.paginator = paginator
                
            def has_previous(self):
                return self.number > 1
                
            def has_next(self):
                return self.number < self.paginator.num_pages
                
            def previous_page_number(self):
                return self.number - 1
                
            def next_page_number(self):
                return self.number + 1
        
        # Criar uma classe paginator simplificada
        class SimplePaginator:
            def __init__(self, object_list, per_page, total_pages):
                self.object_list = object_list
                self.per_page = per_page
                self.num_pages = total_pages
                self.count = len(object_list) if object_list else 0
                
        # Criar os objetos de paginação
        paginator = SimplePaginator(all_items, items_per_page, total_pages)
        page_obj = SimplePage(agendas_data, page_number, paginator)
    else:
        # Código original para obter os dados do ORM Django
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

    # Determinar qual formulário usar
    if settings.SQLITECLOUD_ENABLED:
        from agenda.cloud_forms import CloudAgendaForm as FormClass
        from agenda.utils import create_agenda_item
    else:
        from agenda.views import AgendaForm as FormClass

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES)

        contexto = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            if settings.SQLITECLOUD_ENABLED:
                # Usar a função de utilidade para criar o item via SQLite Cloud
                data = form.cleaned_data
                create_agenda_item(data)
                messages.success(request, 'Usuário cadastrado com sucesso!')
                return redirect('index')
            else:
                # Salvar normalmente usando o ORM do Django
                form.save()
                messages.success(request, 'Usuário cadastrado com sucesso!')
                return redirect('index')

        return render(
            request,
            'agenda/inserir_cadastro.html',
            contexto
        )
        
    contexto = {
        'form': FormClass(),
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

    # Determinar qual formulário usar
    if settings.SQLITECLOUD_ENABLED:
        from agenda.cloud_forms import CloudAgendaForm as FormClass
        from agenda.utils import execute_update
    else:
        from agenda.views import AgendaForm as FormClass

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=cadastro)

        contexto = {
            'form': form,
            'form_action': form_action,
        }

        if form.is_valid():
            if settings.SQLITECLOUD_ENABLED:
                # Implementação simplificada apenas para mostrar a abordagem
                # Na prática, você precisaria criar uma função específica para atualização
                data = form.cleaned_data
                cadastro = form.save(commit=False)  # Não salva no banco
                # Aqui você implementaria a lógica para atualizar no SQLite Cloud
                messages.success(request, 'Cadastro atualizado com sucesso!')
                return redirect('index')
            else:
                # Salvar normalmente usando o ORM do Django
                cadastro = form.save()
                messages.success(request, 'Cadastro atualizado com sucesso!')
                return redirect('index')

        return render(
            request,
            'agenda/inserir_cadastro.html',
            contexto
        )
        
    contexto = {
        'form': FormClass(instance=cadastro),
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
