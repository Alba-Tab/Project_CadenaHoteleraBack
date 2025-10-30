from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from django.utils.text import slugify
from .exporters import export_docx, export_xlsx, export_pdf


def enviar_reporte_por_email(rows, report_name, format, recipient_email, subject, message=None, tenant=None):
    """
    Servicio genérico para enviar reportes por email.

    Args:
        rows: Lista de diccionarios con los datos del reporte
        report_name: Nombre del reporte (usado para el nombre del archivo)
        format: Formato del archivo ('xlsx', 'docx', 'pdf')
        recipient_email: Email del destinatario
        subject: Asunto del email
        message: Mensaje del cuerpo del email (opcional)
        tenant: Objeto tenant (opcional) - Si se proporciona y tiene configuración de email, se usa esa

    Returns:
        dict: {"success": True/False, "message": "..."}
    """
    try:
        # Generar el archivo según el formato
        fname = slugify(report_name)

        if format == "xlsx":
            blob, content_type, filename = export_xlsx(rows, fname)
        elif format == "docx":
            blob, content_type, filename = export_docx(rows, report_name, fname)
        elif format == "pdf":
            blob, content_type, filename = export_pdf(rows, report_name, fname)
        else:
            return {
                "success": False,
                "message": f"Formato no soportado: {format}"
            }

        # Determinar configuración de email a usar
        connection = None
        from_email = None

        # Verificar si el tenant tiene configuración de email propia
        if tenant and hasattr(tenant, 'email_host_user') and tenant.email_host_user:
            # Usar configuración del tenant
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                host=getattr(tenant, 'email_host', 'smtp.gmail.com'),
                port=getattr(tenant, 'email_port', 587),
                username=tenant.email_host_user,
                password=getattr(tenant, 'email_host_password', ''),
                use_tls=getattr(tenant, 'email_use_tls', True),
                fail_silently=False,
            )
            from_email = getattr(tenant, 'default_from_email', tenant.email_host_user)
        else:
            # Usar configuración del sistema (.env)
            connection = None  # Usa la configuración por defecto de Django
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

        # Crear el email
        email = EmailMessage(
            subject=subject,
            body=message or f"Adjunto encontrarás el reporte '{report_name}' solicitado.",
            from_email=from_email,
            to=[recipient_email],
            connection=connection,
        )

        # Adjuntar el archivo
        email.attach(filename, blob, content_type)

        # Enviar el email
        email.send()

        return {
            "success": True,
            "message": f"Reporte enviado exitosamente a {recipient_email}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error al enviar el email: {str(e)}"
        }

