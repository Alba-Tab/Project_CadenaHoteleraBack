from django.core.mail import EmailMessage
from django.conf import settings
from io import BytesIO
from typing import Tuple

def send_report_email(
    recipient_email: str,
    report_name: str,
    report_data: Tuple[bytes, str, str],  # (content, content_type, filename)
    subject: str = None,
    message: str = ""
):
    """
    Envía un reporte por email como adjunto.
    
    Args:
        recipient_email: Email del destinatario
        report_name: Nombre del reporte
        report_data: Tupla con (bytes, content_type, filename)
        subject: Asunto personalizado (opcional)
        message: Mensaje adicional (opcional)
    """
    content, content_type, filename = report_data
    
    # Asunto por defecto si no se proporciona
    if not subject:
        subject = f"Reporte: {report_name}"
    
    # Mensaje base
    email_body = f"""
Estimado/a usuario/a,

Adjunto encontrará el reporte solicitado: {report_name}

{message}

Saludos cordiales,
Sistema de Reportes
Hotel Management System
    """.strip()
    
    # Crear email con adjunto
    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    
    # Adjuntar el archivo
    email.attach(filename, content, content_type)
    
    # Enviar
    email.send()
    
    return True