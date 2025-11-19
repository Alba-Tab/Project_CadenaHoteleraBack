"""
Utilidades para el sistema de backups.
Funciones reutilizables para todos los comandos de backup.
"""
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from django.conf import settings

# Ruta de PostgreSQL en Windows
PG_BIN_PATH = r"C:\Program Files\PostgreSQL\17\bin"


def get_backup_config():
    """
    Obtiene la configuración de backups desde .env
    """
    return {
        'enabled': settings.env.bool('BACKUP_ENABLED', default=True),
        'frequency': settings.env.str('BACKUP_FREQUENCY', default='daily'),
        'time': settings.env.str('BACKUP_TIME', default='03:00'),
        'retention_days': settings.env.int('BACKUP_RETENTION_DAYS', default=7),
        'storage': settings.env.str('BACKUP_STORAGE', default='local'),
    }


def get_db_credentials():
    """
    Obtiene las credenciales de la base de datos desde settings
    """
    db = settings.DATABASES['default']
    return {
        'host': db.get('HOST', 'localhost'),
        'port': str(db.get('PORT', '5432')),
        'user': db.get('USER', 'postgres'),
        'password': db.get('PASSWORD', ''),
        'database': db.get('NAME', ''),
    }


def create_backup_directory(backup_type='full'):
    """
    Crea las carpetas necesarias para almacenar backups
    
    Args:
        backup_type: 'full' o 'tenant'
    
    Returns:
        Path: Ruta completa de la carpeta
    """
    base_dir = Path(settings.BASE_DIR) / 'media' / 'backups' / backup_type
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def generate_backup_filename(backup_type='full', schema_name=None):
    """
    Genera un nombre de archivo para el backup
    
    Args:
        backup_type: 'full' o 'tenant'
        schema_name: Nombre del schema (solo para backups de tenant)
    
    Returns:
        str: Nombre del archivo
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if backup_type == 'full':
        return f'full_backup_{timestamp}.sql'
    elif schema_name:
        return f'{schema_name}_{timestamp}.sql'
    else:
        return f'backup_{timestamp}.sql'


def execute_pg_dump(output_file, schema_name=None):
    """
    Ejecuta pg_dump para crear un backup
    
    Args:
        output_file: Ruta completa del archivo de salida
        schema_name: Nombre del schema (None para backup completo)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    db = get_db_credentials()
    
    # Ruta completa de pg_dump
    pg_dump_exe = os.path.join(PG_BIN_PATH, 'pg_dump.exe')
    
    # Comando base
    cmd = [
        pg_dump_exe,
        '-h', db['host'],
        '-p', db['port'],
        '-U', db['user'],
        '-F', 'p',  # Formato plain SQL
        '-f', str(output_file),
    ]
    
    # Si se especifica un schema, agregarlo
    if schema_name:
        cmd.extend(['-n', schema_name])
    
    # Agregar el nombre de la base de datos
    cmd.append(db['database'])
    
    # Configurar variable de entorno para password
    env = os.environ.copy()
    env['PGPASSWORD'] = db['password']
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600  # Timeout de 1 hora
        )
        
        if result.returncode == 0:
            file_size = os.path.getsize(output_file)
            return True, f'Backup exitoso. Tamaño: {file_size / 1024 / 1024:.2f} MB'
        else:
            error_msg = result.stderr or 'Error desconocido'
            return False, f'Error en pg_dump: {error_msg}'
            
    except subprocess.TimeoutExpired:
        return False, 'Timeout: El backup tardó más de 1 hora'
    except FileNotFoundError:
        return False, f'pg_dump no encontrado en {PG_BIN_PATH}. Verifica la ruta de PostgreSQL'
    except Exception as e:
        return False, f'Error inesperado: {str(e)}'


def execute_pg_restore(input_file, schema_name=None):
    """
    Ejecuta psql para restaurar un backup
    
    Args:
        input_file: Ruta completa del archivo a restaurar
        schema_name: Nombre del schema (None para restauración completa)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    db = get_db_credentials()
    
    # Rutas completas de psql
    psql_exe = os.path.join(PG_BIN_PATH, 'psql.exe')
    
    # Configurar variable de entorno para password
    env = os.environ.copy()
    env['PGPASSWORD'] = db['password']
    
    try:
        # Si es un schema específico, primero eliminarlo y recrearlo
        if schema_name:
            drop_cmd = [
                psql_exe,
                '-h', db['host'],
                '-p', db['port'],
                '-U', db['user'],
                '-d', db['database'],
                '-c', f'DROP SCHEMA IF EXISTS {schema_name} CASCADE; CREATE SCHEMA {schema_name};'
            ]
            subprocess.run(drop_cmd, env=env, check=True)
        
        # Restaurar el backup
        restore_cmd = [
            psql_exe,
            '-h', db['host'],
            '-p', db['port'],
            '-U', db['user'],
            '-d', db['database'],
            '-f', str(input_file)
        ]
        
        result = subprocess.run(
            restore_cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=3600
        )
        
        if result.returncode == 0:
            return True, 'Restauración completada exitosamente'
        else:
            return False, f'Error en restauración: {result.stderr}'
            
    except subprocess.TimeoutExpired:
        return False, 'Timeout: La restauración tardó más de 1 hora'
    except Exception as e:
        return False, f'Error inesperado: {str(e)}'


def cleanup_old_backups(backup_dir, retention_days=7):
    """
    Elimina backups más antiguos que retention_days
    
    Args:
        backup_dir: Carpeta de backups
        retention_days: Días de retención
    
    Returns:
        tuple: (deleted_count: int, freed_space: int)
    """
    if not isinstance(backup_dir, Path):
        backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        return 0, 0
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0
    freed_space = 0
    
    for file in backup_dir.glob('*.sql'):
        file_time = datetime.fromtimestamp(file.stat().st_mtime)
        
        if file_time < cutoff_date:
            file_size = file.stat().st_size
            try:
                file.unlink()
                deleted_count += 1
                freed_space += file_size
            except Exception as e:
                print(f'Error eliminando {file.name}: {e}')
    
    return deleted_count, freed_space


def get_backup_stats(backup_dir):
    """
    Obtiene estadísticas de los backups en una carpeta
    
    Args:
        backup_dir: Carpeta de backups
    
    Returns:
        dict: Estadísticas
    """
    if not isinstance(backup_dir, Path):
        backup_dir = Path(backup_dir)
    
    if not backup_dir.exists():
        return {
            'total_backups': 0,
            'total_size': 0,
            'oldest': None,
            'newest': None,
        }
    
    backups = list(backup_dir.glob('*.sql'))
    
    if not backups:
        return {
            'total_backups': 0,
            'total_size': 0,
            'oldest': None,
            'newest': None,
        }
    
    total_size = sum(f.stat().st_size for f in backups)
    oldest = min(backups, key=lambda f: f.stat().st_mtime)
    newest = max(backups, key=lambda f: f.stat().st_mtime)
    
    return {
        'total_backups': len(backups),
        'total_size': total_size,
        'total_size_mb': total_size / 1024 / 1024,
        'oldest': datetime.fromtimestamp(oldest.stat().st_mtime),
        'newest': datetime.fromtimestamp(newest.stat().st_mtime),
    }
