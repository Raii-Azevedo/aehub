# AE Knowledge Hub

Plataforma interna desenvolvida em Django para centralizar conhecimento, materiais, vídeos, ferramentas e roadmap de iniciativas de IA/engenharia. O sistema também inclui onboarding, controle de acesso por e-mail autorizado, ranking de contribuição e autenticação com Google Workspace.

## Visão geral

O projeto foi estruturado para funcionar sobre uma base de dados já existente, utilizando vários modelos com `managed = False`. Isso permite integrar tabelas legadas sem recriá-las pelo Django.

### Principais funcionalidades

- Dashboard com visão geral da plataforma
- Cadastro e consulta de casos de uso
- Biblioteca de materiais e vídeos
- Catálogo de ferramentas
- Roadmap com fases, progresso e entregas
- Ranking de gamificação por contribuições
- Boas-vindas/onboarding no primeiro acesso
- Login por e-mail autorizado e Google OAuth
- Interface multilíngue: Português, Inglês e Espanhol

## Stack

- Python 3.11
- Django 5
- PostgreSQL via `DATABASE_URL`
- Gunicorn
- WhiteNoise
- Django Allauth
- Deploy preparado para Railway

## Estrutura principal

```text
config/   Configurações do projeto Django
core/     App principal com views, models, templates e estáticos
locale/   Arquivos de tradução
notebooks/ Apoio e comandos auxiliares
```

## Requisitos

Antes de executar localmente, configure:

- Python 3.11
- Ambiente virtual ativo
- Banco PostgreSQL acessível
- Variável `DATABASE_URL`

## Variáveis de ambiente

Crie um arquivo `.env` ou configure as variáveis no ambiente:

```env
SECRET_KEY=dev-secret-key
DEBUG=True
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
```

> Observação: sem `DATABASE_URL`, a aplicação não inicia.

## Instalação local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

A aplicação ficará disponível em:

- http://127.0.0.1:8000/

## Fluxo de acesso

1. O usuário acessa a tela de login.
2. O e-mail precisa existir na tabela de e-mails autorizados.
3. Após autenticação, o usuário passa pelo onboarding inicial.
4. Em seguida, acessa o dashboard e os módulos da plataforma.

## Rotas principais

- `/login/` — login local por e-mail autorizado
- `/dashboard/` — painel principal
- `/casos/` — casos de uso
- `/materiais/` — materiais
- `/videos/` — vídeos
- `/ferramentas/` — ferramentas
- `/roadmap/` — roadmap
- `/ranking/` — gamificação
- `/admin/usuarios/` — administração de usuários autorizados

## Deploy

O projeto já contém arquivos para deploy:

- `Procfile`
- `runtime.txt`

Comando web configurado:

```bash
python manage.py migrate && gunicorn config.wsgi
```

## Licença

Uso interno / privado.
