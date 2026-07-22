from django.db import migrations


class Migration(migrations.Migration):
    """
    1) Adds a 'tipo_certificacao' column to certifications (Paid Exam vs Free Course),
       matching the Type column from the "AE Suggested Certifications List" spreadsheet.
    2) Simplifies the level scale from Beginner/Junior/Mid-level/Senior to the
       Beginner/Intermediate/Advanced scale used by that spreadsheet, remapping
       existing rows accordingly (Junior -> Beginner, Mid-level -> Intermediate,
       Senior -> Advanced).
    """

    dependencies = [
        ('core', '0017_add_engagement_tables'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE certifications
                    ADD COLUMN IF NOT EXISTS tipo_certificacao VARCHAR(30) NOT NULL DEFAULT 'paid_exam';

                UPDATE certifications SET nivel = 'Beginner'     WHERE nivel = 'Junior';
                UPDATE certifications SET nivel = 'Intermediate' WHERE nivel = 'Mid-level';
                UPDATE certifications SET nivel = 'Advanced'     WHERE nivel = 'Senior';
            """,
            reverse_sql="""
                UPDATE certifications SET nivel = 'Junior'    WHERE nivel = 'Beginner';
                UPDATE certifications SET nivel = 'Mid-level' WHERE nivel = 'Intermediate';
                UPDATE certifications SET nivel = 'Senior'    WHERE nivel = 'Advanced';

                ALTER TABLE certifications DROP COLUMN IF EXISTS tipo_certificacao;
            """,
        ),
    ]
