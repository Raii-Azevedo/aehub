from django.db import migrations


class Migration(migrations.Migration):
    """
    Restores db_table = 'favoritos' on the Favorito model.
    Django's internal state lost this when managed=False was set without
    an explicit db_table, causing it to query 'core_favorito' instead.
    This migration records the correct table name in the migration state
    so makemigrations stops re-generating it on every deploy.
    No actual DDL is needed — the table already exists as 'favoritos'.
    """

    dependencies = [
        ('core', '0015_seed_certifications'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='favorito',
            table='favoritos',
        ),
    ]
