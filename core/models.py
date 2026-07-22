from django.db import models
from django.contrib.auth.models import User


# ============================================
# BASE MODEL
# ============================================
class BaseModel(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


# ============================================
# EMAILS AUTORIZADOS
# ============================================
class AllowedEmail(models.Model):
    # The real DB column order (from the error log):
    # id, email, role, nome, added_by, avatar, data_criacao, data_atualizacao, user_id
    email = models.EmailField(primary_key=True)
    role = models.CharField(max_length=10, default='viewer')
    nome = models.CharField(max_length=255, blank=True, default='')  # NOT NULL in DB
    added_by = models.CharField(max_length=255, blank=True, null=True)
    # avatar is an ImageField in DB but we treat it as nullable text to avoid media deps
    avatar = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'allowed_emails'
        managed = False

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
    autor = models.TextField()
    autor_email = models.EmailField()
    autor_id = models.IntegerField(null=True, blank=True)  # FK to auth_user (NOT NULL in DB — must supply)
    macrotopico = models.CharField(max_length=100, blank=True, default='')
    ativo = models.BooleanField()
    data_criacao = models.DateTimeField()
    data_atualizacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'casos_uso'
        managed = False

    def __str__(self):
        return self.titulo


# ============================================
# FEEDBACK DOS CASOS
# ============================================
class CasoFeedback(models.Model):
    caso_id = models.IntegerField()
    usuario_email = models.EmailField()
    avaliacao = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)
    utilidade = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField()

    class Meta:
        db_table = 'feedback_casos'
        managed = False


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
    macrotopico = models.CharField(max_length=100, blank=True, default='')
    data_criacao = models.DateTimeField()
    data_atualizacao = models.DateTimeField(null=True, blank=True)  # NOT NULL in DB — must supply on create

    class Meta:
        db_table = 'materiais'
        managed = False


# ============================================
# ROADMAP
# ============================================
class RoadmapFase(models.Model):
    fase = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    data_prevista = models.DateField()
    entregas = models.TextField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'roadmap_fases'
        managed = False

    def __str__(self):
        return self.fase


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
    macrotopico = models.CharField(max_length=100, blank=True, default='')
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
    macrotopico = models.CharField(max_length=100, blank=True, default='')
    data_criacao = models.DateTimeField()
    data_atualizacao = models.DateTimeField(null=True, blank=True)  # NOT NULL in DB — added by migration 0002

    class Meta:
        db_table = 'ferramentas'
        managed = False


# ============================================
# VIDEOS
# ============================================
class Video(models.Model):
    titulo = models.CharField(max_length=500)
    descricao = models.TextField(blank=True, null=True)
    tema = models.CharField(max_length=500)   # expanded from legacy varchar(20) via migration 0009
    nivel = models.CharField(max_length=100)  # expanded from legacy varchar(20) via migration 0009
    duracao = models.TextField(blank=True, null=True)  # expanded from varchar(20) via migration 0011
    youtube_id = models.TextField(blank=True, null=True)
    thumbnail_url = models.TextField(blank=True, default='')  # NOT NULL in DB
    autor = models.CharField(max_length=255)
    autor_email = models.EmailField()
    macrotopico = models.CharField(max_length=100, blank=True, default='')
    data_criacao = models.DateTimeField(null=True, blank=True)
    data_atualizacao = models.DateTimeField(null=True, blank=True)  # added by migration 0002

    class Meta:
        db_table = 'videos'
        managed = False
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo


# ============================================
# ONBOARDING
# ============================================
class UserOnboarding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding')
    onboarding_completo = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)
    perfil_tipo = models.CharField(max_length=50, blank=True, null=True)  # architect, gogetter, simplifier, systematic

    class Meta:
        db_table = 'user_onboarding'

    def __str__(self):
        return f"{self.user.email} - {'ok' if self.onboarding_completo else 'pendente'}"


# ============================================
# FAVORITOS
# ============================================
class Favorito(models.Model):
    CONTENT_TYPES = [
        ('caso', 'Caso de Uso'),
        ('material', 'Material'),
        ('video', 'Vídeo'),
        ('ferramenta', 'Ferramenta'),
        ('snippet', 'Snippet'),
    ]
    usuario_email = models.EmailField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'favoritos'
        unique_together = ('usuario_email', 'content_type', 'object_id')
        managed = False

    def __str__(self):
        return f"{self.usuario_email} → {self.content_type}:{self.object_id}"


# ============================================
# CERTIFICATIONS
# ============================================
class Certification(models.Model):
    CATEGORIA_CHOICES = [
        ('Analytics Engineering Roadmap', 'Analytics Engineering Roadmap'),
        ('Data Pipelines & Engineering', 'Data Pipelines & Engineering'),
        ('Cloud Architecture', 'Cloud Architecture'),
        ('BI Tooling & DataViz', 'BI Tooling & DataViz'),
        ('Machine Learning & Advanced Analytics', 'Machine Learning & Advanced Analytics'),
        ('Gen AI Solutions', 'Gen AI Solutions'),
        ('DevOps', 'DevOps'),
        ('UI/UX Designer', 'UI/UX Designer'),
    ]
    NIVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Mid-Level', 'Mid-Level'),
        ('Senior', 'Senior'),
    ]
    PRIORIDADE_CHOICES = [
        ('recommended', '⭐ Recommended'),
        ('complementary', '🧠 Complementary'),
        ('foundations', '📚 Foundations'),
    ]
    TIPO_CHOICES = [
        ('paid_exam', '💳 Paid Exam'),
        ('free_course', '🆓 Free Course'),
    ]

    titulo = models.CharField(max_length=200)
    fornecedor = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100, choices=CATEGORIA_CHOICES)
    nivel = models.CharField(max_length=50, choices=NIVEL_CHOICES)
    prioridade = models.CharField(max_length=30, choices=PRIORIDADE_CHOICES, default='recommended')
    tipo_certificacao = models.CharField(max_length=30, choices=TIPO_CHOICES, default='paid_exam')
    descricao = models.TextField()
    tags = models.CharField(max_length=500, blank=True, default='')
    link_oficial = models.URLField(max_length=500)
    link_curso = models.URLField(max_length=500, blank=True, default='')
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certifications'
        managed = False
        ordering = ['categoria', 'nivel', 'titulo']

    def __str__(self):
        return self.titulo


class CertificationProgress(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    usuario_email = models.EmailField()
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='progress_entries')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'certification_progress'
        managed = False
        unique_together = ('usuario_email', 'certification')

    def __str__(self):
        return f"{self.usuario_email} → {self.certification.titulo}: {self.status}"


# ============================================
# CONTENT ENGAGEMENT (Likes + Ratings)
# ============================================
class ContentLike(models.Model):
    CONTENT_TYPES = [
        ('caso', 'Caso de Uso'),
        ('material', 'Material'),
        ('video', 'Vídeo'),
        ('ferramenta', 'Ferramenta'),
        ('snippet', 'Snippet'),
    ]
    usuario_email = models.EmailField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content_likes'
        unique_together = ('usuario_email', 'content_type', 'object_id')
        managed = False

    def __str__(self):
        return f"{self.usuario_email} liked {self.content_type}:{self.object_id}"


class ContentRating(models.Model):
    CONTENT_TYPES = [
        ('caso', 'Caso de Uso'),
        ('material', 'Material'),
        ('video', 'Vídeo'),
        ('ferramenta', 'Ferramenta'),
        ('snippet', 'Snippet'),
    ]
    usuario_email = models.EmailField()
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.IntegerField()
    rating = models.IntegerField()  # 1–5
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'content_ratings'
        unique_together = ('usuario_email', 'content_type', 'object_id')
        managed = False

    def __str__(self):
        return f"{self.usuario_email} rated {self.content_type}:{self.object_id} → {self.rating}"
