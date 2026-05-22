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
    Snippet,
    RoadmapProgresso,
    RoadmapFase,
    RoadmapEntrega,
    AllowedEmail,
    UserOnboarding,
    Favorito,
)

def is_admin(user):
    try:
        return AllowedEmail.objects.get(email=user.email).role == 'admin'
    except AllowedEmail.DoesNotExist:
        return False
# ================== FUNÇÕES AUXILIARES ==================

@login_required
def perfis_view(request):
    import json as _json
    ferramentas_db = list(
        Ferramenta.objects.values('id', 'nome', 'categoria', 'descricao', 'nivel', 'documentacao_link')
    )
    # Ideal tools per profile (fallback when no DB match is found)
    perfis_tools_fallback = {
        'architect': [
            {'nome': 'Jira', 'descricao': 'Task and sprint management with visual board', 'link': 'https://www.atlassian.com/software/jira'},
            {'nome': 'ClickUp', 'descricao': 'Weekly planning and delivery tracking', 'link': 'https://clickup.com'},
            {'nome': 'Google Calendar', 'descricao': 'Time blocking and weekly rituals', 'link': 'https://calendar.google.com'},
            {'nome': 'Pomodoro (Forest/Focus)', 'descricao': 'Focus technique in timed work blocks', 'link': 'https://pomofocus.io'},
            {'nome': 'Notion', 'descricao': 'Structured documentation and project wikis', 'link': 'https://notion.so'},
        ],
        'gogetter': [
            {'nome': 'Trello', 'descricao': 'Simple kanban board to track what is in progress', 'link': 'https://trello.com'},
            {'nome': 'OneNote', 'descricao': 'Quick notes without rigid structure', 'link': 'https://onenote.com'},
            {'nome': 'Slack', 'descricao': 'Agile communication and fast team escalation', 'link': 'https://slack.com'},
            {'nome': 'Miro', 'descricao': 'Quick mind-mapping in crisis moments', 'link': 'https://miro.com'},
            {'nome': 'Linear', 'descricao': 'Minimalist issue tracking for low-overhead workflows', 'link': 'https://linear.app'},
        ],
        'simplifier': [
            {'nome': 'Excel / Google Sheets', 'descricao': 'Simple lists and prioritization without complexity', 'link': 'https://sheets.google.com'},
            {'nome': 'Google Docs', 'descricao': 'Lightweight and collaborative documentation', 'link': 'https://docs.google.com'},
            {'nome': 'Google Keep', 'descricao': 'Quick notes and visual reminders', 'link': 'https://keep.google.com'},
            {'nome': 'Paper + Pen', 'descricao': 'The classic that never fails for those who think by writing', 'link': ''},
            {'nome': 'WhatsApp / Slack', 'descricao': 'Asking the team for help without ceremony', 'link': 'https://slack.com'},
        ],
        'systematic': [
            {'nome': 'Excalidraw', 'descricao': 'Quick diagrams to externalize thinking', 'link': 'https://excalidraw.com'},
            {'nome': 'Mermaid', 'descricao': 'Diagrams as code — traceable and versionable', 'link': 'https://mermaid.js.org'},
            {'nome': 'NotebookLM', 'descricao': 'AI as cognitive extension to process large documents', 'link': 'https://notebooklm.google.com'},
            {'nome': 'Notion', 'descricao': 'Personal knowledge base and initiative spreadsheet', 'link': 'https://notion.so'},
            {'nome': 'dbt', 'descricao': 'Documentation and traceability at the analytics layer', 'link': 'https://www.getdbt.com'},
        ],
    }
    return render(request, 'core/perfis.html', {
        'ferramentas_db': _json.dumps(ferramentas_db, default=str),
        'perfis_tools_fallback': _json.dumps(perfis_tools_fallback),
        'user_role': get_user_role(request.user),
    })

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


def _get_favoritos_ids(user_email, content_type):
    """Returns list of bookmarked object_ids for the user. Returns [] if the table doesn't exist yet."""
    try:
        return list(
            Favorito.objects.filter(usuario_email=user_email, content_type=content_type)
            .values_list('object_id', flat=True)
        )
    except Exception:
        return []


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
        # Capturar perfil_tipo se vier no POST do onboarding
        perfil_tipo = request.POST.get('perfil_tipo', '').strip()
        if perfil_tipo in ['architect', 'gogetter', 'simplifier', 'systematic']:
            onboarding.perfil_tipo = perfil_tipo
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
        # Use iexact so capitalisation differences (e.g. User@Artefact.com vs
        # user@artefact.com) never block a valid email.
        AllowedEmail.objects.get(email__iexact=email)
    except AllowedEmail.DoesNotExist:
        return False, 'Email not authorized. Ask an admin to add your email to the access list.'

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
        messages.error(request, 'Google login is not configured on the server.')
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
        messages.error(request, 'Google login is not configured on the server.')
        return redirect('login')

    if request.GET.get('error'):
        messages.error(request, 'Google authentication was cancelled or denied.')
        return redirect('login')

    expected_state = request.session.pop('google_oauth_state', None)
    received_state = request.GET.get('state')

    if not expected_state or expected_state != received_state:
        messages.error(request, 'Google callback validation failed. Please try again.')
        return redirect('login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'Google authentication code was not received.')
        return redirect('login')

    try:
        token_data = _exchange_google_code_for_tokens(request, code)
        id_token = token_data.get('id_token')
        token_info = _fetch_google_token_info(id_token)
    except error.HTTPError:
        messages.error(request, 'Could not validate Google login.')
        return redirect('login')
    except error.URLError:
        messages.error(request, 'Communication with Google failed. Please try again.')
        return redirect('login')
    except json.JSONDecodeError:
        messages.error(request, 'Invalid response received from Google.')
        return redirect('login')

    if token_info.get('aud') != settings.GOOGLE_OAUTH_CLIENT_ID:
        messages.error(request, 'Google token is invalid for this application.')
        return redirect('login')

    email = (token_info.get('email') or '').lower().strip()
    if not email:
        messages.error(request, 'Google account has no email available.')
        return redirect('login')

    if str(token_info.get('email_verified', '')).lower() != 'true':
        messages.error(request, 'The Google account must have a verified email.')
        return redirect('login')

    expected_domain = (settings.GOOGLE_WORKSPACE_DOMAIN or '').lower().strip()
    email_domain = email.split('@')[-1] if '@' in email else ''
    hosted_domain = (token_info.get('hd') or '').lower().strip()

    if expected_domain and email_domain != expected_domain:
        messages.error(request, 'Please use your Artefact corporate account to log in.')
        return redirect('login')

    if expected_domain and hosted_domain and hosted_domain != expected_domain:
        messages.error(request, 'The authenticated Google account does not belong to the allowed workspace.')
        return redirect('login')

    is_allowed, error_message = _validate_allowed_email(email)
    if not is_allowed:
        messages.error(request, error_message)
        return redirect('login')

    user = _get_or_create_local_user(email)
    login(request, user)
    messages.success(request, f'Logged in as {email}.')
    return redirect('boas_vindas')


# ================== DASHBOARD ==================

@login_required
def dashboard(request):
    criar_admin_se_nao_existir()

    from datetime import timedelta

    agora = timezone.now()
    inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_mes_anterior = (inicio_mes - timedelta(days=1)).replace(day=1)

    # Totais atuais
    total_casos = CasoUso.objects.filter(ativo=True).count()
    total_materiais = Material.objects.count()
    total_videos = Video.objects.count()
    total_ferramentas = Ferramenta.objects.count()

    # Novos este mês
    novos_casos_mes = CasoUso.objects.filter(ativo=True, data_criacao__gte=inicio_mes).count()
    novos_materiais_mes = Material.objects.filter(data_criacao__gte=inicio_mes).count()
    novos_videos_mes = Video.objects.filter(data_criacao__gte=inicio_mes).count()
    novos_ferramentas_mes = Ferramenta.objects.filter(data_criacao__gte=inicio_mes).count()

    # Dados para gráfico de atividade (últimos 6 meses)
    grafico_labels = []
    grafico_casos = []
    grafico_outros = []
    for i in range(5, -1, -1):
        mes_ref = (agora.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
        if i == 0:
            fim_mes = agora
        else:
            prox = (mes_ref.replace(day=28) + timedelta(days=4)).replace(day=1)
            fim_mes = prox - timedelta(seconds=1)

        grafico_labels.append(mes_ref.strftime('%b/%y'))
        n_casos = CasoUso.objects.filter(data_criacao__gte=mes_ref, data_criacao__lte=fim_mes, ativo=True).count()
        n_outros = (
            Material.objects.filter(data_criacao__gte=mes_ref, data_criacao__lte=fim_mes).count() +
            Video.objects.filter(data_criacao__gte=mes_ref, data_criacao__lte=fim_mes).count() +
            Ferramenta.objects.filter(data_criacao__gte=mes_ref, data_criacao__lte=fim_mes).count()
        )
        grafico_casos.append(n_casos)
        grafico_outros.append(n_outros)

    context = {
        'total_casos': total_casos,
        'total_materiais': total_materiais,
        'total_videos': total_videos,
        'total_ferramentas': total_ferramentas,
        'novos_casos_mes': novos_casos_mes,
        'novos_materiais_mes': novos_materiais_mes,
        'novos_videos_mes': novos_videos_mes,
        'novos_ferramentas_mes': novos_ferramentas_mes,
        'ultimos_casos': CasoUso.objects.filter(ativo=True).order_by('-data_criacao')[:5],
        'top_contribuidores': _get_top_contribuidores(),
        'user_role': get_user_role(request.user),
        'grafico_labels': json.dumps(grafico_labels),
        'grafico_casos': json.dumps(grafico_casos),
        'grafico_outros': json.dumps(grafico_outros),
    }

    return render(request, 'core/dashboard.html', context)


def _get_top_contribuidores():
    try:
        from collections import defaultdict
        pontos_por_email = defaultdict(lambda: {'casos': 0, 'videos': 0, 'materiais': 0, 'ferramentas': 0})

        for item in CasoUso.objects.filter(ativo=True).values('autor_email').annotate(n=Count('id')):
            pontos_por_email[item['autor_email']]['casos'] = item['n']
        for item in Video.objects.values('autor_email').annotate(n=Count('id')):
            pontos_por_email[item['autor_email']]['videos'] = item['n']
        for item in Material.objects.values('autor_email').annotate(n=Count('id')):
            pontos_por_email[item['autor_email']]['materiais'] = item['n']
        for item in Ferramenta.objects.values('autor_email').annotate(n=Count('id')):
            pontos_por_email[item['autor_email']]['ferramentas'] = item['n']

        resultado = []
        for email, d in pontos_por_email.items():
            total = d['casos'] * 10 + d['videos'] * 15 + d['materiais'] * 3 + d['ferramentas'] * 8
            if total == 0:
                continue
            try:
                allowed = AllowedEmail.objects.get(email=email)
                nome = allowed.nome or email
                role = allowed.role
            except AllowedEmail.DoesNotExist:
                nome = email
                role = 'viewer'
            resultado.append({
                'email': email,
                'nome': nome,
                'role': role,
                'total_contribuicoes': d['casos'] + d['videos'] + d['materiais'] + d['ferramentas'],
                'pontuacao': total,
            })

        resultado.sort(key=lambda x: x['pontuacao'], reverse=True)
        return resultado[:5]
    except Exception:
        return []

# ================== CASOS DE USO ==================

@login_required
def casos_lista(request):
    """Lista todos os casos de uso"""
    query = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
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
    if tag:
        casos = casos.filter(tags__icontains=tag)

    favoritos_ids = _get_favoritos_ids(request.user.email, 'caso')

    return render(request, 'core/casos.html', {
        'casos': casos,
        'query': query,
        'tag_filtro': tag,
        'favoritos_ids': favoritos_ids,
        'user_role': get_user_role(request.user)
    })


@login_required
def caso_novo(request):
    """Criar novo caso de uso"""
    if get_user_role(request.user) == 'viewer':
        messages.error(request, '🚫 You do not have permission to add items.')
        return redirect('casos_lista')

    if request.method == 'POST':
        agora = timezone.now()
        
        # Buscar nome do autor na tabela AllowedEmail
        try:
            allowed = AllowedEmail.objects.get(email=request.user.email)
            nome_autor = allowed.nome or request.user.email
        except AllowedEmail.DoesNotExist:
            nome_autor = request.user.email
        
        caso = CasoUso.objects.create(
            titulo=request.POST.get('titulo'),
            contexto=request.POST.get('contexto'),
            tecnologia=request.POST.get('tecnologia'),
            descricao=request.POST.get('descricao'),
            resultado=request.POST.get('resultado'),
            tags=request.POST.get('tags', ''),
            autor=nome_autor,
            autor_email=request.user.email,
            autor_id=request.user.id,  # satisfies NOT NULL FK constraint in casos_uso
            ativo=True,
            data_criacao=agora,
            data_atualizacao=agora
        )
        messages.success(request, '✅ Case added successfully!')
        return redirect('casos_lista')
    
    # GET: retornar para lista
    return redirect('casos_lista')


@login_required
def caso_editar(request, id):
    """Editar caso de uso"""
    caso = get_object_or_404(CasoUso, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to edit items.')
        return redirect('casos_lista')
    if role == 'user' and caso.autor_email != request.user.email:
        messages.error(request, '🚫 You can only edit cases you created yourself.')
        return redirect('casos_lista')

    if request.method == 'POST':
        caso.titulo = request.POST.get('titulo')
        caso.contexto = request.POST.get('contexto')
        caso.tecnologia = request.POST.get('tecnologia')
        caso.descricao = request.POST.get('descricao')
        caso.resultado = request.POST.get('resultado')
        caso.tags = request.POST.get('tags', '')
        caso.data_atualizacao = timezone.now()
        caso.save()
        messages.success(request, '✅ Case updated successfully!')
        return redirect('casos_lista')
    
    # GET não é tratado - formulário é renderizado em modal no template
    return redirect('casos_lista')


@login_required
def caso_excluir(request, id):
    """Excluir caso de uso (soft delete)"""
    caso = get_object_or_404(CasoUso, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to delete items.')
        return redirect('casos_lista')
    if role == 'user' and caso.autor_email != request.user.email:
        messages.error(request, '🚫 You can only delete cases you created yourself.')
        return redirect('casos_lista')

    caso.ativo = False
    caso.save()
    messages.success(request, '✅ Case deleted successfully!')
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
    tag = request.GET.get('tag', '').strip()
    materiais = Material.objects.all().order_by('-data_criacao')

    if query:
        materiais = materiais.filter(
            Q(titulo__icontains=query) |
            Q(tipo__icontains=query) |
            Q(topicos__icontains=query) |
            Q(descricao__icontains=query) |
            Q(autor__icontains=query)
        )
    if tag:
        materiais = materiais.filter(topicos__icontains=tag)

    favoritos_ids = _get_favoritos_ids(request.user.email, 'material')

    return render(request, 'core/materiais.html', {
        'materiais': materiais,
        'query': query,
        'tag_filtro': tag,
        'favoritos_ids': favoritos_ids,
        'user_role': get_user_role(request.user)
    })


@login_required
def material_novo(request):
    """Criar novo material"""
    if get_user_role(request.user) == 'viewer':
        messages.error(request, '🚫 You do not have permission to add items.')
        return redirect('materiais_lista')

    if request.method == 'POST':
        material = Material.objects.create(
            titulo=request.POST.get('titulo'),
            tipo=request.POST.get('tipo'),
            topicos=request.POST.get('topicos', ''),
            descricao=request.POST.get('descricao'),
            url=request.POST.get('url', ''),
            autor=request.user.get_full_name() or request.user.username,
            autor_email=request.user.email,
            data_criacao=timezone.now()
        )
        messages.success(request, '✅ Material added successfully!')
        return redirect('materiais_lista')
    
    # GET: mostrar formulário
    return render(request, 'core/material_form.html', {
        'user_role': get_user_role(request.user)
    })


@login_required
def material_editar(request, id):
    """Editar material"""
    material = get_object_or_404(Material, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to edit items.')
        return redirect('materiais_lista')
    if role == 'user' and material.autor_email != request.user.email:
        messages.error(request, '🚫 You can only edit materials you created yourself.')
        return redirect('materiais_lista')

    if request.method == 'POST':
        material.titulo = request.POST.get('titulo')
        material.tipo = request.POST.get('tipo')
        material.topicos = request.POST.get('topicos', '')
        material.descricao = request.POST.get('descricao')
        material.url = request.POST.get('url', '')
        material.save()
        messages.success(request, '✅ Material updated successfully!')
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
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to delete items.')
        return redirect('materiais_lista')
    if role == 'user' and material.autor_email != request.user.email:
        messages.error(request, '🚫 You can only delete materials you created yourself.')
        return redirect('materiais_lista')

    material.delete()
    messages.success(request, '✅ Material deleted successfully!')
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

    favoritos_ids = _get_favoritos_ids(request.user.email, 'video')

    return render(request, 'core/videos.html', {
        'videos': videos,
        'query': query,
        'favoritos_ids': favoritos_ids,
        'user_role': get_user_role(request.user)
    })


@login_required
def video_novo(request):
    """Criar novo vídeo"""
    if get_user_role(request.user) == 'viewer':
        messages.error(request, '🚫 You do not have permission to add items.')
        return redirect('videos_lista')

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
        messages.success(request, '✅ Video added successfully!')
        return redirect('videos_lista')
    
    # GET: retornar para lista
    return redirect('videos_lista')


@login_required
def video_editar(request, id):
    """Editar vídeo"""
    video = get_object_or_404(Video, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to edit items.')
        return redirect('videos_lista')
    if role == 'user' and video.autor_email != request.user.email:
        messages.error(request, '🚫 You can only edit videos you created yourself.')
        return redirect('videos_lista')

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
        messages.success(request, '✅ Video updated successfully!')
        return redirect('videos_lista')
    
    # GET: retornar para lista
    return redirect('videos_lista')


@login_required
def video_excluir(request, id):
    """Excluir vídeo"""
    video = get_object_or_404(Video, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to delete items.')
        return redirect('videos_lista')
    if role == 'user' and video.autor_email != request.user.email:
        messages.error(request, '🚫 You can only delete videos you created yourself.')
        return redirect('videos_lista')

    video.delete()
    messages.success(request, '✅ Video deleted successfully!')
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

    favoritos_ids = _get_favoritos_ids(request.user.email, 'ferramenta')

    return render(request, 'core/ferramentas.html', {
        'ferramentas': ferramentas,
        'query': query,
        'favoritos_ids': favoritos_ids,
        'user_role': get_user_role(request.user)
    })


@login_required
def ferramenta_novo(request):
    """Criar nova ferramenta"""
    if get_user_role(request.user) == 'viewer':
        messages.error(request, '🚫 You do not have permission to add items.')
        return redirect('ferramentas_lista')

    if request.method == 'POST':
        try:
            allowed_ferr = AllowedEmail.objects.get(email=request.user.email)
            nome_autor_ferr = allowed_ferr.nome or request.user.email
        except AllowedEmail.DoesNotExist:
            nome_autor_ferr = request.user.email

        ferramenta = Ferramenta.objects.create(
            nome=request.POST.get('nome'),
            categoria=request.POST.get('categoria'),
            versao=request.POST.get('versao', ''),
            descricao=request.POST.get('descricao', ''),
            nivel=request.POST.get('nivel', ''),
            documentacao_link=request.POST.get('documentacao_link', ''),
            autor=nome_autor_ferr,
            autor_email=request.user.email,
            data_criacao=timezone.now()
        )
        messages.success(request, '✅ Tool added successfully!')
        return redirect('ferramentas_lista')
    
    # GET: mostrar formulário
    return render(request, 'core/ferramenta_form.html', {
        'user_role': get_user_role(request.user)
    })


@login_required
def ferramenta_editar(request, id):
    """Editar ferramenta"""
    ferramenta = get_object_or_404(Ferramenta, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to edit items.')
        return redirect('ferramentas_lista')
    if role == 'user' and ferramenta.autor_email != request.user.email:
        messages.error(request, '🚫 You can only edit tools you created yourself.')
        return redirect('ferramentas_lista')

    if request.method == 'POST':
        ferramenta.nome = request.POST.get('nome')
        ferramenta.categoria = request.POST.get('categoria')
        ferramenta.versao = request.POST.get('versao', '')
        ferramenta.descricao = request.POST.get('descricao')
        ferramenta.nivel = request.POST.get('nivel', '')
        ferramenta.documentacao_link = request.POST.get('documentacao_link', '')
        ferramenta.save()
        messages.success(request, '✅ Tool updated successfully!')
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
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to delete items.')
        return redirect('ferramentas_lista')
    if role == 'user' and ferramenta.autor_email != request.user.email:
        messages.error(request, '🚫 You can only delete tools you created yourself.')
        return redirect('ferramentas_lista')

    ferramenta.delete()
    messages.success(request, '✅ Tool deleted successfully!')
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
        messages.error(request, 'Access denied. Admins only.')
        return redirect('roadmap_index')
    
    progresso = get_object_or_404(RoadmapProgresso, id=id)
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            novo_progresso = data.get('progresso')
            if novo_progresso is not None:
                progresso.progresso = int(novo_progresso)
                progresso.save()
                messages.success(request, 'Progress updated!')
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
        messages.error(request, 'Access denied. Admins only.')
        return redirect('roadmap_index')
    
    if request.method == 'POST':
        # Validar campos obrigatórios
        titulo = request.POST.get('titulo', '').strip()
        responsavel = request.POST.get('responsavel', '').strip()
        prazo_str = request.POST.get('prazo', '').strip()
        
        if not titulo or not responsavel or not prazo_str:
            messages.error(request, '❌ Please fill in all required fields (Title, Owner, and Date).')
            return redirect('roadmap_index')
        
        # Converter prazo para DateField
        try:
            prazo = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, '❌ Invalid date. Use YYYY-MM-DD format.')
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
            messages.success(request, '✅ Delivery added successfully!')
        except Exception as e:
            messages.error(request, f'❌ Error creating delivery: {str(e)}')
        
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
        try:
            casos = CasoUso.objects.filter(
                autor_email=user.email,
                ativo=True
            ).count()
        except Exception:
            casos = 0

        try:
            videos = Video.objects.filter(autor_email=user.email).count()
        except Exception:
            videos = 0

        try:
            materiais = Material.objects.filter(autor_email=user.email).count()
        except Exception:
            materiais = 0

        try:
            ferramentas = Ferramenta.objects.filter(autor_email=user.email).count()
        except Exception:
            ferramentas = 0
        
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
        messages.error(request, 'Access denied. Admins only.')
        return redirect('dashboard')
    
    usuarios = AllowedEmail.objects.all().order_by('-data_criacao')
    
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
            messages.error(request, 'Email must be from the @artefact.com domain.')
            return redirect('admin_usuarios')
        
        # Verificar se já existe
        if AllowedEmail.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} is already registered.')
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
        
        messages.success(request, f'✅ User {email} added successfully!')
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
        messages.success(request, f'✅ User {email} updated successfully!')
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
        messages.error(request, 'You cannot delete your own user account.')
        return redirect('admin_usuarios')

    usuario.delete()
    messages.success(request, f'✅ User {email} deleted successfully!')
    return redirect('admin_usuarios')


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# ================== SNIPPETS ==================

@login_required
def snippets_lista(request):
    query = request.GET.get('q', '').strip()
    tag = request.GET.get('tag', '').strip()
    linguagem = request.GET.get('linguagem', '').strip()
    try:
        snippets = Snippet.objects.all().order_by('-data_criacao')
        if query:
            snippets = snippets.filter(
                Q(titulo__icontains=query) |
                Q(descricao__icontains=query) |
                Q(codigo__icontains=query) |
                Q(tags__icontains=query) |
                Q(autor__icontains=query)
            )
        if tag:
            snippets = snippets.filter(tags__icontains=tag)
        if linguagem:
            snippets = snippets.filter(linguagem__iexact=linguagem)
    except Exception:
        snippets = []

    try:
        linguagens = Snippet.objects.values_list('linguagem', flat=True).distinct().order_by('linguagem')
    except Exception:
        linguagens = []

    favoritos_ids = _get_favoritos_ids(request.user.email, 'snippet')

    return render(request, 'core/snippets.html', {
        'snippets': snippets,
        'query': query,
        'tag_filtro': tag,
        'linguagem_filtro': linguagem,
        'linguagens': linguagens,
        'favoritos_ids': favoritos_ids,
        'user_role': get_user_role(request.user),
    })


@login_required
def snippet_novo(request):
    if get_user_role(request.user) == 'viewer':
        messages.error(request, '🚫 You do not have permission to add items.')
        return redirect('snippets_lista')

    if request.method == 'POST':
        try:
            allowed = AllowedEmail.objects.get(email=request.user.email)
            nome_autor = allowed.nome or request.user.email
        except AllowedEmail.DoesNotExist:
            nome_autor = request.user.email

        Snippet.objects.create(
            titulo=request.POST.get('titulo'),
            linguagem=request.POST.get('linguagem'),
            codigo=request.POST.get('codigo'),
            descricao=request.POST.get('descricao', ''),
            tags=request.POST.get('tags', ''),
            autor=nome_autor,
            autor_email=request.user.email,
            data_criacao=timezone.now()
        )
        messages.success(request, '✅ Snippet added successfully!')
        return redirect('snippets_lista')
    return redirect('snippets_lista')


@login_required
def snippet_editar(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to edit.')
        return redirect('snippets_lista')
    if role == 'user' and snippet.autor_email != request.user.email:
        messages.error(request, '🚫 You can only edit snippets you created yourself.')
        return redirect('snippets_lista')

    if request.method == 'POST':
        snippet.titulo = request.POST.get('titulo')
        snippet.linguagem = request.POST.get('linguagem')
        snippet.codigo = request.POST.get('codigo')
        snippet.descricao = request.POST.get('descricao', '')
        snippet.tags = request.POST.get('tags', '')
        snippet.save()
        messages.success(request, '✅ Snippet updated!')
        return redirect('snippets_lista')
    return redirect('snippets_lista')


@login_required
def snippet_excluir(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    role = get_user_role(request.user)

    if role == 'viewer':
        messages.error(request, '🚫 You do not have permission to delete.')
        return redirect('snippets_lista')
    if role == 'user' and snippet.autor_email != request.user.email:
        messages.error(request, '🚫 You can only delete snippets you created yourself.')
        return redirect('snippets_lista')

    snippet.delete()
    messages.success(request, '✅ Snippet deleted!')
    return redirect('snippets_lista')


@login_required
def snippet_dados(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    return JsonResponse({
        'id': snippet.id,
        'titulo': snippet.titulo,
        'linguagem': snippet.linguagem,
        'codigo': snippet.codigo,
        'descricao': snippet.descricao,
        'tags': snippet.tags,
        'autor': snippet.autor,
    })


# ================== BUSCA GLOBAL ==================

@login_required
def busca_global(request):
    query = request.GET.get('q', '').strip()
    resultados = {}
    total = 0

    if query:
        casos = CasoUso.objects.filter(ativo=True).filter(
            Q(titulo__icontains=query) | Q(descricao__icontains=query) |
            Q(tecnologia__icontains=query) | Q(tags__icontains=query)
        )[:10]
        materiais = Material.objects.filter(
            Q(titulo__icontains=query) | Q(descricao__icontains=query) |
            Q(topicos__icontains=query)
        )[:10]
        videos = Video.objects.filter(
            Q(titulo__icontains=query) | Q(descricao__icontains=query) |
            Q(tema__icontains=query)
        )[:10]
        ferramentas = Ferramenta.objects.filter(
            Q(nome__icontains=query) | Q(descricao__icontains=query) |
            Q(categoria__icontains=query)
        )[:10]
        try:
            snippets = Snippet.objects.filter(
                Q(titulo__icontains=query) | Q(descricao__icontains=query) |
                Q(codigo__icontains=query) | Q(tags__icontains=query)
            )[:10]
            snippets_count = snippets.count()
        except Exception:
            snippets = []
            snippets_count = 0

        resultados = {
            'casos': casos,
            'materiais': materiais,
            'videos': videos,
            'ferramentas': ferramentas,
            'snippets': snippets,
        }
        total = casos.count() + materiais.count() + videos.count() + ferramentas.count() + snippets_count

    return render(request, 'core/busca_global.html', {
        'query': query,
        'resultados': resultados,
        'total': total,
        'user_role': get_user_role(request.user),
    })


# ================== FAVORITOS ==================

@login_required
def favoritos(request):
    try:
        favs = Favorito.objects.filter(usuario_email=request.user.email)
    except Exception:
        favs = []
    return render(request, 'core/favoritos.html', {
        'favoritos': favs,
        'user_role': get_user_role(request.user),
    })


@login_required
def favorito_toggle(request, content_type, object_id):
    """Adiciona ou remove um favorito (toggle). Retorna JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)

    # Validar content_type
    tipos_validos = ['caso', 'material', 'video', 'ferramenta', 'snippet']
    if content_type not in tipos_validos:
        return JsonResponse({'error': 'Tipo inválido'}, status=400)

    # Obter título do objeto
    titulo = ''
    try:
        if content_type == 'caso':
            obj = CasoUso.objects.get(id=object_id)
            titulo = obj.titulo
        elif content_type == 'material':
            obj = Material.objects.get(id=object_id)
            titulo = obj.titulo
        elif content_type == 'video':
            obj = Video.objects.get(id=object_id)
            titulo = obj.titulo
        elif content_type == 'ferramenta':
            obj = Ferramenta.objects.get(id=object_id)
            titulo = obj.nome
        elif content_type == 'snippet':
            obj = Snippet.objects.get(id=object_id)
            titulo = obj.titulo
    except Exception:
        return JsonResponse({'error': 'Objeto não encontrado'}, status=404)

    try:
        fav, created = Favorito.objects.get_or_create(
            usuario_email=request.user.email,
            content_type=content_type,
            object_id=object_id,
            defaults={'titulo': titulo}
        )
    except Exception:
        return JsonResponse({'error': 'Bookmarks table not ready. Run migrations.'}, status=500)

    if not created:
        fav.delete()
        return JsonResponse({'status': 'removed', 'message': 'Removed from bookmarks'})

    return JsonResponse({'status': 'added', 'message': 'Added to bookmarks!'})


# ================== CHANGELOG ==================

@login_required
def changelog(request):
    from datetime import timedelta
    periodo = request.GET.get('periodo', '7')
    try:
        dias = int(periodo)
    except ValueError:
        dias = 7

    desde = timezone.now() - timedelta(days=dias)

    novos_casos = CasoUso.objects.filter(ativo=True, data_criacao__gte=desde).order_by('-data_criacao')
    novos_materiais = Material.objects.filter(data_criacao__gte=desde).order_by('-data_criacao')
    novos_videos = Video.objects.filter(data_criacao__gte=desde).order_by('-data_criacao')
    novas_ferramentas = Ferramenta.objects.filter(data_criacao__gte=desde).order_by('-data_criacao')
    novos_snippets = Snippet.objects.filter(data_criacao__gte=desde).order_by('-data_criacao')

    total_novidades = (
        novos_casos.count() + novos_materiais.count() + novos_videos.count() +
        novas_ferramentas.count() + novos_snippets.count()
    )

    return render(request, 'core/changelog.html', {
        'novos_casos': novos_casos,
        'novos_materiais': novos_materiais,
        'novos_videos': novos_videos,
        'novas_ferramentas': novas_ferramentas,
        'novos_snippets': novos_snippets,
        'total_novidades': total_novidades,
        'periodo': dias,
        'user_role': get_user_role(request.user),
    })


# ================== PERFIL DE USUÁRIO ==================

def _calcular_badges(casos, videos, materiais, ferramentas, snippets):
    """Retorna lista de badges conquistados com base nas contribuições."""
    badges = []
    total = casos + videos + materiais + ferramentas + snippets

    if casos >= 1:
        badges.append({'icon': '📋', 'nome': 'Case Maker', 'desc': 'Registrou pelo menos 1 caso de uso'})
    if casos >= 5:
        badges.append({'icon': '🧠', 'nome': 'Case Expert', 'desc': '5+ casos de uso registrados'})
    if casos >= 10:
        badges.append({'icon': '🏛️', 'nome': 'Case Master', 'desc': '10+ casos de uso registrados'})
    if videos >= 1:
        badges.append({'icon': '🎬', 'nome': 'Video Creator', 'desc': 'Publicou pelo menos 1 vídeo'})
    if videos >= 5:
        badges.append({'icon': '📹', 'nome': 'Content Pro', 'desc': '5+ vídeos publicados'})
    if materiais >= 3:
        badges.append({'icon': '📚', 'nome': 'Bibliophile', 'desc': '3+ materiais compartilhados'})
    if ferramentas >= 2:
        badges.append({'icon': '🔧', 'nome': 'Tool Guru', 'desc': '2+ ferramentas catalogadas'})
    if snippets >= 3:
        badges.append({'icon': '💻', 'nome': 'Code Sharer', 'desc': '3+ snippets publicados'})
    if total >= 10:
        badges.append({'icon': '⭐', 'nome': 'Contributor', 'desc': '10+ contribuições no total'})
    if total >= 25:
        badges.append({'icon': '🚀', 'nome': 'Power User', 'desc': '25+ contribuições no total'})
    if total >= 50:
        badges.append({'icon': '🏆', 'nome': 'AE Legend', 'desc': '50+ contribuições — lenda do time!'})

    return badges


@login_required
def perfil_usuario(request, email):
    try:
        allowed = AllowedEmail.objects.get(email=email)
    except AllowedEmail.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard')

    # Contribuições
    casos = list(CasoUso.objects.filter(autor_email=email, ativo=True).order_by('-data_criacao'))
    videos = list(Video.objects.filter(autor_email=email).order_by('-data_criacao'))
    materiais = list(Material.objects.filter(autor_email=email).order_by('-data_criacao'))
    ferramentas = list(Ferramenta.objects.filter(autor_email=email).order_by('-data_criacao'))
    snippets_list = list(Snippet.objects.filter(autor_email=email).order_by('-data_criacao'))

    n_casos = len(casos)
    n_videos = len(videos)
    n_materiais = len(materiais)
    n_ferramentas = len(ferramentas)
    n_snippets = len(snippets_list)

    pontuacao = n_casos * 10 + n_videos * 15 + n_materiais * 3 + n_ferramentas * 8 + n_snippets * 5
    badges = _calcular_badges(n_casos, n_videos, n_materiais, n_ferramentas, n_snippets)

    # Perfil salvo
    perfil_tipo = None
    try:
        django_user = User.objects.get(email=email)
        onboarding = UserOnboarding.objects.get(user=django_user)
        perfil_tipo = onboarding.perfil_tipo
    except (User.DoesNotExist, UserOnboarding.DoesNotExist):
        pass

    is_own_profile = request.user.email == email

    return render(request, 'core/perfil_usuario.html', {
        'perfil_email': email,
        'perfil_nome': allowed.nome or email,
        'perfil_role': allowed.role,
        'perfil_tipo': perfil_tipo,
        'casos': casos,
        'videos': videos,
        'materiais': materiais,
        'ferramentas': ferramentas,
        'snippets': snippets_list,
        'n_casos': n_casos,
        'n_videos': n_videos,
        'n_materiais': n_materiais,
        'n_ferramentas': n_ferramentas,
        'n_snippets': n_snippets,
        'pontuacao': pontuacao,
        'badges': badges,
        'is_own_profile': is_own_profile,
        'user_role': get_user_role(request.user),
    })


# ================== SALVAR PERFIL TIPO ==================

@login_required
def salvar_perfil_tipo(request):
    if request.method == 'POST':
        perfil_tipo = request.POST.get('perfil_tipo', '').strip()
        tipos_validos = ['architect', 'gogetter', 'simplifier', 'systematic']
        if perfil_tipo not in tipos_validos:
            return JsonResponse({'error': 'Invalid profile type.'}, status=400)

        try:
            onboarding, _ = UserOnboarding.objects.get_or_create(user=request.user)
            onboarding.perfil_tipo = perfil_tipo
            onboarding.save()
        except Exception:
            pass
        return JsonResponse({'status': 'ok', 'message': 'Profile saved!'})
    return JsonResponse({'error': 'Method not allowed.'}, status=405)
)
    return JsonResponse({'error': 'Method not allowed.'}, status=405)
