import importlib.util
import os

from django.db import migrations


def _load_certifications_data():
    """
    Reuse the CERTIFICATIONS list from migration 0020 instead of duplicating
    all 57 records here.
    """
    path = os.path.join(os.path.dirname(__file__), '0020_reclassify_ae_certifications.py')
    spec = importlib.util.spec_from_file_location('_mig0020_data', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CERTIFICATIONS


def fix_missing_certifications(apps, schema_editor):
    """
    Migration 0020 archived the old catalog (ativo = FALSE) and then inserted
    the 57 new certifications, guarding each insert with:
        WHERE NOT EXISTS (SELECT 1 FROM certifications WHERE titulo = %s)

    That guard checked ALL rows regardless of `ativo`, so any new certification
    that happened to share an exact title with an old (now archived/inactive)
    row was silently skipped. 26 of the 57 titles matched an old title, so
    only 31 ended up inserted instead of 57.

    This migration inserts exactly those missing certifications, guarding
    correctly this time on `ativo = TRUE` so it only skips certs that are
    already active (i.e. already successfully inserted), not archived ones.
    """
    from django.db import connection
    certifications = _load_certifications_data()
    with connection.cursor() as cursor:
        for cert in certifications:
            cursor.execute("""
                INSERT INTO certifications
                    (titulo, fornecedor, categoria, nivel, prioridade, tipo_certificacao,
                     descricao, tags, link_oficial, link_curso, ativo, data_criacao)
                SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE, NOW()
                WHERE NOT EXISTS (
                    SELECT 1 FROM certifications WHERE titulo = %s AND ativo = TRUE
                )
            """, [
                cert['titulo'], cert['fornecedor'], cert['categoria'],
                cert['nivel'], cert['prioridade'], cert['tipo_certificacao'],
                cert['descricao'], cert['tags'], cert['link_oficial'], cert['link_curso'],
                cert['titulo'],
            ])


def reverse_fix_missing_certifications(apps, schema_editor):
    # No-op: reversing would require knowing exactly which rows this
    # migration inserted vs. 0020 already did, which isn't worth tracking.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_reclassify_ae_certifications'),
    ]

    operations = [
        migrations.RunPython(fix_missing_certifications, reverse_code=reverse_fix_missing_certifications),
    ]
