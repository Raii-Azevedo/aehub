from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_fix_video_columns'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='favorito',
            name='titulo',
        ),
    ]
