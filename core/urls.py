# core/urls.py
from django.urls import include, path
from . import views

# Adicione no topo
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK")

urlpatterns = [
    path('', views.home, name='home'),
    path('boas-vindas/', views.boas_vindas, name='boas_vindas'),
    path('login/', views.login_view, name='login'),
    path('login/google/', views.google_login_view, name='google_login'),
    path('login/google/callback/', views.google_callback_view, name='google_callback'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
     #  TESTE
    path('force-login/', views.force_login, name='force_login'),
    # 👇 ESSENCIAL PRO GOOGLE LOGIN
    path('accounts/', include('allauth.urls')),
    
    # Casos
    path('casos/', views.casos_lista, name='casos_lista'),
    path('casos/novo/', views.caso_novo, name='caso_novo'),
    path('casos/editar/<int:id>/', views.caso_editar, name='caso_editar'),
    path('casos/excluir/<int:id>/', views.caso_excluir, name='caso_excluir'),
    path('casos/<int:id>/dados/', views.caso_dados, name='caso_dados'),

    # Materiais
    path('materiais/', views.materiais_lista, name='materiais_lista'),
    path('materiais/novo/', views.material_novo, name='material_novo'),
    path('materiais/editar/<int:id>/', views.material_editar, name='material_editar'),
    path('materiais/excluir/<int:id>/', views.material_excluir, name='material_excluir'),
    path('materiais/<int:id>/dados/', views.material_dados, name='material_dados'),
    
    # Vídeos
    path('videos/', views.videos_lista, name='videos_lista'),
    path('videos/novo/', views.video_novo, name='video_novo'),
    path('videos/editar/<int:id>/', views.video_editar, name='video_editar'),
    path('videos/excluir/<int:id>/', views.video_excluir, name='video_excluir'),
    path('videos/<int:id>/dados/', views.video_dados, name='video_dados'),
        
    # Ferramentas
    path('ferramentas/', views.ferramentas_lista, name='ferramentas_lista'),
    path('ferramentas/novo/', views.ferramenta_novo, name='ferramenta_novo'),
    path('ferramentas/editar/<int:id>/', views.ferramenta_editar, name='ferramenta_editar'),
    path('ferramentas/excluir/<int:id>/', views.ferramenta_excluir, name='ferramenta_excluir'),
    path('ferramentas/<int:id>/dados/', views.ferramenta_dados, name='ferramenta_dados'),
    
    # Roadmap
    path('roadmap/', views.roadmap_index, name='roadmap_index'),
    path('roadmap/progresso/editar/<int:id>/', views.roadmap_progresso_editar, name='roadmap_progresso_editar'),
    path('roadmap/fase/atualizar/<int:id>/', views.roadmap_fase_atualizar, name='roadmap_fase_atualizar'),
    path('roadmap/entrega/nova/', views.roadmap_entrega_nova, name='roadmap_entrega_nova'),
    path('roadmap/entrega/status/<int:id>/', views.roadmap_entrega_status, name='roadmap_entrega_status'),
    path('roadmap/entrega/excluir/<int:id>/', views.roadmap_entrega_excluir, name='roadmap_entrega_excluir'),
    
    # Gamificação
    path('ranking/', views.gamificacao_ranking, name='ranking'),

    # Admin Usuários
    path('admin/usuarios/', views.admin_usuarios, name='admin_usuarios'),
    path('admin/usuarios/novo/', views.admin_usuario_novo, name='admin_usuario_novo'),
    path('admin/usuarios/editar/<str:email>/', views.admin_usuario_editar, name='admin_usuario_editar'),
    path('admin/usuarios/excluir/<str:email>/', views.admin_usuario_excluir, name='admin_usuario_excluir'),

    # Perfis
    path('perfis/', views.perfis_view, name='perfis'),
]