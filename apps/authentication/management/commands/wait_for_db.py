"""Management command: wait for database to be ready."""
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for database to be available"

    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")
        db_conn = None
        retries = 0
        while not db_conn:
            try:
                db_conn = connections["default"]
                db_conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS("✓ Database available!"))
            except OperationalError:
                retries += 1
                if retries > 30:
                    self.stdout.write(self.style.ERROR("Database not available after 30 retries."))
                    raise
                self.stdout.write(f"  Database unavailable, retry {retries}/30...")
                time.sleep(5)
