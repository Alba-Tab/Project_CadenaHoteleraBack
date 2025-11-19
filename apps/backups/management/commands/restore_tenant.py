from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess, os

class Command(BaseCommand):
    help = "Restaura un tenant desde un archivo SQL."

    def add_arguments(self, parser):
        parser.add_argument("schema_name", type=str, help="Schema del tenant a restaurar")
        parser.add_argument("file", type=str, help="Ruta del archivo .sql")

    def handle(self, *args, **options):
        schema = options["schema_name"]
        file_path = options["file"]

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR("Archivo no encontrado."))
            return

        db = settings.DATABASES["default"]
        env = os.environ.copy()
        env["PGPASSWORD"] = db["PASSWORD"]

        self.stdout.write(f"⚠️ Eliminando y recreando schema '{schema}'...")
        drop_cmd = [
            "psql", "-h", db["HOST"], "-p", str(db["PORT"]), "-U", db["USER"], "-d", db["NAME"],
            "-c", f"DROP SCHEMA IF EXISTS {schema} CASCADE; CREATE SCHEMA {schema};"
        ]
        subprocess.run(drop_cmd, env=env)

        self.stdout.write(f"🔁 Restaurando datos de {file_path}...")
        restore_cmd = [
            "psql", "-h", db["HOST"], "-p", str(db["PORT"]), "-U", db["USER"], "-d", db["NAME"],
            "-f", file_path
        ]
        subprocess.run(restore_cmd, env=env)
        self.stdout.write(self.style.SUCCESS(f"✅ Restauración completada para schema '{schema}'"))
