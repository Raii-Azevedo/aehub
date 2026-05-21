import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Aguarda o banco de dados estar disponível antes de continuar o startup.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-retries',
            type=int,
            default=30,
            help='Número máximo de tentativas antes de desistir (default: 30)',
        )
        parser.add_argument(
            '--wait',
            type=int,
            default=2,
            help='Segundos entre cada tentativa (default: 2)',
        )

    def handle(self, *args, **options):
        max_retries = options['max_retries']
        wait_seconds = options['wait']

        self.stdout.write('⏳ Aguardando o banco de dados...')

        for attempt in range(1, max_retries + 1):
            try:
                conn = connections['default']
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS(
                    f'✅ Banco disponível após {attempt} tentativa(s).'
                ))
                return
            except OperationalError:
                self.stdout.write(
                    f'   Tentativa {attempt}/{max_retries} — banco ainda não está pronto. '
                    f'Aguardando {wait_seconds}s...'
                )
                time.sleep(wait_seconds)

        self.stderr.write(self.style.ERROR(
            f'❌ Banco não ficou disponível após {max_retries} tentativas. Abortando.'
        ))
        raise SystemExit(1)
