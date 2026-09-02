"""
"What's New" newsletter — data collection, rendering and sending.

Reuses existing HUB infrastructure on purpose:
- Recipients come from the existing `AllowedEmail` table (no second user list).
- "New/updated content" uses the same `data_criacao` / `data_atualizacao` fields
  and filtering convention already used by the `changelog` view (core/views.py).
- Deep links reuse the same anchor ids already rendered by each list template
  (`#fav-caso-<id>`, `#card-cert-<id>`, etc.) — the same ones `favoritos.html`
  already links to.
- Display names reuse the same heuristic as `core.views._nome_de_exibicao`
  (duplicated here on purpose, exactly like migration 0022 already does, so this
  module never has to import the large `views.py` module).

See docs/newsletter_setup.md for how to configure sending + scheduling in Railway.
"""
import re
from datetime import timedelta

from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from core.models import (
    AllowedEmail,
    CasoUso,
    Material,
    Video,
    Ferramenta,
    Snippet,
    Certification,
)


def _nome_de_exibicao(email, allowed=None):
    """Same heuristic as core.views._nome_de_exibicao — duplicated on purpose (see module docstring)."""
    if allowed is None:
        allowed = AllowedEmail.objects.filter(email__iexact=email).first()
    if allowed and allowed.nome:
        return allowed.nome
    local_part = (email or '').split('@')[0]
    partes = re.split(r'[._\-+0-9]+', local_part)
    nome_derivado = ' '.join(p.capitalize() for p in partes if p)
    return nome_derivado or email


def _url(path):
    return f"{settings.SITE_URL.rstrip('/')}{path}"


def _truncate(text, length=170):
    text = (text or '').strip()
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + '…'


def _is_new(item, desde):
    criado = getattr(item, 'data_criacao', None)
    return bool(criado and criado >= desde)


def _secao_casos(desde, nomes_cache):
    qs = CasoUso.objects.filter(ativo=True).filter(
        Q(data_criacao__gte=desde) | Q(data_atualizacao__gte=desde)
    ).order_by('-data_criacao')
    itens = []
    for c in qs:
        itens.append({
            'id': c.id,
            'chave': 'casos',
            'secao': '📊 Use Cases',
            'titulo': c.titulo,
            'descricao': _truncate(c.descricao),
            'meta': f"{c.contexto} · {c.tecnologia}".strip(' ·'),
            'autor': nomes_cache(c.autor_email),
            'data': c.data_criacao,
            'status': 'New' if _is_new(c, desde) else 'Updated',
            'url': _url(f"{reverse('casos_lista')}#fav-caso-{c.id}"),
            'relevancia': f"A real case validated in {c.contexto or 'production'} — a great reference for a similar challenge.",
        })
    return {'chave': 'casos', 'titulo': '📊 Use Cases', 'itens': itens}


def _secao_materiais(desde, nomes_cache):
    qs = Material.objects.filter(
        Q(data_criacao__gte=desde) | Q(data_atualizacao__gte=desde)
    ).order_by('-data_criacao')
    itens = []
    for m in qs:
        itens.append({
            'id': m.id,
            'chave': 'materiais',
            'secao': '📚 Materials',
            'titulo': m.titulo,
            'descricao': _truncate(m.descricao),
            'meta': m.tipo or m.topicos or '',
            'autor': nomes_cache(m.autor_email),
            'data': m.data_criacao,
            'status': 'New' if _is_new(m, desde) else 'Updated',
            'url': _url(f"{reverse('materiais_lista')}#fav-material-{m.id}"),
            'relevancia': f"New material to go deeper on {m.topicos or m.tipo or 'a topic useful for your day-to-day'}.",
        })
    return {'chave': 'materiais', 'titulo': '📚 Materials', 'itens': itens}


def _secao_videos(desde, nomes_cache):
    qs = Video.objects.filter(
        Q(data_criacao__gte=desde) | Q(data_atualizacao__gte=desde)
    ).order_by('-data_criacao')
    itens = []
    for v in qs:
        duracao = f" · {v.duracao}" if v.duracao else ''
        itens.append({
            'id': v.id,
            'chave': 'videos',
            'secao': '🎬 Videos',
            'titulo': v.titulo,
            'descricao': _truncate(v.descricao),
            'meta': f"{v.tema}{duracao}".strip(' ·'),
            'autor': nomes_cache(v.autor_email),
            'data': v.data_criacao,
            'status': 'New' if _is_new(v, desde) else 'Updated',
            'url': _url(f"{reverse('videos_lista')}#fav-video-{v.id}"),
            'relevancia': f"Learn at your own pace: video content on {v.tema or 'a relevant topic'}.",
        })
    return {'chave': 'videos', 'titulo': '🎬 Videos', 'itens': itens}


def _secao_ferramentas(desde, nomes_cache):
    qs = Ferramenta.objects.filter(
        Q(data_criacao__gte=desde) | Q(data_atualizacao__gte=desde)
    ).order_by('-data_criacao')
    itens = []
    for f in qs:
        itens.append({
            'id': f.id,
            'chave': 'ferramentas',
            'secao': '🔧 Tools',
            'titulo': f.nome,
            'descricao': _truncate(f.descricao),
            'meta': f.categoria or '',
            'autor': nomes_cache(f.autor_email),
            'data': f.data_criacao,
            'status': 'New' if _is_new(f, desde) else 'Updated',
            'url': _url(f"{reverse('ferramentas_lista')}#fav-ferramenta-{f.id}"),
            'relevancia': f"A {f.categoria or 'productivity'} tool just got cataloged — worth checking if it solves what you need.",
        })
    return {'chave': 'ferramentas', 'titulo': '🔧 Tools', 'itens': itens}


def _secao_snippets(desde, nomes_cache):
    qs = Snippet.objects.filter(data_criacao__gte=desde).order_by('-data_criacao')
    itens = []
    for s in qs:
        itens.append({
            'id': s.id,
            'chave': 'snippets',
            'secao': '💻 Snippets',
            'titulo': s.titulo,
            'descricao': _truncate(s.descricao),
            'meta': s.linguagem or '',
            'autor': nomes_cache(s.autor_email),
            'data': s.data_criacao,
            'status': 'New',
            'url': _url(f"{reverse('snippets_lista')}#fav-snippet-{s.id}"),
            'relevancia': f"Ready-to-use {s.linguagem or 'code'} — copy it, adapt it, save yourself some time.",
        })
    return {'chave': 'snippets', 'titulo': '💻 Snippets', 'itens': itens}


def _secao_certificacoes(desde):
    qs = Certification.objects.filter(ativo=True, data_criacao__gte=desde).order_by('-data_criacao')
    itens = []
    for c in qs:
        itens.append({
            'id': c.id,
            'chave': 'certificacoes',
            'secao': '🎓 Certifications',
            'titulo': c.titulo,
            'descricao': _truncate(c.descricao),
            'meta': f"{c.fornecedor} · {c.get_nivel_display()}",
            'autor': None,
            'data': c.data_criacao,
            'status': 'New',
            'url': _url(f"{reverse('certificacoes_lista')}#card-cert-{c.id}"),
            'relevancia': f"Another certification step in {c.categoria} — a good next milestone on your growth path.",
        })
    return {'chave': 'certificacoes', 'titulo': '🎓 Certifications', 'itens': itens}


def selecionar_destaques(secoes, limite=1):
    """Picks the `limite` most recently created/updated items across all sections —
    simple, deterministic, and always genuinely the newest things. Used both for the
    newsletter's single highlight and the What's New page's Featured section (public,
    reused by core.views.changelog)."""
    todos = [item for secao in secoes for item in secao['itens']]
    todos.sort(key=lambda i: i['data'] or timezone.now(), reverse=True)
    return todos[:limite]


def _escolher_destaque(secoes):
    destaques = selecionar_destaques(secoes, limite=1)
    return destaques[0] if destaques else None


def coletar_novidades(dias=None):
    """Returns a dict describing everything created/updated in the last `dias` days."""
    dias = dias or settings.NEWSLETTER_PERIOD_DAYS
    agora = timezone.now()
    desde = agora - timedelta(days=dias)

    # Small in-memory cache so we don't hit AllowedEmail once per item.
    _cache = {}

    def nomes_cache(email):
        if not email:
            return None
        if email not in _cache:
            _cache[email] = _nome_de_exibicao(email)
        return _cache[email]

    secoes_brutas = [
        _secao_casos(desde, nomes_cache),
        _secao_materiais(desde, nomes_cache),
        _secao_videos(desde, nomes_cache),
        _secao_ferramentas(desde, nomes_cache),
        _secao_snippets(desde, nomes_cache),
        _secao_certificacoes(desde),
    ]
    secoes = [s for s in secoes_brutas if s['itens']]
    total_itens = sum(len(s['itens']) for s in secoes)

    return {
        'secoes': secoes,
        'total_itens': total_itens,
        'destaque': _escolher_destaque(secoes) if secoes else None,
        'desde': desde,
        'ate': agora,
        'dias': dias,
    }


def _get_recipients(recipients_override=None):
    """Same AllowedEmail table used everywhere else in the HUB — no second user list."""
    if recipients_override:
        return list(dict.fromkeys(recipients_override))  # de-dupe, preserve order
    if settings.NEWSLETTER_TEST_MODE:
        return list(settings.NEWSLETTER_TEST_RECIPIENTS)
    return list(
        AllowedEmail.objects.exclude(email='').values_list('email', flat=True).distinct()
    )


def periodo_label(desde, ate):
    return f"Last {(ate - desde).days} days · {desde.strftime('%b %d')} – {ate.strftime('%b %d, %Y')}"


def montar_contexto_email(novidades, nome_destinatario=None):
    return {
        'secoes': novidades['secoes'],
        'total_itens': novidades['total_itens'],
        'destaque': novidades['destaque'],
        'periodo_label': periodo_label(novidades['desde'], novidades['ate']),
        'nome': nome_destinatario,
        'hub_url': _url(reverse('changelog')),  # What's New is the HUB's home page
        'hub_url_casos': _url(f"{reverse('casos_lista')}"),
        'hub_url_snippets': _url(f"{reverse('snippets_lista')}"),
        'hub_url_materiais': _url(f"{reverse('materiais_lista')}"),
    }


def _assunto(total_itens):
    if total_itens == 0:
        return "💜 The Hub misses you — got something to share?"
    return f"🚀 What's New on the AE Hub — {total_itens} update{'s' if total_itens != 1 else ''}"


def enviar_newsletter(dias=None, dry_run=False, recipients_override=None):
    """
    Orchestrates the whole flow: collect novidades, render the email, send it.

    Returns a summary dict — used by the management command's stdout and by tests.
    """
    novidades = coletar_novidades(dias)
    recipients = _get_recipients(recipients_override)

    modo = 'override' if recipients_override else ('test' if settings.NEWSLETTER_TEST_MODE else 'all_allowed_emails')

    resumo = {
        'modo': modo,
        'total_itens': novidades['total_itens'],
        'secoes': [(s['titulo'], len(s['itens'])) for s in novidades['secoes']],
        'destinatarios': recipients,
        'dry_run': dry_run,
        'enviados': 0,
    }

    if not recipients:
        resumo['aviso'] = 'No recipients resolved — nothing sent.'
        return resumo

    assunto = _assunto(novidades['total_itens'])

    if dry_run:
        # Render once just to prove the template works, but send nothing.
        allowed_map = {a.email.lower(): a for a in AllowedEmail.objects.filter(email__in=recipients)}
        exemplo_nome = _nome_de_exibicao(recipients[0], allowed_map.get(recipients[0].lower()))
        contexto = montar_contexto_email(novidades, nome_destinatario=exemplo_nome)
        html = render_to_string('core/email/newsletter.html', contexto)
        resumo['assunto'] = assunto
        resumo['preview_html_length'] = len(html)
        return resumo

    allowed_map = {a.email.lower(): a for a in AllowedEmail.objects.filter(email__in=recipients)}
    connection = get_connection()
    connection.open()
    enviados = 0
    try:
        for email in recipients:
            allowed = allowed_map.get(email.lower())
            nome = _nome_de_exibicao(email, allowed)
            contexto = montar_contexto_email(novidades, nome_destinatario=nome)
            html = render_to_string('core/email/newsletter.html', contexto)
            texto = strip_tags(html)

            msg = EmailMultiAlternatives(
                subject=assunto,
                body=texto,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[email],
                connection=connection,
            )
            msg.attach_alternative(html, 'text/html')
            msg.send()
            enviados += 1
    finally:
        connection.close()

    resumo['assunto'] = assunto
    resumo['enviados'] = enviados
    return resumo
