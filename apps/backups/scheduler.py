"""
Scheduler para backups automáticos usando APScheduler
Programa backups diarios, semanales y mensuales según configuración
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

# Instancia global del scheduler
scheduler = None


def backup_full_daily():
    """Ejecuta backup completo diario"""
    try:
        logger.info('Ejecutando backup completo diario automático')
        call_command('backup_full', '--type=auto_daily')
        logger.info('Backup diario completado')
    except Exception as e:
        logger.error(f'Error en backup diario: {e}')


def backup_full_weekly():
    """Ejecuta backup completo semanal"""
    try:
        logger.info('Ejecutando backup completo semanal automático')
        call_command('backup_full', '--type=auto_weekly')
        logger.info('Backup semanal completado')
    except Exception as e:
        logger.error(f'Error en backup semanal: {e}')


def backup_full_monthly():
    """Ejecuta backup completo mensual"""
    try:
        logger.info('Ejecutando backup completo mensual automático')
        call_command('backup_full', '--type=auto_monthly')
        logger.info('Backup mensual completado')
    except Exception as e:
        logger.error(f'Error en backup mensual: {e}')


def cleanup_backups_auto():
    """Ejecuta limpieza automática de backups antiguos"""
    try:
        logger.info('Ejecutando limpieza automática de backups')
        call_command('cleanup_backups')
        logger.info('Limpieza completada')
    except Exception as e:
        logger.error(f'Error en limpieza: {e}')


def get_backup_time():
    """Obtiene la hora de backup desde .env"""
    try:
        backup_time = settings.env.str('BACKUP_TIME', default='03:00')
        hour, minute = backup_time.split(':')
        return int(hour), int(minute)
    except:
        return 3, 0  # Default: 3:00 AM


def start_scheduler():
    """
    Inicia el scheduler de backups automáticos
    """
    global scheduler
    
    # Verificar si los backups están habilitados
    backup_enabled = settings.env.bool('BACKUP_ENABLED', default=False)
    
    if not backup_enabled:
        logger.info('Backups automáticos deshabilitados (BACKUP_ENABLED=False)')
        return
    
    # Solo en producción (DEBUG=False)
    if settings.DEBUG:
        logger.info('Backups automáticos deshabilitados en modo DEBUG')
        return
    
    # Si ya está corriendo, no iniciar de nuevo
    if scheduler is not None and scheduler.running:
        logger.info('Scheduler ya está en ejecución')
        return
    
    # Crear scheduler
    scheduler = BackgroundScheduler()
    
    # Obtener configuración
    frequency = settings.env.str('BACKUP_FREQUENCY', default='daily')
    hour, minute = get_backup_time()
    
    logger.info(f'Iniciando scheduler de backups - Frecuencia: {frequency}, Hora: {hour:02d}:{minute:02d}')
    
    # Programar según frecuencia configurada
    if frequency == 'daily':
        # Backup diario a la hora configurada
        scheduler.add_job(
            backup_full_daily,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='backup_daily',
            name='Backup Completo Diario',
            replace_existing=True
        )
        logger.info(f'✅ Backup diario programado a las {hour:02d}:{minute:02d}')
    
    elif frequency == 'weekly':
        # Backup semanal los domingos
        scheduler.add_job(
            backup_full_weekly,
            trigger=CronTrigger(day_of_week='sun', hour=hour, minute=minute),
            id='backup_weekly',
            name='Backup Completo Semanal',
            replace_existing=True
        )
        logger.info(f'✅ Backup semanal programado los domingos a las {hour:02d}:{minute:02d}')
    
    elif frequency == 'monthly':
        # Backup mensual el día 1 de cada mes
        scheduler.add_job(
            backup_full_monthly,
            trigger=CronTrigger(day=1, hour=hour, minute=minute),
            id='backup_monthly',
            name='Backup Completo Mensual',
            replace_existing=True
        )
        logger.info(f'✅ Backup mensual programado el día 1 de cada mes a las {hour:02d}:{minute:02d}')
    
    # Limpieza automática (cada día a las 2:00 AM)
    scheduler.add_job(
        cleanup_backups_auto,
        trigger=CronTrigger(hour=2, minute=0),
        id='cleanup_backups',
        name='Limpieza de Backups Antiguos',
        replace_existing=True
    )
    logger.info('✅ Limpieza automática programada diariamente a las 02:00')
    
    # Iniciar scheduler
    scheduler.start()
    logger.info('🚀 Scheduler de backups iniciado correctamente')


def stop_scheduler():
    """
    Detiene el scheduler
    """
    global scheduler
    
    if scheduler is not None and scheduler.running:
        scheduler.shutdown()
        scheduler = None
        logger.info('Scheduler de backups detenido')


def get_scheduled_jobs():
    """
    Retorna la lista de trabajos programados
    """
    if scheduler is None or not scheduler.running:
        return []
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time,
            'trigger': str(job.trigger)
        })
    
    return jobs
