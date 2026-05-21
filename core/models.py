from django.db import models
from django.contrib.auth.models import User




# ============================================
# BASE MODEL (PADRÃO)
# ============================================
class BaseModel(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================
# EMAILS AUTORIZADOS
# ============================================
class AllowedEmail(models.Model):
    email = models.EmailField(primary_key=True)
    role = models.CharField(max_length=10, default='viewer')
    added_by = models.CharField(max_length=255, blank=True, null=True)
    # These columns exist in the DB (created by early migrations).
    # Declaring them here lets the ORM populate them automatically on save.
    data_criacao = models.DateTimeField(auto_now_add=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'allowed_emails'
        managed = False  # 🔥 ESSENCIAL — Django does not create/alter this table

    def __str__(self):
        return f"{self.email} ({self.role})"


# ============================================
# CASOS DE USO
# ============================================
class CasoUso(models.Model):
    titulo = models.TextField()
    contexto = models.TextField()
    tecnologia = models.TextField()
    descricao = models.TextField()
    resultado = models.TextField()
    tags = models.TextField(blank=True, null=True)

    autor = models.TextField()  # Nome do autor
    autor_email = models.EmailField()
    ativo = models.BooleanField()

    data_criacao = models.DateTimeField()
    data_atualizacao = models.DateTimeField()

    class Meta:
        db_table = 'casos_uso'  # 👈 NOME REAL
        managed = False     # 👈 NÃO DEIXA DJANGO MEXER

    def __str__(self):
        return self.titulo


# ============================================
# FEEDBACK DOS CASOS
# ============================================
class CasoFeedback(models.Model):
    caso_id = models.IntegerField()  # 🔥 FK manual (não usar ForeignKey Django)
    usuario_email = models.EmailField()

    avaliacao = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    utilidade = models.TextField(blank=True, null=True)

    data_criacao = models.DateTimeField()

    class Meta:
        db_table = 'feedback_casos'  # 👈 nome real
        managed = False             # 👈 ESSENCIAL


# ============================================
# MATERIAIS
# ============================================
class Material(models.Model):
    titulo = models.TextField()
    tipo = models.TextField()
    topicos = models.TextField(blank=True, null=True)
    descricao = models.TextField()
    url = models.TextField(blank=True, null=True)

    autor = models.TextField()
    autor_email = models.EmailField()

    data_criacao = models.DateTimeField()

    class Meta:
        db_table = 'materiais'
        managed = False


# ============================================
# ROADMAP (USANDO BANCO EXISTENTE - STREAMLIT)
# ============================================
class RoadmapFase(models.Model):
    fase = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    data_prevista = models.DateField()

    # 🔥 CAMPOS QUE EXISTEM NO BANCO
    entregas = models.TextField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'roadmap_fases'
        managed = False

    def __str__(self):
        return self.fase


# --------------------------------------------

class RoadmapProgresso(models.Model):
    pilar = models.CharField(max_length=255)
    progresso = models.IntegerField()
    meta = models.CharField(max_length=255, null=True, blank=True)
    atualizado_por = models.CharField(max_length=255)

    data_atualizacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'roadmap_progresso'
        managed = False

    def __str__(self):
        return self.pilar


# --------------------------------------------
class RoadmapEntrega(models.Model):
    titulo = models.CharField(max_length=500)
    responsavel = models.CharField(max_length=255)
    prazo = models.DateField()

    prioridade = models.CharField(max_length=10)
    status = models.CharField(max_length=20)

    criado_por = models.CharField(max_length=255)
    data_criacao = models.DateTimeField()

    class Meta:
        db_table = 'roadmap_entregas'
        managed = False
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo
    
    
# ============================================
# SNIPPET
# ============================================

class Snippet(models.Model):
    titulo = models.TextField()
    linguagem = models.TextField()
    codigo = models.TextField()
    descricao = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)

    autor = models.TextField()
    autor_email = models.EmailField()

    data_criacao = models.DateTimeField()

    class Meta:
        db_table = 'snippets'
        managed = False


# ============================================
# FERRAMENTAS
# ============================================
class Ferramenta(models.Model):
    nome = models.TextField()
    categoria = models.TextField()
    versao = models.TextField(blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    nivel = models.TextField(blank=True, null=True)
    documentacao_link = models.TextField(blank=True, null=True)

    autor = models.TextField()
    autor_email = models.EmailField()

    data_criacao = models.DateTimeField()

    class Meta:
        db_table = 'ferramentas'
        managed = False

# ============================================
# VÍDEOS (USANDO BANCO EXISTENTE)
# ============================================

class Video(models.Model):
    titulo = models.CharField(max_length=500)
    descricao = models.TextField(blank=True, null=True)

    tema = models.CharField(max_length=100)

    nivel = models.CharField(max_length=20)

    duracao = models.CharField(max_length=20, blank=True, null=True)
    youtube_id = models.TextField(blank=True, null=True)
    thumbnail_url = models.TextField(blank=True, null=True)

    autor = models.CharField(max_length=255)
    autor_email = models.EmailField()  # Adicionado

    data_criacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'videos'     # 🔥 nome real
        managed = False         # 🔥 não deixar Django mexer
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo


# ============================================
# ONBOARDING (FORMULÁRIO DE BOAS-VINDAS)
# ============================================
class UserOnboarding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding')
    onboarding_completo = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_onboarding'

    def __str__(self):
        return f"{self.user.email} - {'ok' if self.onboarding_completo else 'pendente'}"