import re

from django.db import migrations


def _nome_de_exibicao(nome_allowed, email):
    """
    Mirrors core.views._nome_de_exibicao: prefer the saved AllowedEmail.nome,
    otherwise derive a 'Nome Sobrenome' guess from the email's local part
    (e.g. 'raissa.azevedo' -> 'Raissa Azevedo') instead of the email itself.
    """
    if nome_allowed:
        return nome_allowed
    local_part = (email or '').split('@')[0]
    partes = re.split(r'[._\-+0-9]+', local_part)
    nome = ' '.join(p.capitalize() for p in partes if p)
    return nome or email


# Content tables that carry both a free-text `autor` display field and an
# `autor_email` field. Before this fix, several creation views fell back to
# writing the raw email into `autor` whenever AllowedEmail.nome was blank
# (which was common, since nothing used to populate it), so some existing
# rows show an email address as their "author" instead of a name.
TABELAS = ['casos_uso', 'materiais', 'videos', 'ferramentas', 'snippets']


def fix_autor_fields(apps, schema_editor):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT email, nome FROM allowed_emails")
        nomes_por_email = {email: nome for email, nome in cursor.fetchall()}

        for tabela in TABELAS:
            cursor.execute(f"SELECT id, autor, autor_email FROM {tabela}")
            rows = cursor.fetchall()
            for row_id, autor, autor_email in rows:
                if not autor_email:
                    continue
                # Only touch rows that actually look like the bug: the
                # display name is empty or contains an '@' (i.e. is/looks
                # like an email). Custom author names typed by admins are
                # left untouched.
                looks_like_email = (not autor) or ('@' in autor)
                if not looks_like_email:
                    continue

                nome_correto = _nome_de_exibicao(nomes_por_email.get(autor_email, ''), autor_email)
                if nome_correto and nome_correto != autor:
                    cursor.execute(
                        f"UPDATE {tabela} SET autor = %s WHERE id = %s",
                        [nome_correto, row_id],
                    )


def reverse_noop(apps, schema_editor):
    # Not reversible: the original (incorrect) values aren't recorded anywhere.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_fix_missing_certifications'),
    ]

    operations = [
        migrations.RunPython(fix_autor_fields, reverse_code=reverse_noop),
    ]
