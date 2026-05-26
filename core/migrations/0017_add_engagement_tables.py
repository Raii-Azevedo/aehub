from django.db import migrations


class Migration(migrations.Migration):
    """
    Creates content_likes and content_ratings tables for the engagement system.
    Both tables are managed=False in Django — Railway's makemigrations will not
    try to re-create them because the model Meta declares managed=False.
    """

    dependencies = [
        ('core', '0016_fix_favorito_db_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE IF NOT EXISTS content_likes (
                id          SERIAL PRIMARY KEY,
                usuario_email VARCHAR(254) NOT NULL,
                content_type  VARCHAR(20)  NOT NULL,
                object_id     INTEGER      NOT NULL,
                data_criacao  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                UNIQUE (usuario_email, content_type, object_id)
            );
            CREATE INDEX IF NOT EXISTS idx_content_likes_type_obj
                ON content_likes (content_type, object_id);

            CREATE TABLE IF NOT EXISTS content_ratings (
                id            SERIAL PRIMARY KEY,
                usuario_email VARCHAR(254) NOT NULL,
                content_type  VARCHAR(20)  NOT NULL,
                object_id     INTEGER      NOT NULL,
                rating        SMALLINT     NOT NULL CHECK (rating BETWEEN 1 AND 5),
                data_criacao  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                data_atualizacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                UNIQUE (usuario_email, content_type, object_id)
            );
            CREATE INDEX IF NOT EXISTS idx_content_ratings_type_obj
                ON content_ratings (content_type, object_id);
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS content_ratings;
            DROP TABLE IF EXISTS content_likes;
            """,
        ),
    ]
