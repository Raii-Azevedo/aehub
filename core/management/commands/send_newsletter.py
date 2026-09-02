from django.core.management.base import BaseCommand

from core.newsletter_utils import enviar_newsletter


class Command(BaseCommand):
    help = (
        "Sends the 'What's New' newsletter with HUB updates from the last N days "
        "(default: settings.NEWSLETTER_PERIOD_DAYS, currently 15). "
        "See docs/newsletter_setup.md for scheduling + go-live instructions."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias', type=int, default=None,
            help='Override the lookback window in days (default: NEWSLETTER_PERIOD_DAYS).',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Collect + render the newsletter but do not send any email.',
        )
        parser.add_argument(
            '--to', type=str, default=None,
            help=(
                'Comma-separated recipient override, for one-off manual tests. '
                'Ignores NEWSLETTER_TEST_MODE / AllowedEmail entirely when set.'
            ),
        )

    def handle(self, *args, **options):
        recipients_override = None
        if options['to']:
            recipients_override = [e.strip() for e in options['to'].split(',') if e.strip()]

        resumo = enviar_newsletter(
            dias=options['dias'],
            dry_run=options['dry_run'],
            recipients_override=recipients_override,
        )

        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING("📬 Newsletter — What's New"))
        self.stdout.write(f"  Mode:            {resumo['modo']}")
        self.stdout.write(f"  Items found:     {resumo['total_itens']}")
        for titulo, n in resumo.get('secoes', []):
            self.stdout.write(f"    - {titulo}: {n}")
        self.stdout.write(f"  Recipients:      {', '.join(resumo['destinatarios']) or '(none)'}")

        if resumo.get('aviso'):
            self.stdout.write(self.style.WARNING(f"  ⚠️  {resumo['aviso']}"))
            return

        if resumo['dry_run']:
            self.stdout.write(self.style.WARNING(
                f"  Dry-run — nothing sent. Subject would be: \"{resumo.get('assunto', '')}\" "
                f"(rendered {resumo.get('preview_html_length', 0)} chars of HTML)."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"  ✅ Sent {resumo['enviados']} email(s) with subject \"{resumo['assunto']}\"."
            ))
        self.stdout.write('')
