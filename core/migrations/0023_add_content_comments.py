from django.db import migrations


class Migration(migrations.Migration):
    """
    Creates the content_comments table — generic comments on any content type
    (caso/material/video/ferramenta/snippet), mirroring the content_likes /
    content_ratings pattern from migration 0017. managed=False on the model,
    so Django will never try to auto-manage this table.
    """

    dependencies = [
        ('core', '0022_fix_author_names_showing_email'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS content_comments (
                id            SERIAL PRIMARY KEY,
                usuario_email VARCHAR(254) NOT NULL,
                content_type  VARCHAR(20)  NOT NULL,
                object_id     INTEGER      NOT NULL,
                texto         TEXT         NOT NULL,
                data_criacao  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
            );
            CREATE INDEX IF NOT EXISTS idx_content_comments_type_obj
                ON content_comments (content_type, object_id);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS content_comments;
            """,
        ),
    ]
