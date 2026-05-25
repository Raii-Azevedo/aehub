from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_add_macrotopico'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS certifications (
                    id              SERIAL PRIMARY KEY,
                    titulo          VARCHAR(200) NOT NULL,
                    fornecedor      VARCHAR(100) NOT NULL,
                    categoria       VARCHAR(100) NOT NULL DEFAULT '',
                    nivel           VARCHAR(50)  NOT NULL DEFAULT 'Junior',
                    prioridade      VARCHAR(30)  NOT NULL DEFAULT 'recommended',
                    descricao       TEXT         NOT NULL DEFAULT '',
                    tags            VARCHAR(500) NOT NULL DEFAULT '',
                    link_oficial    VARCHAR(500) NOT NULL DEFAULT '',
                    link_curso      VARCHAR(500) NOT NULL DEFAULT '',
                    ativo           BOOLEAN      NOT NULL DEFAULT TRUE,
                    data_criacao    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS certification_progress (
                    id               SERIAL PRIMARY KEY,
                    usuario_email    VARCHAR(254) NOT NULL,
                    certification_id INTEGER      NOT NULL REFERENCES certifications(id) ON DELETE CASCADE,
                    status           VARCHAR(20)  NOT NULL DEFAULT 'in_progress',
                    data_atualizacao TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
                    UNIQUE (usuario_email, certification_id)
                );
            """,
            reverse_sql="""
                DROP TABLE IF EXISTS certification_progress;
                DROP TABLE IF EXISTS certifications;
            """,
        ),
    ]
