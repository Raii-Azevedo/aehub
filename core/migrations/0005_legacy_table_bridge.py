from django.db import migrations


TABLE_RENAMES = [
    ('AllowedEmail', 'core_allowedemail', 'allowed_emails'),
    ('CasoFeedback', 'core_casofeedback', 'feedback_casos'),
    ('CasoUso', 'core_casouso', 'casos_uso'),
    ('Ferramenta', 'core_ferramenta', 'ferramentas'),
    ('Material', 'core_material', 'materiais'),
    ('RoadmapEntrega', 'core_roadmapentrega', 'roadmap_entregas'),
    ('RoadmapFase', 'core_roadmapfase', 'roadmap_fases'),
    ('RoadmapProgresso', 'core_roadmapprogresso', 'roadmap_progresso'),
    ('Snippet', 'core_snippet', 'snippets'),
    ('Video', 'core_video', 'videos'),
]


def sync_legacy_tables(apps, schema_editor):
    connection = schema_editor.connection

    with connection.cursor() as cursor:
        existing_tables = set(connection.introspection.table_names(cursor))

    if 'core_aemes' in existing_tables:
        schema_editor.execute('DROP TABLE IF EXISTS core_aemes')
        existing_tables.remove('core_aemes')

    for model_name, old_table, new_table in TABLE_RENAMES:
        if old_table not in existing_tables or new_table in existing_tables:
            continue

        model = apps.get_model('core', model_name)
        schema_editor.alter_db_table(model, old_table, new_table)
        existing_tables.remove(old_table)
        existing_tables.add(new_table)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_expand_video_link_field'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(sync_legacy_tables, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.DeleteModel(
                    name='AEMes',
                ),
                migrations.AlterModelOptions(
                    name='allowedemail',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='casofeedback',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='casouso',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='ferramenta',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='material',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='roadmapentrega',
                    options={'managed': False, 'ordering': ['-data_criacao']},
                ),
                migrations.AlterModelOptions(
                    name='roadmapfase',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='roadmapprogresso',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='snippet',
                    options={'managed': False},
                ),
                migrations.AlterModelOptions(
                    name='video',
                    options={'managed': False, 'ordering': ['-data_criacao']},
                ),
                migrations.AlterModelTable(
                    name='allowedemail',
                    table='allowed_emails',
                ),
                migrations.AlterModelTable(
                    name='casofeedback',
                    table='feedback_casos',
                ),
                migrations.AlterModelTable(
                    name='casouso',
                    table='casos_uso',
                ),
                migrations.AlterModelTable(
                    name='ferramenta',
                    table='ferramentas',
                ),
                migrations.AlterModelTable(
                    name='material',
                    table='materiais',
                ),
                migrations.AlterModelTable(
                    name='roadmapentrega',
                    table='roadmap_entregas',
                ),
                migrations.AlterModelTable(
                    name='roadmapfase',
                    table='roadmap_fases',
                ),
                migrations.AlterModelTable(
                    name='roadmapprogresso',
                    table='roadmap_progresso',
                ),
                migrations.AlterModelTable(
                    name='snippet',
                    table='snippets',
                ),
                migrations.AlterModelTable(
                    name='video',
                    table='videos',
                ),
            ],
        ),
    ]