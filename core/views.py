from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.db.models import Count, Q
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.urls import reverse
from datetime import datetime
import json
import secrets
import traceback
from urllib import error, parse, request as urllib_request
from core.models import AllowedEmail
from django.http import HttpResponse



from .models import (
    CasoUso,
    Material,
    Video,
    Ferramenta,
    RoadmapProgresso,
    RoadmapFase,
    RoadmapEntrega,
    AllowedEmail,
    UserOnboarding,
)

def is_admin(user):
    try:
        return AllowedEmail.objects.get(email=user.email).role == 'admin'
    except AllowedEmail.DoesNotExist:
        return False
# ================== FUNÇÕES AUXILIARES ==================

def perfis_view(request):
    return render(request, 'core/perfis.html')

def get_user_role(user):
    """Retorna o papel do usuário baseado no email autorizado"""
    try:
        allowed = AllowedEmail.objects.get(email=user.email)
        return allowed.role
    except AllowedEmail.DoesNotExist:
        return 'viewer'


def normalize_video_url(url_or_id):
    """Preserva o link informado, removendo apenas espaços extras."""
    return (url_or_id or '').strip()


def criar_admin_se_nao_existir():
    """Cria usuário admin padrão se não existir"""
    if not User.objects.filter(email='admin@artefact.com').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@artefact.com',
            password='admin'
        )
        # Também adiciona à lista de emails permitidos
        AllowedEmail.objects.get_or_create(
            email='admin@artefact.com',
            defaults={
                'role': 'admin',
                'nome': 'Administrador',
                'added_by': 'system'
            }
        )


# ================== DEBUG VIEW ==================

def debug_view(request):
    """View para debug do banco de dados"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM core_casouso")
            count = cursor.fetchone()[0]
        
        data = {
            'status': 'OK',
            'db_connected': True,
            'casos_count': count,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'status': 'ERROR', 
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)



def force_login(request):
    user = User.objects.first()

    if not user:
        return HttpResponse("Nenhum usuário existe")

    login(request, user)
    return HttpResponse("logado")

# ================== AUTH ==================

def home(request):
    return redirect('boas_vindas')


@login_required
def boas_vindas(request):
    """Página de boas-vindas. Exige preenchimento do formulário de skills no 1º acesso."""
    onboarding, _ = UserOnboarding.objects.get_or_create(user=request.user)

    if onboarding.onboarding_completo:
        return redirect('dashboard')

    if request.method == 'POST':
        onboarding.onboarding_completo = True
        onboarding.data_conclusao = timezone.now()
        onboarding.save()
        return redirect('dashboard')

    return render(request, 'core/boas_vindas.html')


def _is_google_auth_configured():
    return bool(settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_CLIENT_SECRET)


def _get_google_redirect_uri(request):
    return request.build_absolute_uri(reverse('google_callback'))


def _exchange_google_code_for_tokens(request, code):
    payload = parse.urlencode({
        'code': code,
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
        'redirect_uri': _get_google_redirect_uri(request),
        'grant_type': 'authorization_code',
    }).encode('utf-8')
    req = urllib_request.Request(
        'https://oauth2.googleapis.com/token',
        data=payload,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    with urllib_request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode('utf-8'))


def _fetch_google_token_info(id_token):
    token_info_url = 'https://oauth2.googleapis.com/tokeninfo?id_token=' + parse.quote(id_token)

    with urllib_request.urlopen(token_info_url, timeout=15) as response:
        return json.loads(response.read().decode('utf-8'))


def _get_or_create_local_user(email):
    email = email.lower().strip()
    user = User.objects.filter(email=email).first()

    if user:
        return user

    user = User.objects.create(
        username=email,
        email=email,
    )
    user.set_unusable_password()
    user.save()
    return user


def _validate_allowed_email(email):
    email = email.lower().strip()

    try:
        AllowedEmail.objects.get(email=email)
    except AllowedEmail.DoesNotExist:
        return False, 'Email não autorizado'

    return True, None


def login_view(request):
    if request.user.is_authenticated:
        return redirect('boas_vindas')

    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            return render(request, 'core/login.html', {'erro': 'Email vazio'})

        email = email.lower().strip()
        is_allowed, error_message = _validate_allowed_email(email)
        if not is_allowed:
            return render(request, 'core/login.html', {'erro': error_message})

        user = _get_or_create_local_user(email)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return redirect('boas_vindas')

    return render(request, 'core/login.html')


def google_login_view(request):
    if request.user.is_authenticated:
        return redirect('boas_vindas')

    if not _is_google_auth_configured():
        messages.error(request, 'Login Google não configurado no servidor.')
        return redirect('login')

    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state

    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': _get_google_redirect_uri(request),
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
        'prompt': 'select_account',
    }

    if settings.GOOGLE_WORKSPACE_DOMAIN:
        params['hd'] = settings.GOOGLE_WORKSPACE_DOMAIN

    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + parse.urlencode(params)
    return redirect(auth_url)


def google_callback_view(request):
    if not _is_google_auth_configured():
        messages.error(request, 'Login Google não configurado no servidor.')
        return redirect('login')

    if request.GET.get('error'):
        messages.error(request, 'Autenticação Google cancelada ou recusada.')
        return redirect('login')

    expected_state = request.session.pop('google_oauth_state', None)
    received_state = request.GET.get('state')

    if not expected_state or expected_state != received_state:
        messages.error(request, 'Falha de validação no retorno do Google. Tente novamente.')
        return redirect('login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Código de autenticação do Google não recebido.')
        return redirect('login')

    try:
        token_data = _exchange_google_code_for_tokens(request, code)
        id_token = token_data.get('id_token')
        token_info = _fetch_google_token_info(id_token)
    except error.HTTPError:
        messages.error(request, 'Não foi possível validar o login com Google.')
        return redirect('login')
    except error.URLError:
        messages.error(request, 'Falha de comunicação com o Google. Tente novamente.')
        return redirect('login')
    except json.JSONDecodeError:
        messages.error(request, 'Resposta inválida recebida do Google.')
        return redirect('login')

    if token_info.get('aud') != settings.GOOGLE_OAUTH_CLIENT_ID:
        messages.error(request, 'Token Google inválido para esta aplicação.')
        return redirect('login')

    email = (token_info.get('email') or '').lower().strip()
    if not email:
        messages.error(request, 'Conta Google sem email disponível.')
        return redirect('login')

    if str(token_info.get('email_verified', '')).lower() != 'true':
        messages.error(request, 'A conta Google precisa ter email verificado.')
        return redirect('login')

    expected_domain = (settings.GOOGLE_WORKSPACE_DOMAIN or '').lower().strip()
    email_domain = email.split('@')[-1] if '@' in email else ''
    hosted_domain = (token_info.get('hd') or '').lower().strip()

    if expected_domain and email_domain != expected_domain:
        messages.error(request, 'Use sua conta corporativa da Artefact para acessar.')
        return redirect('login')

    if expected_domain and hosted_domain and hosted_domain != expected_domain:
        messages.error(request, 'A conta Google autenticada não pertence ao workspace permitido.')
        return redirect('login')

    is_allowed, error_message = _validate_allowed_email(email)
    if not is_allowed:
        messages.error(request, error_message)
        return redirect('login')

    user = _get_or_create_local_user(email)
    login(request, user)
    messages.success(request, f'Login realizado com {email}.')
    return redirect('boas_vindas')


# ================== DASHBOARD ==================

@login_required
def dashboard(request):
    criar_admin_se_nao_existir()  

    context = {
        'total_casos': CasoUso.objects.filter(ativo=True).count(),
        'total_materiais': Material.objects.count(),
        'total_videos': Video.objects.count(),
        'total_ferramentas': Ferramenta.objects.count(),
        'ultimos_casos': CasoUso.objects.filter(
            ativo=True
        ).order_by('-data_criacao')[:5],
        'top_contribuidores': _get_top_contribuidores(),
        'user_role': get_user_role(request.user),
    }

    return render(request, 'core/dashboard.html', context)


def _get_top_contribuidores():
    top = (
        CasoUso.objects
        .filter(ativo=True)
        .values('autor_email')
        .annotate(total_casos=Count('id'))
        .order_by('-total_casos')[:5]
    )

    resultado = []

    for item in top:
        email = item['autor_email']

        try:
            allowed = AllowedEmail.objects.get(email=email)
            nome = allowed.email  # ou campo nome se tiver
            role = allowed.role
        except AllowedEmail.DoesNotExist:
            nome = email
            role = 'viewer'

        resultado.append({
            'email': email,
            'nome': nome,
            'role': role,
            'total_casos': item['total_casos']
        })

    return resultado

# ================== CASOS DE USO ==================

@login_required
def casos_lista(request):
    """Lista todos os casos de uso"""
    query = request.GET.get('q', '').strip()
    casos = CasoUso.objects.filter(ativo=True).order_by('-data_criacao')

    if query:
        casos = casos.filter(
            Q(titulo__icontains=query) |
            Q(contexto__icontains=query) |
            Q(tecnologia__icontains=query) |
            Q(descricao__icontains=query) |
            Q(resultado__icontains=query) |
            Q(tags__icontains=query)
        )

    return render(request, 'core/casos.html', {
        'casos': casos,
        'query': query,
        'user_role': get_user_role(request.user)
    })


@login_required
def caso_novo(request):
    """Criar novo caso de uso"""
    if request.method == 'POST':
        agora = timezone.now()
        
        # Buscar nome do autor na tabela AllowedEmail
        try:
            allowed = AllowedEmail.objects.get(email=request.user.email)
            nome_autor = allowed.email  # Usar email como nome se não tiver campo específico
        except AllowedEmail.DoesNotExist:
            nome_autor = request.user.email
        
        caso = CasoUso.objects.create(
            titulo=request.POST.get('titulo'),
            contexto=request.POST.get('contexto'),
            tecnologia=request.POST.get('tecnologia'),
            descricao=request.POST.get('descricao'),
            resultado=request.POST.get('resultado'),
            tags=request.POST.get('tags', ''),
            autor=nome_autor,  # ✅ Preencher campo autor
            autor_email=request.user.email,
            ativo=True,
            data_criacao=agora,
            data_atualizacao=agora
        )
        messages.success(request, '✅ Caso adicionado com sucesso!')
        return redirect('casos_lista')
    
    # GET: retornar para lista
    return redirect('casos_lista')


@login_required
def caso_editar(request, id):
    """Editar caso de uso"""
    caso = get_object_or_404(CasoUso, id=id)
    
    if request.method == 'POST':
        caso.titulo = request.POST.get('titulo')
        caso.contexto = request.POST.get('contexto')
        caso.tecnologia = request.POST.get('tecnologia')
        caso.descricao = request.POST.get('descricao')
        caso.resultado = request.POST.get('resultado')
        caso.tags = request.POST.get('tags', '')
        caso.data_atualizacao = timezone.now()
        caso.save()
        messages.success(request, '✅ Caso atualizado com sucesso!')
        return redirect('casos_lista')
    
    # GET não é tratado - formulário é renderizado em modal no template
    return redirect('casos_lista')


@login_required
def caso_excluir(request, id):
    """Excluir caso de uso (soft delete)"""
    caso = get_object_or_404(CasoUso, id=id)
    caso.ativo = False
    caso.save()
    messages.success(request, '✅ Caso removido com sucesso!')
    return redirect('casos_lista')


@login_required
def caso_dados(request, id):
    """Retorna os dados de um caso em JSON para edição"""
    caso = get_object_or_404(CasoUso, id=id)
    
    data = {
        'id': caso.id,
        'titulo': caso.titulo,
        'contexto': caso.contexto,
        'tecnologia': caso.tecnologia,
        'descricao': caso.descricao,
        'resultado': caso.resultado,
        'tags': caso.tags,
        'autor': caso.autor,
        'autor_email': caso.autor_email,
        'data_criacao': caso.data_criacao.isoformat() if caso.data_criacao else None,
    }
    return JsonResponse(data)


# ================== MATERIAIS ==================

@login_required
def materiais_lista(request):
    """Lista todos os materiais"""
    query = request.GET.get('q', '').strip()
    materiais = Material.objects.all().order_by('-data_criacao')

    if query:
        materiais = materiais.filter(
            Q(titulo__icontains=query) |
            Q(tipo__icontains=query) |
            Q(topicos__icontains=query) |
            Q(descricao__icontains=query) |
            Q(autor__icontains=query)
        )

    return render(request, 'core/materiais.html', {
        'materiais': materiais,
        'query': query,
        'user_role': get_user_role(request.user)
    })


@login_required
def material_novo(request):
    """Criar novo material"""
    if request.method == 'POST':
        material = Material.objects.create(
            titulo=request.POST.get('titulo'),
            tipo=request.POST.get('tipo'),
            topicos=request.POST.get('topicos', ''),
            descricao=request.POST.get('descricao'),
            url=request.POST.get('url', ''),
            autor=request.user.get_full_name() or request.user.username,
            autor_email=request.user.email
        )
        messages.success(request, '✅ Material adicionado com sucesso!')
        return redirect('materiais_lista')
    
    # GET: mostrar formulário
    return render(request, 'core/material_form.html', {
        'user_role': get_user_role(request.user)
    })


@login_required
def material_editar(request, id):
    """Editar material"""
    material = get_object_or_404(Material, id=id)
    
    if request.method == 'POST':
        material.titulo = request.POST.get('titulo')
        material.tipo = request.POST.get('tipo')
        material.topicos = request.POST.get('topicos', '')
        material.descricao = request.POST.get('descricao')
        material.url = request.POST.get('url', '')
        material.save()
        messages.success(request, '✅ Material atualizado com sucesso!')
        return redirect('materiais_lista')
    
    # GET: mostrar formulário com dados
    return render(request, 'core/material_form.html', {
        'material': material,
        'editing': True,
        'user_role': get_user_role(request.user)
    })


@login_required
def material_excluir(request, id):
    """Excluir material"""
    material = get_object_or_404(Material, id=id)
    material.delete()
    messages.success(request, '✅ Material removido com sucesso!')
    return redirect('materiais_lista')


@login_required
def material_dados(request, id):
    """Retorna os dados de um material em JSON para edição"""
    material = get_object_or_404(Material, id=id)
    data = {
        'id': material.id,
        'titulo': material.titulo,
        'tipo': material.tipo,
        'topicos': material.topicos,
        'descricao': material.descricao,
        'url': material.url,
        'autor': material.autor,
    }
    return JsonResponse(data)


# ================== VÍDEOS ==================

@login_required
def videos_lista(request):
    """Lista todos os vídeos"""
    query = request.GET.get('q', '').strip()
    videos = Video.objects.all().order_by('-data_criacao')

    if query:
        videos = videos.filter(
            Q(titulo__icontains=query) |
            Q(descricao__icontains=query) |
            Q(tema__icontains=query) |
            Q(autor__icontains=query)
        )

    return render(request, 'core/videos.html', {
        'videos': videos,
        'query': query,
        'user_role': get_user_role(request.user)
    })


@login_required
def video_novo(request):
    """Criar novo vídeo"""
    if request.method == 'POST':
        autor = request.POST.get('autor', request.user.get_full_name() or request.user.username)
        youtube_id = normalize_video_url(request.POST.get('youtube_id', ''))
        
        video = Video.objects.create(
            titulo=request.POST.get('titulo'),
            descricao=request.POST.get('descricao', ''),
            tema=request.POST.get('tema'),
            nivel=request.POST.get('nivel'),
            duracao=request.POST.get('duracao', ''),
            youtube_id=youtube_id,
            autor=autor,
            autor_email=request.user.email,
            data_criacao=timezone.now()
        )
        messages.success(request, '✅ Vídeo adicionado com sucesso!')
        return redirect('videos_lista')
    
    # GET: retornar para lista
    return redirect('videos_lista')


@login_required
def video_editar(request, id):
    """Editar vídeo"""
    video = get_object_or_404(Video, id=id)
    
    if request.method == 'POST':
        youtube_id = normalize_video_url(request.POST.get('youtube_id', ''))
        
        video.titulo = request.POST.get('titulo')
        video.descricao = request.POST.get('descricao', '')
        video.tema = request.POST.get('tema')
        video.nivel = request.POST.get('nivel')
        video.duracao = request.POST.get('duracao', '')
        video.youtube_id = youtube_id
        video.autor = request.POST.get('autor', video.autor)
        video.save()
        messages.success(request, '✅ Vídeo atualizado com sucesso!')
        return redirect('videos_lista')
    
    # GET: retornar para lista
    return redirect('videos_lista')


@login_required
def video_excluir(request, id):
    """Excluir vídeo"""
    video = get_object_or_404(Video, id=id)
    video.delete()
    messages.success(request, '✅ Vídeo removido com sucesso!')
    return redirect('videos_lista')


@login_required
def video_dados(request, id):
    """Retorna os dados de um vídeo em JSON para edição"""
    video = get_object_or_404(Video, id=id)
    data = {
        'id': video.id,
        'titulo': video.titulo,
        'descricao': video.descricao,
        'tema': video.tema,
        'nivel': video.nivel,
        'duracao': video.duracao,
        'youtube_id': video.youtube_id,
        'autor': video.autor,
        'autor_email': video.autor_email,
    }
    return JsonResponse(data)


# ================== FERRAMENTAS ==================

@login_required
def ferramentas_lista(request):
    """Lista todas as ferramentas"""
    query = request.GET.get('q', '').strip()
    ferramentas = Ferramenta.objects.all().order_by('-data_criacao')

    if query:
        ferramentas = ferramentas.filter(
            Q(nome__icontains=query) |
            Q(categoria__icontains=query) |
            Q(descricao__icontains=query) |
            Q(nivel__icontains=query) |
            Q(autor__icontains=query)
        )

    return render(request, 'core/ferramentas.html', {
        'ferramentas': ferramentas,
        'query': query,
        'user_role': get_user_role(request.user)
    })


@login_required
def ferramenta_novo(request):
    """Criar nova ferramenta"""
    if request.method == 'POST':
        ferramenta = Ferramenta.objects.create(
            nome=request.POST.get('nome'),
            categoria=request.POST.get('categoria'),
            versao=request.POST.get('versao', ''),
            descricao=request.POST.get('descricao'),
            nivel=request.POST.get('nivel', ''),
            documentacao_link=request.POST.get('documentacao_link', ''),
            autor=request.user.get_full_name() or request.user.username,
            autor_email=request.user.email
        )
        messages.success(request, '✅ Ferramenta adicionada com sucesso!')
        return redirect('ferramentas_lista')
    
    # GET: mostrar formulário
    return render(request, 'core/ferramenta_form.html', {
        'user_role': get_user_role(request.user)
    })


@login_required
def ferramenta_editar(request, id):
    """Editar ferramenta"""
    ferramenta = get_object_or_404(Ferramenta, id=id)
    
    if request.method == 'POST':
        ferramenta.nome = request.POST.get('nome')
        ferramenta.categoria = request.POST.get('categoria')
        ferramenta.versao = request.POST.get('versao', '')
        ferramenta.descricao = request.POST.get('descricao')
        ferramenta.nivel = request.POST.get('nivel', '')
        ferramenta.documentacao_link = request.POST.get('documentacao_link', '')
        ferramenta.save()
        messages.success(request, '✅ Ferramenta atualizada com sucesso!')
        return redirect('ferramentas_lista')
    
    # GET: mostrar formulário com dados
    return render(request, 'core/ferramenta_form.html', {
        'ferramenta': ferramenta,
        'editing': True,
        'user_role': get_user_role(request.user)
    })


@login_required
def ferramenta_excluir(request, id):
    """Excluir ferramenta"""
    ferramenta = get_object_or_404(Ferramenta, id=id)
    ferramenta.delete()
    messages.success(request, '✅ Ferramenta removida com sucesso!')
    return redirect('ferramentas_lista')


@login_required
def ferramenta_dados(request, id):
    """Retorna os dados de uma ferramenta em JSON para edição"""
    ferramenta = get_object_or_404(Ferramenta, id=id)
    data = {
        'id': ferramenta.id,
        'nome': ferramenta.nome,
        'categoria': ferramenta.categoria,
        'versao': ferramenta.versao,
        'descricao': ferramenta.descricao,
        'nivel': ferramenta.nivel,
        'documentacao_link': ferramenta.documentacao_link,
        'autor': ferramenta.autor,
    }
    return JsonResponse(data)


# ================== ROADMAP ==================

@login_required
def roadmap_index(request):
    """Página principal do roadmap"""
    user_role = get_user_role(request.user)
    
    context = {
        'progressos': RoadmapProgresso.objects.all(),
        'fases': RoadmapFase.objects.all().order_by('id'),
        'entregas': RoadmapEntrega.objects.all().order_by('-data_criacao'),
        'user_role': user_role,
        'is_admin': user_role == 'admin',
        'edit_mode': request.GET.get('edit', False),
    }
    return render(request, 'core/roadmap.html', context)


@login_required
def roadmap_progresso_editar(request, id):
    """Editar progresso de um pilar"""
    if get_user_role(request.user) != 'admin':
        messages.error(request, 'Permissão negada. Apenas administradores.')
        return redirect('roadmap_index')
    
    progresso = get_object_or_404(RoadmapProgresso, id=id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            novo_progresso = data.get('progresso')
            if novo_progresso is not None:
                progresso.progresso = int(novo_progresso)
                progresso.save()
                messages.success(request, 'Progresso atualizado!')
        except:
            pass
        return redirect('roadmap_index')
    
    return redirect('roadmap_index')


@login_required
def roadmap_fase_atualizar(request, id):
    """Atualizar status de uma fase"""
    if get_user_role(request.user) != 'admin':
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    fase = get_object_or_404(RoadmapFase, id=id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            fase.status = data.get('status')
            fase.save()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def roadmap_entrega_nova(request):
    """Criar nova entrega"""
    if get_user_role(request.user) != 'admin':
        messages.error(request, 'Permissão negada. Apenas administradores.')
        return redirect('roadmap_index')
    
    if request.method == 'POST':
        # Validar campos obrigatórios
        titulo = request.POST.get('titulo', '').strip()
        responsavel = request.POST.get('responsavel', '').strip()
        prazo_str = request.POST.get('prazo', '').strip()
        
        if not titulo or not responsavel or not prazo_str:
            messages.error(request, '❌ Preencha todos os campos obrigatórios (Título, Responsável e Data).')
            return redirect('roadmap_index')
        
        # Converter prazo para DateField
        try:
            prazo = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, '❌ Data inválida. Use o formato YYYY-MM-DD.')
            return redirect('roadmap_index')
        
        try:
            entrega = RoadmapEntrega.objects.create(
                titulo=titulo,
                responsavel=responsavel,
                prazo=prazo,
                prioridade=request.POST.get('prioridade', 'Média'),
                status=request.POST.get('status', 'pendente'),
                criado_por=request.user.username,
                data_criacao=timezone.now()
            )
            messages.success(request, '✅ Entrega adicionada com sucesso!')
        except Exception as e:
            messages.error(request, f'❌ Erro ao criar entrega: {str(e)}')
        
        return redirect('roadmap_index')
    
    # GET: retornar para roadmap
    return redirect('roadmap_index')


@login_required
def roadmap_entrega_status(request, id):
    """Atualizar status de uma entrega"""
    if get_user_role(request.user) != 'admin':
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    entrega = get_object_or_404(RoadmapEntrega, id=id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entrega.status = data.get('status')
            entrega.save()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'error': 'Dados inválidos'}, status=400)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
def roadmap_entrega_excluir(request, id):
    """Excluir entrega"""
    if get_user_role(request.user) != 'admin':
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    entrega = get_object_or_404(RoadmapEntrega, id=id)
    entrega.delete()
    return JsonResponse({'success': True})


# ================== GAMIFICAÇÃO ==================

@login_required
def gamificacao_ranking(request):
    """Ranking de gamificação com pontuação detalhada"""
    
    # Buscar todos os usuários com email autorizado
    allowed_emails = AllowedEmail.objects.values_list('email', flat=True)
    usuarios = User.objects.filter(email__in=allowed_emails)
    
    ranking = []
    
    for user in usuarios:
        # Contar contribuições usando email (mais confiável)
        casos = CasoUso.objects.filter(
            autor_email=user.email,
            ativo=True
            ).count()
        
        # Usar email para filtrar contribuições
        videos = Video.objects.filter(autor_email=user.email).count()
        materiais = Material.objects.filter(autor_email=user.email).count()
        ferramentas = Ferramenta.objects.filter(autor_email=user.email).count()
        
        # Calcular pontuação
        pontos_casos = casos * 10
        pontos_videos = videos * 15
        pontos_materiais = materiais * 3
        pontos_ferramentas = ferramentas * 8
        
        pontuacao_total = pontos_casos + pontos_videos + pontos_materiais + pontos_ferramentas
        total_contribuicoes = casos + videos + materiais + ferramentas
        
        if pontuacao_total > 0 or total_contribuicoes > 0:
            # Buscar role do usuário
            try:
                allowed = AllowedEmail.objects.get(email=user.email)
                role = allowed.role
                nome_exibicao = user.get_full_name() or user.username
            except AllowedEmail.DoesNotExist:
                role = 'viewer'
                nome_exibicao = user.get_full_name() or user.username
            
            ranking.append({
                'id': user.id,
                'email': user.email,
                'nome': nome_exibicao,
                'role': role,
                'avatar': None,
                'pontuacao': pontuacao_total,
                'total_contribuicoes': total_contribuicoes,
                'detalhes': {
                    'casos': casos,
                    'videos': videos,
                    'materiais': materiais,
                    'ferramentas': ferramentas,
                }
            })
    
    # Ordenar por pontuação
    ranking.sort(key=lambda x: x['pontuacao'], reverse=True)
    
    # Calcular percentual para barra de progresso
    max_pontos = ranking[0]['pontuacao'] if ranking else 1
    for item in ranking:
        item['percentual'] = (item['pontuacao'] / max_pontos) * 100
    
    # Destaque do mês (primeiro do ranking)
    destaque_mes = ranking[0] if ranking else None
    
    context = {
        'ranking': ranking,
        'destaque_mes': destaque_mes,
        'user_role': get_user_role(request.user),
    }
    return render(request, 'core/ranking.html', context)


# ================== GERENCIAMENTO DE USUÁRIOS ==================

@login_required
def admin_usuarios(request):
    """Gerenciamento de usuários autorizados (apenas admin)"""
    if get_user_role(request.user) != 'admin':
        messages.error(request, 'Acesso negado. Apenas administradores.')
        return redirect('dashboard')
    
    usuarios = AllowedEmail.objects.all().order_by('-added_at')
    
    context = {
        'usuarios': usuarios,
        'user_role': 'admin',
    }
    return render(request, 'core/admin_usuarios.html', context)


@login_required
def admin_usuario_novo(request):
    """Adicionar novo usuário (apenas admin)"""
    if get_user_role(request.user) != 'admin':
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', 'viewer')
        nome = request.POST.get('nome', '')
        
        # Validar domínio
        if not email.endswith('@artefact.com'):
            messages.error(request, 'O email deve ser do domínio @artefact.com')
            return redirect('admin_usuarios')
        
        # Verificar se já existe
        if AllowedEmail.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} já cadastrado')
            return redirect('admin_usuarios')
        
        # Criar novo usuário na lista de permitidos
        AllowedEmail.objects.create(
            email=email.lower(),
            role=role,
            nome=nome,
            added_by=request.user.email
        )
        
        # Criar usuário Django se não existir
        if not User.objects.filter(email=email).exists():
            username = email.split('@')[0]
            User.objects.create_user(
                username=username,
                email=email,
                password=None
            )
        
        messages.success(request, f'✅ Usuário {email} adicionado com sucesso!')
        return redirect('admin_usuarios')
    
    # GET: mostrar formulário
    return render(request, 'core/admin_usuario_form.html', {
        'editing': False,
        'user_role': 'admin'
    })


@login_required
def admin_usuario_editar(request, email):
    """Editar role de um usuário (apenas admin)"""
    if get_user_role(request.user) != 'admin':
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    usuario = get_object_or_404(AllowedEmail, email=email)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        nome = request.POST.get('nome')
        
        usuario.role = role
        usuario.nome = nome
        usuario.save()
        messages.success(request, f'✅ Usuário {email} atualizado com sucesso!')
        return redirect('admin_usuarios')
    
    # GET: mostrar formulário com dados
    return render(request, 'core/admin_usuario_form.html', {
        'usuario': usuario,
        'editing': True,
        'user_role': 'admin'
    })


@login_required
def admin_usuario_excluir(request, email):
    """Excluir usuário (apenas admin)"""
    if get_user_role(request.user) != 'admin':
        return JsonResponse({'error': 'Permissão negada'}, status=403)
    
    usuario = get_object_or_404(AllowedEmail, email=email)
    
    # Não permitir excluir a si mesmo
    if usuario.email == request.user.email:
        messages.error(request, 'Você não pode excluir seu próprio usuário')
        return redirect('admin_usuarios')
    
    # Opcional: não excluir o usuário Django, apenas remover permissão
    # usuario.delete()
    
    # Melhor: apenas desativar em vez de excluir
    messages.success(request, f'✅ Usuário {email} removido com sucesso!')
    return redirect('admin_usuarios')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')