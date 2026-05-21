"""
Migration 0007 — Restore autor_email (and autor text) columns

Migration 0002 removed autor_email from casos_uso, materiais,
ferramentas, and videos as part of an earlier refactor.
The current models and views expect those columns to exist.
Migration 0001 also created casos_uso.autor as a ForeignKey
(stored as autor_id), but the current model treats it as a plain
TextField — so we add an explicit 'autor' text column as well.

All columns are added with ADD COLUMN IF NOT EXISTS so the migration
is idempotent (safe to run against databases that already have the
columns from an older schema).
"""

from django.db import migrations


ADD_SQL = """
ALTER TABLE casos_uso   ADD COLUMN IF NOT EXISTS autor_email  VARCHAR(254) NOT NULL DEFAULT '';
ALTER TABLE casos_uso   ADD COLUMN IF NOT EXISTS autor        VARCHAR(255) NOT NULL DEFAULT '';
ALTER TABLE materiais   ADD COLUMN IF NOT EXISTS autor_email  VARCHAR(254) NOT NULL DEFAULT '';
ALTER TABLE ferramentas ADD COLUMN IF NOT EXISTS autor_email  VARCHAR(254) NOT NULL DEFAULT '';
ALTER TABLE videos      ADD COLUMN IF NOT EXISTS autor_email  VARCHAR(254) NOT NULL DEFAULT '';
ALTER TABLE snippets    ADD COLUMN IF NOT EXISTS autor_email  VARCHAR(254) NOT NULL DEFAULT '';
"""

REVERSE_SQL = """
ALTER TABLE casos_uso   DROP COLUMN IF EXISTS autor_email;
ALTER TABLE casos_uso   DROP COLUMN IF EXISTS autor;
ALTER TABLE materiais   DROP COLUMN IF EXISTS autor_email;
ALTER TABLE ferramentas DROP COLUMN IF EXISTS autor_email;
ALTER TABLE videos      DROP COLUMN IF EXISTS autor_email;
ALTER TABLE snippets    DROP COLUMN IF EXISTS autor_email;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_user_onboarding'),
    ]

    operations = [
        migrations.RunSQL(
            sql=ADD_SQL,
            reverse_sql=REVERSE_SQL,
        ),
    ]
