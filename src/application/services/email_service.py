"""
Email Service - Servicio para envío de emails con Resend.
"""

import base64
from typing import Optional, Dict
from loguru import logger
import resend

from src.config.settings import settings


class EmailService:
    """
    Servicio para envío de emails usando Resend.
    
    Permite enviar presupuestos por email con PDF adjunto.
    """
    
    def __init__(self):
        """Inicializa el servicio de email."""
        if not settings.resend_api_key:
            logger.warning("⚠️ RESEND_API_KEY no configurada")
        else:
            resend.api_key = settings.resend_api_key
            logger.info("✓ EmailService inicializado con Resend")
    
    def enviar_presupuesto(
        self,
        email_destinatario: str,
        pdf_bytes: bytes,
        datos_presupuesto: Dict,
        mensaje_personalizado: Optional[str] = None
    ) -> bool:
        """
        Envía un presupuesto por email con PDF adjunto.
        
        Args:
            email_destinatario: Email del destinatario
            pdf_bytes: Contenido del PDF en bytes
            datos_presupuesto: Datos del presupuesto (numero, fecha, total, etc.)
            mensaje_personalizado: Mensaje opcional del remitente
            
        Returns:
            bool: True si se envió correctamente
            
        Raises:
            Exception: Si hay error al enviar
        """
        try:
            # Convertir PDF a base64
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Generar nombre de archivo
            numero = datos_presupuesto.get('numero', 'PRESUPUESTO')
            nombre_archivo = f"{numero}.pdf"
            
            # Generar HTML del email
            html_content = self._generar_html_email(
                datos_presupuesto,
                mensaje_personalizado
            )
            
            # Enviar email
            params = {
                "from": f"{settings.email_from_name} <{settings.email_from}>",
                "to": [email_destinatario],
                "subject": f"Presupuesto de Reforma - {numero}",
                "html": html_content,
                "attachments": [{
                    "filename": nombre_archivo,
                    "content": pdf_base64
                }]
            }
            
            response = resend.Emails.send(params)
            
            logger.info(
                f"✓ Email enviado a {email_destinatario} | "
                f"ID: {response.get('id', 'N/A')}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email: {e}")
            raise
    
    def _generar_html_email(
        self,
        datos: Dict,
        mensaje_personalizado: Optional[str] = None
    ) -> str:
        """
        Genera el HTML del email.
        
        Args:
            datos: Datos del presupuesto
            mensaje_personalizado: Mensaje opcional
            
        Returns:
            str: HTML del email
        """
        numero = datos.get('numero', 'N/A')
        fecha = datos.get('fecha', 'N/A')
        total = datos.get('total', '0.00')
        cliente = datos.get('cliente', {})
        nombre_cliente = cliente.get('nombre', 'Cliente')
        
        mensaje_html = ""
        if mensaje_personalizado:
            mensaje_html = f"""
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #1f77b4; margin: 20px 0;">
                <p style="margin: 0; font-style: italic;">{mensaje_personalizado}</p>
            </div>
            """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #1f77b4, #1565c0);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .greeting {{
                    font-size: 18px;
                    margin-bottom: 20px;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #e9ecef;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #666;
                }}
                .info-value {{
                    color: #333;
                }}
                .total {{
                    background: #1f77b4;
                    color: white;
                    padding: 15px;
                    border-radius: 6px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .total-label {{
                    font-size: 14px;
                    opacity: 0.9;
                    margin-bottom: 5px;
                }}
                .total-amount {{
                    font-size: 32px;
                    font-weight: bold;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #666;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: #1f77b4;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 10px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏗️ Tu Presupuesto de Reforma</h1>
                </div>
                
                <div class="content">
                    <p class="greeting">Hola {nombre_cliente},</p>
                    
                    <p>Adjunto encontrarás tu presupuesto detallado de reforma. Hemos preparado un análisis completo con todas las partidas y costes.</p>
                    
                    {mensaje_html}
                    
                    <div class="info-box">
                        <div class="info-row">
                            <span class="info-label">📋 Número de Presupuesto:</span>
                            <span class="info-value">{numero}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">📅 Fecha:</span>
                            <span class="info-value">{fecha}</span>
                        </div>
                    </div>
                    
                    <div class="total">
                        <div class="total-label">TOTAL (IVA incluido)</div>
                        <div class="total-amount">{total}€</div>
                    </div>
                    
                    <p>El presupuesto incluye:</p>
                    <ul>
                        <li>Desglose detallado de todas las partidas</li>
                        <li>Precios actualizados con IPC</li>
                        <li>IVA aplicable según normativa</li>
                        <li>Condiciones y validez del presupuesto</li>
                    </ul>
                    
                    <p>Si tienes alguna pregunta o necesitas aclaraciones sobre el presupuesto, no dudes en contactarnos.</p>
                    
                    <p style="margin-top: 30px;">
                        Saludos cordiales,<br>
                        <strong>Equipo de Calculadora de Presupuestos</strong>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Este email fue generado automáticamente por nuestra calculadora de presupuestos.</p>
                    <p style="font-size: 12px; margin-top: 10px;">
                        © 2025 Calculadora de Presupuestos. Todos los derechos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def enviar_reset_password(
        self,
        email_destinatario: str,
        reset_link: str,
        nombre: str
    ) -> bool:
        """
        Envía email de recuperación de contraseña.
        
        Args:
            email_destinatario: Email del usuario
            reset_link: Link completo para reset de contraseña
            nombre: Nombre del usuario
            
        Returns:
            bool: True si se envió correctamente
            
        Raises:
            Exception: Si hay error al enviar
        """
        try:
            # Generar HTML del email
            html_content = self._generar_html_reset_password(
                nombre,
                reset_link
            )
            
            # Enviar email
            params = {
                "from": f"{settings.email_from_name} <{settings.email_from}>",
                "to": [email_destinatario],
                "subject": "🔐 Recuperación de Contraseña",
                "html": html_content
            }
            
            response = resend.Emails.send(params)
            
            logger.info(
                f"✓ Email de reset enviado a {email_destinatario} | "
                f"ID: {response.get('id', 'N/A')}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enviando email de reset: {e}")
            raise
    
    def _generar_html_reset_password(
        self,
        nombre: str,
        reset_link: str
    ) -> str:
        """
        Genera el HTML del email de reset de contraseña.
        
        Args:
            nombre: Nombre del usuario
            reset_link: Link de reset
            
        Returns:
            str: HTML del email
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    padding: 30px 20px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 600;
                }}
                .content {{
                    padding: 30px 20px;
                }}
                .greeting {{
                    font-size: 18px;
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 15px 30px;
                    background: #e74c3c;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 600;
                    font-size: 16px;
                }}
                .button:hover {{
                    background: #c0392b;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 14px;
                    color: #666;
                }}
                .security-note {{
                    background: #e8f5e9;
                    border-left: 4px solid #4caf50;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Recuperación de Contraseña</h1>
                </div>
                
                <div class="content">
                    <p class="greeting">Hola {nombre},</p>
                    
                    <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta.</p>
                    
                    <p>Haz click en el siguiente botón para crear una nueva contraseña:</p>
                    
                    <div style="text-align: center;">
                        <a href="{reset_link}" class="button">Restablecer Contraseña</a>
                    </div>
                    
                    <div class="warning">
                        <strong>⏰ Este link expira en 1 hora</strong><br>
                        Por seguridad, el enlace solo es válido durante 60 minutos.
                    </div>
                    
                    <div class="security-note">
                        <strong>🔒 Nota de Seguridad:</strong><br>
                        Si no solicitaste este cambio de contraseña, puedes ignorar este email de forma segura. 
                        Tu contraseña actual permanecerá sin cambios.
                    </div>
                    
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                        Si el botón no funciona, copia y pega este enlace en tu navegador:<br>
                        <a href="{reset_link}" style="color: #1f77b4; word-break: break-all;">{reset_link}</a>
                    </p>
                    
                    <p style="margin-top: 30px;">
                        Saludos cordiales,<br>
                        <strong>Equipo de Calculadora de Presupuestos</strong>
                    </p>
                </div>
                
                <div class="footer">
                    <p>Este email fue generado automáticamente. Por favor no respondas a este mensaje.</p>
                    <p style="font-size: 12px; margin-top: 10px;">
                        © 2025 Calculadora de Presupuestos. Todos los derechos reservados.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Singleton
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Obtiene instancia singleton del servicio de email.
    
    Returns:
        EmailService: Instancia única
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
