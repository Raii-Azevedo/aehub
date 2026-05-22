"""
Migration 0009 — Expand constrained Video columns and add data_atualizacao
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_favorito_perfil_tipo'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # Expand tema: legacy table had varchar(20), form accepts free text
                "ALTER TABLE videos ALTER COLUMN tema TYPE VARCHAR(500);",
                # Expand nivel: legacy varchar(20) — 'Intermediate' fits but expand for safety
                "ALTER TABLE videos ALTER COLUMN nivel TYPE VARCHAR(100);",
                # Add data_atualizacao if it doesn't exist (added by migration 0002 in managed mode)
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name='videos' AND column_name='data_atualizacao'
                    ) THEN
                        ALTER TABLE videos ADD COLUMN data_atualizacao TIMESTAMP WITH TIME ZONE;
                    END IF;
                END $$;
                """,
                # Backfill nulls so existing rows don't break
                "UPDATE videos SET data_atualizacao = data_criacao WHERE data_atualizacao IS NULL;",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
