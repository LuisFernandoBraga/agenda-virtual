from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Agenda, Genero, Faixa_Etaria
from django.contrib.auth.models import User

class GeneroModelTest(TestCase):
    def setUp(self):
        self.genero = Genero.objects.create(nome='Masculino')
    
    def test_genero_str(self):
        self.assertEqual(str(self.genero), 'Masculino')
        
    def test_genero_nome_max_length(self):
        max_length = self.genero._meta.get_field('nome').max_length
        self.assertEqual(max_length, 100)

class FaixaEtariaModelTest(TestCase):
    def setUp(self):
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
    
    def test_faixa_etaria_str(self):
        self.assertEqual(str(self.faixa_etaria), 'Adulto')
        
    def test_faixa_etaria_nome_max_length(self):
        max_length = self.faixa_etaria._meta.get_field('nome').max_length
        self.assertEqual(max_length, 100)

class AgendaModelTest(TestCase):
    def setUp(self):
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        self.agenda = Agenda.objects.create(
            nome='João',
            sobrenome='Silva',
            cpf='123.456.789-10',
            email='joao@example.com',
            contato='(11) 98765-4321',
            descricao_servico='Corte de cabelo',
            data_hora=timezone.now(),
            valor='50,00',
            genero=self.genero,
            faixa_etaria=self.faixa_etaria
        )
    
    def test_agenda_str(self):
        self.assertEqual(str(self.agenda), 'João Silva')
        
    def test_agenda_nome_max_length(self):
        max_length = self.agenda._meta.get_field('nome').max_length
        self.assertEqual(max_length, 100)
        
    def test_agenda_defaults(self):
        self.assertTrue(self.agenda.show)
        self.assertIsNotNone(self.agenda.data_hora)

class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        
        # Criar vários agendamentos para testar paginação
        for i in range(10):
            Agenda.objects.create(
                nome=f'Cliente {i}',
                sobrenome='Teste',
                contato='12345678',
                descricao_servico='Teste de serviço',
                valor='50,00',
                genero=self.genero,
                faixa_etaria=self.faixa_etaria
            )
    
    def test_index_view_status_code(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        
    def test_index_view_template(self):
        response = self.client.get(reverse('index'))
        self.assertTemplateUsed(response, 'agenda/index.html')
        
    def test_index_view_paginator(self):
        response = self.client.get(reverse('index'))
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['page_obj']), 8)  # 8 itens por página

class PesquisaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        
        # Criar agendamentos com nomes específicos para teste
        Agenda.objects.create(
            nome='Maria',
            sobrenome='Silva',
            contato='12345678',
            descricao_servico='Teste de serviço',
            valor='50,00',
            genero=self.genero,
            faixa_etaria=self.faixa_etaria
        )
        
        Agenda.objects.create(
            nome='João',
            sobrenome='Silva',
            contato='12345678',
            descricao_servico='Teste de serviço',
            valor='50,00',
            genero=self.genero,
            faixa_etaria=self.faixa_etaria
        )
    
    def test_pesquisa_redirect_empty_query(self):
        response = self.client.get(reverse('pesquisa'), {'q': ''})
        self.assertRedirects(response, reverse('index'))
        
    def test_pesquisa_results(self):
        response = self.client.get(reverse('pesquisa'), {'q': 'Maria'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
        
    def test_pesquisa_no_results(self):
        response = self.client.get(reverse('pesquisa'), {'q': 'NomeInexistente'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 0)

class CadastroViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        self.agenda = Agenda.objects.create(
            nome='Cliente',
            sobrenome='Teste',
            contato='12345678',
            descricao_servico='Teste de serviço',
            valor='50,00',
            genero=self.genero,
            faixa_etaria=self.faixa_etaria
        )
    
    def test_cadastro_view(self):
        response = self.client.get(reverse('cadastro', args=[self.agenda.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/cadastro.html')
        self.assertEqual(response.context['cadastro'], self.agenda)

class InserirCadastroViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        
    def test_inserir_cadastro_get(self):
        response = self.client.get(reverse('inserir_cadastro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/inserir_cadastro.html')
        
    def test_inserir_cadastro_post_valid(self):
        data = {
            'nome': 'Novo',
            'sobrenome': 'Cliente',
            'cpf': '123.456.789-00',
            'email': 'novo@example.com',
            'contato': '987654321',
            'descricao_servico': 'Teste de inserção',
            'data_hora': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'valor': '75,00',
            'genero': self.genero.id,
            'faixa_etaria': self.faixa_etaria.id
        }
        
        response = self.client.post(reverse('inserir_cadastro'), data)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Agenda.objects.count(), 1)

class AtualizaViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        self.agenda = Agenda.objects.create(
            nome='Cliente',
            sobrenome='Antigo',
            cpf='123.456.789-00',
            email='antigo@example.com',
            contato='12345678',
            descricao_servico='Descrição antiga',
            valor='50,00',
            genero=self.genero,
            faixa_etaria=self.faixa_etaria
        )
    
    def test_atualiza_get(self):
        response = self.client.get(reverse('atualiza', args=[self.agenda.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/inserir_cadastro.html')
        
    def test_atualiza_post_valid(self):
        data = {
            'nome': 'Cliente',
            'sobrenome': 'Atualizado',
            'cpf': '123.456.789-00',
            'email': 'atualizado@example.com',
            'contato': '87654321',
            'descricao_servico': 'Descrição atualizada',
            'data_hora': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'valor': '75,00',
            'genero': self.genero.id,
            'faixa_etaria': self.faixa_etaria.id
        }
        
        response = self.client.post(reverse('atualiza', args=[self.agenda.id]), data)
        self.assertRedirects(response, reverse('index'))
        
        # Verificar se os dados foram atualizados
        self.agenda.refresh_from_db()
        self.assertEqual(self.agenda.sobrenome, 'Atualizado')
        self.assertEqual(self.agenda.email, 'atualizado@example.com')
        self.assertEqual(self.agenda.descricao_servico, 'Descrição atualizada')

class ExcluirViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.genero = Genero.objects.create(nome='Masculino')
        self.faixa_etaria = Faixa_Etaria.objects.create(nome='Adulto')
        self.agenda = Agenda.objects.create(
            nome='Cliente',
            sobrenome='Excluir',
            contato='12345678',
            descricao_servico='Teste de exclusão',
            valor='50,00',
            genero=self.genero,
            faixa_etaria=self.faixa_etaria
        )
    
    def test_excluir(self):
        self.assertEqual(Agenda.objects.count(), 1)
        response = self.client.post(reverse('excluir', args=[self.agenda.id]))
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Agenda.objects.count(), 0)

class RegistroViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_registro_get(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'agenda/registro.html')
        
    def test_registro_post_valid(self):
        data = {
            'nome': 'Usuário',
            'sobrenome': 'Teste',
            'email': 'usuario@example.com',
            'username': 'usuario_teste',
            'password1': 'senha_segura123',
            'password2': 'senha_segura123'
        }
        
        response = self.client.post(reverse('registro'), data)
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(User.objects.count(), 1)
        
    def test_registro_post_email_exists(self):
        # Criar usuário com email existente
        User.objects.create_user(
            username='usuario_existente',
            email='existente@example.com', 
            password='senha123'
        )
        
        data = {
            'nome': 'Outro',
            'sobrenome': 'Usuário',
            'email': 'existente@example.com',  # Email já existe
            'username': 'outro_usuario',
            'password1': 'senha_segura123',
            'password2': 'senha_segura123'
        }
        
        response = self.client.post(reverse('registro'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)  # Não deve criar novo usuário
