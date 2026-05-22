"""
Migration 0008 — Adiciona modelo Favorito e campo perfil_tipo ao UserOnboarding
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_restore_autor_email_columns'),
    ]

    operations = [
        # Campo perfil_tipo no UserOnboarding
        migrations.AddField(
            model_name='useronboarding',
            name='perfil_tipo',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        # Tabela Favoritos
        migrations.CreateModel(
            name='Favorito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario_email', models.EmailField()),
                ('content_type', models.CharField(
                    choices=[
                        ('caso', 'Caso de Uso'),
                        ('material', 'Material'),
                        ('video', 'Vídeo'),
                        ('ferramenta', 'Ferramenta'),
                        ('snippet', 'Snippet'),
                    ],
                    max_length=20,
                )),
                ('object_id', models.IntegerField()),
                ('titulo', models.CharField(blank=True, max_length=500)),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'favoritos',
                'ordering': ['-data_criacao'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='favorito',
            unique_together={('usuario_email', 'content_type', 'object_id')},
        ),
    ]
