"""
Email Service - Servicio dual para envío de emails.

- Resend: Emails de sistema (reset de contraseñas)
- SMTP: Emails con presupuestos adjuntos
"""

import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict
from loguru import logger

try:
	import resend
	RESEND_AVAILABLE = True
except ImportError:
	RESEND_AVAILABLE = False
	logger.warning("⚠️ Resend no está instalado")

from src.config.settings import settings


class EmailService:
	"""
	Servicio dual para envío de emails.
	
	Usa Resend para emails de sistema (reset contraseña) y
	SMTP nativo para emails con adjuntos (presupuestos).
	"""
	
	def __init__(self):
		"""Inicializa el servicio de email."""
		# Configurar Resend si está disponible
		if RESEND_AVAILABLE and settings.resend_api_key:
			resend.api_key = settings.resend_api_key
			logger.info("✓ Resend configurado para emails de sistema")
		else:
			logger.warning("⚠️ Resend no configurado")
		
		# Verificar SMTP
		if settings.is_smtp_configured():
			logger.info("✓ SMTP configurado para envío de presupuestos")
		else:
			logger.warning("⚠️ SMTP no configurado")
	
	# ==========================================
	# SMTP - Envío de presupuestos
	# ==========================================
	
	def enviar_presupuesto(
		self,
		email_destinatario: str,
		pdf_bytes: bytes,
		datos_presupuesto: Dict,
		mensaje_personalizado: Optional[str] = None
	) -> bool:
		"""
		Envía un presupuesto por email con PDF adjunto usando SMTP.
		
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
		if not settings.is_smtp_configured():
			raise ValueError("SMTP no está configurado. Verifica las variables de entorno.")
		
		try:
			# Crear mensaje
			msg = MIMEMultipart()
			msg['From'] = f"{settings.email_from_name} <{settings.email_from_budgets}>"
			msg['To'] = email_destinatario
			msg['Subject'] = f"Presupuesto de Reforma - {datos_presupuesto.get('numero', 'N/A')}"
			
			# Generar HTML del email
			html_content = self._generar_html_presupuesto(
				datos_presupuesto,
				mensaje_personalizado
			)
			
			# Adjuntar HTML
			msg.attach(MIMEText(html_content, 'html'))
			
			# Adjuntar PDF
			numero = datos_presupuesto.get('numero', 'PRESUPUESTO')
			nombre_archivo = f"{numero}.pdf"
			
			pdf_attachment = MIMEBase('application', 'pdf')
			pdf_attachment.set_payload(pdf_bytes)
			encoders.encode_base64(pdf_attachment)
			pdf_attachment.add_header(
				'Content-Disposition',
				f'attachment; filename={nombre_archivo}'
			)
			msg.attach(pdf_attachment)
			
			# Enviar email
			if settings.smtp_use_ssl:
				# SSL (puerto 465)
				with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
					server.login(settings.smtp_username, settings.smtp_password)
					server.send_message(msg)
			else:
				# TLS (puerto 587)
				with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
					server.starttls()
					server.login(settings.smtp_username, settings.smtp_password)
					server.send_message(msg)
			
			logger.info(f"✓ Presupuesto enviado a {email_destinatario} vía SMTP")
			return True
			
		except Exception as e:
			logger.error(f"❌ Error enviando presupuesto vía SMTP: {e}")
			raise
	
	def _generar_html_presupuesto(
		self,
		datos: Dict,
		mensaje_personalizado: Optional[str] = None
	) -> str:
		"""
		Genera el HTML del email de presupuesto.
		
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
			<div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
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
					background: linear-gradient(135deg, #2563eb, #1e40af);
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
					background: #2563eb;
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
						<strong>{settings.email_from_name}</strong>
					</p>
				</div>
				
				<div class="footer">
					<p><strong>{settings.empresa_nombre}</strong></p>
					<p>📞 {settings.empresa_telefono} | ✉️ {settings.empresa_email}</p>
					<p>🌐 {settings.empresa_web}</p>
					<p style="font-size: 12px; margin-top: 10px;">
						© 2025 {settings.empresa_nombre}. Todos los derechos reservados.
					</p>
				</div>
			</div>
		</body>
		</html>
		"""
		
		return html
	
	# ==========================================
	# RESEND - Reset de contraseñas
	# ==========================================
	
	def enviar_reset_password(
		self,
		email_destinatario: str,
		reset_link: str,
		nombre: str
	) -> bool:
		"""
		Envía email de recuperación de contraseña usando Resend.
		
		Args:
			email_destinatario: Email del usuario
			reset_link: Link completo para reset de contraseña
			nombre: Nombre del usuario
			
		Returns:
			bool: True si se envió correctamente
			
		Raises:
			Exception: Si hay error al enviar
		"""
		if not RESEND_AVAILABLE or not settings.is_resend_configured():
			raise ValueError("Resend no está configurado. Verifica RESEND_API_KEY.")
		
		try:
			# Generar HTML del email
			html_content = self._generar_html_reset_password(nombre, reset_link)
			
			# Enviar email
			params = {
				"from": f"{settings.email_from_name} <{settings.email_from_system}>",
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
					
					<p>Recibimos una solicitud para restablecer la contraseña de tu cuenta en {settings.empresa_nombre}.</p>
					
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
						<a href="{reset_link}" style="color: #2563eb; word-break: break-all;">{reset_link}</a>
					</p>
					
					<p style="margin-top: 30px;">
						Saludos cordiales,<br>
						<strong>Equipo de {settings.empresa_nombre}</strong>
					</p>
				</div>
				
				<div class="footer">
					<p>Este email fue generado automáticamente. Por favor no respondas a este mensaje.</p>
					<p style="font-size: 12px; margin-top: 10px;">
						© 2025 {settings.empresa_nombre}. Todos los derechos reservados.
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