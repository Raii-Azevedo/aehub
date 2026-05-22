"""
Migration 0011 — Expand remaining constrained columns in the videos table.

Migration 0009 expanded tema and nivel, but duracao (varchar 20) and
potentially autor/titulo from the legacy table are still constrained.
Expand all of them to TEXT so free-text form inputs cannot overflow.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_favorito_titulo'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE videos ALTER COLUMN duracao  TYPE TEXT;
                ALTER TABLE videos ALTER COLUMN autor    TYPE TEXT;
                ALTER TABLE videos ALTER COLUMN titulo   TYPE TEXT;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
