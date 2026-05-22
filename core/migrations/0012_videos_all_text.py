"""
Migration 0012 — Convert ALL text/varchar columns in videos to TEXT.

Migrations 0009 and 0011 targeted specific columns but the legacy table
may still have other varchar(20) constraints.  This migration uses
information_schema to find every character-varying column in the videos
table and ALTER them all to TEXT, so no INSERT can ever overflow again.
"""

from django.db import migrations


EXPAND_SQL = """
DO $$
DECLARE
    col TEXT;
BEGIN
    FOR col IN
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'videos'
          AND data_type IN ('character varying', 'character')
    LOOP
        EXECUTE format(
            'ALTER TABLE videos ALTER COLUMN %I TYPE TEXT USING %I::TEXT',
            col, col
        );
    END LOOP;
END $$;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_expand_video_duracao'),
    ]

    operations = [
        migrations.RunSQL(
            sql=EXPAND_SQL,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
