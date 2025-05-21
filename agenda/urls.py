from django.urls import path
from agenda import views

urlpatterns = [
    path('pesquisa/', views.pesquisa, name='pesquisa'),
    path('', views.index, name='index'),

    # URLs para as páginas
    path('agendamento/<int:cadastro_id>/detail/', views.cadastro, name='cadastro'),
    path('agendamento/inserir_cadastro/', views.inserir_cadastro, name='inserir_cadastro'), 
    path('agendamento/<int:cadastro_id>/atualiza/', views.atualiza, name='atualiza'),
    path('agendamento/<int:cadastro_id>/excluir/', views.excluir, name='excluir'),
    
    # URL para user
    path('usuario/criar/', views.registro, name='registro'),

    # Rotas alternativas para a Vercel
    path('registroagendamento/inserir_cadastro/', views.inserir_cadastro, name='inserir_cadastro_alt'),
    path('registroagendamento/<int:cadastro_id>/atualiza/', views.atualiza, name='atualiza_alt'),
    path('registroagendamento/<int:cadastro_id>/detail/', views.cadastro, name='cadastro_alt'),
    path('registroagendamento/<int:cadastro_id>/excluir/', views.excluir, name='excluir_alt'),
]