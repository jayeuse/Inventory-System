"""
Django management command to initialize the database
Creates database if it doesn't exist and runs migrations
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Command(BaseCommand):
    help = 'Initialize database: create DB if not exists and run migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-migrations',
            action='store_true',
            help='Skip running migrations',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('DATABASE INITIALIZATION'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        # Get database settings
        db_settings = settings.DATABASES['default']
        db_name = db_settings['NAME']
        db_user = db_settings['USER']
        db_password = db_settings['PASSWORD']
        db_host = db_settings['HOST']
        db_port = db_settings['PORT']

        # Step 1: Create database if it doesn't exist
        self.stdout.write('\n1. Checking if database exists...')
        try:
            # Connect to PostgreSQL server (to 'postgres' database)
            conn = psycopg2.connect(
                dbname='postgres',
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                [db_name]
            )
            exists = cursor.fetchone()

            if exists:
                self.stdout.write(self.style.SUCCESS(f'   ✅ Database "{db_name}" already exists'))
            else:
                # Create database
                self.stdout.write(f'   Creating database "{db_name}"...')
                cursor.execute(f'CREATE DATABASE {db_name}')
                self.stdout.write(self.style.SUCCESS(f'   ✅ Database "{db_name}" created successfully'))

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Error: {e}'))
            return

        # Step 2: Run migrations
        if not options['skip_migrations']:
            self.stdout.write('\n2. Running migrations...')
            from django.core.management import call_command
            try:
                call_command('migrate', verbosity=1)
                self.stdout.write(self.style.SUCCESS('   ✅ Migrations completed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'   ❌ Migration error: {e}'))
                return
        else:
            self.stdout.write('\n2. Skipping migrations (--skip-migrations flag)')

        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('✅ DATABASE INITIALIZATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(f'\nDatabase: {db_name}')
        self.stdout.write(f'Host: {db_host}:{db_port}')
        self.stdout.write('\nYour inventory system is ready to use! 🚀')
