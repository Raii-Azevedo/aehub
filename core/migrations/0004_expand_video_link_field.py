from django.db import migrations


def expand_video_link_field(apps, schema_editor):
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        tables = set(connection.introspection.table_names(cursor))
        if 'videos' not in tables:
            return

        if connection.vendor == 'postgresql':
            cursor.execute("ALTER TABLE videos ALTER COLUMN youtube_id TYPE TEXT")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_snippet'),
    ]

    operations = [
        migrations.RunPython(expand_video_link_field, migrations.RunPython.noop),
    ]