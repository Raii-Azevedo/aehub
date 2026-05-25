"""
Migration 0013 — Add macrotopico column to all five content tables.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_videos_all_text'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE casos_uso   ADD COLUMN IF NOT EXISTS macrotopico VARCHAR(100) NOT NULL DEFAULT '';
                ALTER TABLE materiais   ADD COLUMN IF NOT EXISTS macrotopico VARCHAR(100) NOT NULL DEFAULT '';
                ALTER TABLE videos      ADD COLUMN IF NOT EXISTS macrotopico VARCHAR(100) NOT NULL DEFAULT '';
                ALTER TABLE ferramentas ADD COLUMN IF NOT EXISTS macrotopico VARCHAR(100) NOT NULL DEFAULT '';
                ALTER TABLE snippets    ADD COLUMN IF NOT EXISTS macrotopico VARCHAR(100) NOT NULL DEFAULT '';
            """,
            reverse_sql="""
                ALTER TABLE casos_uso   DROP COLUMN IF EXISTS macrotopico;
                ALTER TABLE materiais   DROP COLUMN IF EXISTS macrotopico;
                ALTER TABLE videos      DROP COLUMN IF EXISTS macrotopico;
                ALTER TABLE ferramentas DROP COLUMN IF EXISTS macrotopico;
                ALTER TABLE snippets    DROP COLUMN IF EXISTS macrotopico;
            """,
        ),
    ]
