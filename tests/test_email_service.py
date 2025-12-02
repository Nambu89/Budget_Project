"""
Tests para el servicio de email (Resend + SMTP).

Prueba ambos servicios de email sin necesidad de deploy.
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import pytest
from io import BytesIO
from reportlab.pdfgen import canvas
from src.application.services.email_service import get_email_service
from src.config.settings import settings


def generar_pdf_prueba() -> bytes:
	"""
	Genera un PDF de prueba simple.
	
	Returns:
		bytes: Contenido del PDF
	"""
	buffer = BytesIO()
	c = canvas.Canvas(buffer)
	c.drawString(100, 750, "PRESUPUESTO DE PRUEBA")
	c.drawString(100, 700, "Este es un PDF de prueba para testing")
	c.drawString(100, 650, "Número: PRES-TEST-001")
	c.drawString(100, 600, "Total: 1,234.56 €")
	c.save()
	
	pdf_bytes = buffer.getvalue()
	buffer.close()
	
	return pdf_bytes


class TestEmailService:
	"""Tests del servicio de email."""
	
	@pytest.fixture
	def email_service(self):
		"""Fixture del servicio de email."""
		return get_email_service()
	
	@pytest.fixture
	def datos_presupuesto_prueba(self):
		"""Fixture con datos de presupuesto de prueba."""
		return {
			'numero': 'PRES-TEST-20251202',
			'fecha': '02/12/2025',
			'total': '1,234.56',
			'cliente': {
				'nombre': 'Cliente de Prueba',
				'email': 'cliente@example.com'
			}
		}
	
	def test_smtp_configurado(self, email_service):
		"""Verifica que SMTP esté configurado correctamente."""
		print("\n" + "="*60)
		print("TEST: Verificar configuración SMTP")
		print("="*60)
		
		if not settings.is_smtp_configured():
			print("⚠️  SMTP NO configurado")
			print(f"   SMTP_HOST: {settings.smtp_host or 'NO DEFINIDO'}")
			print(f"   SMTP_USERNAME: {settings.smtp_username or 'NO DEFINIDO'}")
			print(f"   SMTP_PASSWORD: {'***' if settings.smtp_password else 'NO DEFINIDO'}")
			pytest.skip("SMTP no está configurado en .env")
		
		print("✅ SMTP configurado correctamente")
		print(f"   Host: {settings.smtp_host}")
		print(f"   Puerto: {settings.smtp_port}")
		print(f"   Usuario: {settings.smtp_username}")
		print(f"   SSL: {settings.smtp_use_ssl}")
		print(f"   Email remitente: {settings.email_from_budgets}")
	
	def test_resend_configurado(self, email_service):
		"""Verifica que Resend esté configurado correctamente."""
		print("\n" + "="*60)
		print("TEST: Verificar configuración Resend")
		print("="*60)
		
		if not settings.is_resend_configured():
			print("⚠️  Resend NO configurado")
			print(f"   RESEND_API_KEY: {settings.resend_api_key[:10] + '...' if settings.resend_api_key else 'NO DEFINIDO'}")
			pytest.skip("Resend no está configurado en .env")
		
		print("✅ Resend configurado correctamente")
		print(f"   API Key: {settings.resend_api_key[:10]}...")
		print(f"   Email sistema: {settings.email_from_system}")
	
	def test_generar_html_presupuesto(self, email_service, datos_presupuesto_prueba):
		"""Prueba la generación de HTML para email de presupuesto."""
		print("\n" + "="*60)
		print("TEST: Generar HTML de presupuesto")
		print("="*60)
		
		html = email_service._generar_html_presupuesto(
			datos_presupuesto_prueba,
			mensaje_personalizado="Este es un mensaje de prueba"
		)
		
		# Verificar contenido
		assert "PRES-TEST-20251202" in html
		assert "1,234.56" in html
		assert "Cliente de Prueba" in html
		assert "Este es un mensaje de prueba" in html
		
		print("✅ HTML generado correctamente")
		print(f"   Longitud: {len(html)} caracteres")
		print(f"   Contiene número presupuesto: ✓")
		print(f"   Contiene total: ✓")
		print(f"   Contiene nombre cliente: ✓")
		print(f"   Contiene mensaje personalizado: ✓")
	
	def test_generar_html_reset_password(self, email_service):
		"""Prueba la generación de HTML para reset de contraseña."""
		print("\n" + "="*60)
		print("TEST: Generar HTML de reset de contraseña")
		print("="*60)
		
		reset_link = f"{settings.app_url}/reset-password?token=abc123"
		html = email_service._generar_html_reset_password(
			nombre="Usuario de Prueba",
			reset_link=reset_link
		)
		
		# Verificar contenido
		assert "Usuario de Prueba" in html
		assert reset_link in html
		assert "Restablecer Contraseña" in html
		assert "expira en 1 hora" in html.lower()
		
		print("✅ HTML generado correctamente")
		print(f"   Longitud: {len(html)} caracteres")
		print(f"   Contiene nombre usuario: ✓")
		print(f"   Contiene link de reset: ✓")
		print(f"   Contiene advertencia de expiración: ✓")
	
	@pytest.mark.skipif(
		not settings.is_smtp_configured(),
		reason="SMTP no configurado"
	)
	def test_enviar_presupuesto_smtp(
		self,
		email_service,
		datos_presupuesto_prueba
	):
		"""
		Prueba el envío de presupuesto por SMTP.
		
		⚠️ IMPORTANTE: Cambia el email destinatario por el tuyo.
		"""
		print("\n" + "="*60)
		print("TEST: Enviar presupuesto por SMTP")
		print("="*60)
		
		# ⚠️ CAMBIAR ESTE EMAIL POR EL TUYO
		email_destinatario = "fernando.prada@proton.me"
		
		print(f"\n⚠️  ATENCIÓN: Este test enviará un email real a: {email_destinatario}")
		print("   Si no quieres enviar el email, cancela el test (Ctrl+C)")
		print("   O cambia 'email_destinatario' en el código del test\n")
		
		# Generar PDF de prueba
		pdf_bytes = generar_pdf_prueba()
		
		print(f"📄 PDF generado: {len(pdf_bytes)} bytes")
		print(f"📧 Enviando a: {email_destinatario}")
		print(f"📨 Desde: {settings.email_from_budgets}")
		
		# Enviar email
		try:
			resultado = email_service.enviar_presupuesto(
				email_destinatario=email_destinatario,
				pdf_bytes=pdf_bytes,
				datos_presupuesto=datos_presupuesto_prueba,
				mensaje_personalizado="Este es un email de prueba automático"
			)
			
			assert resultado == True
			
			print("\n✅ Email enviado correctamente por SMTP")
			print("   Revisa tu bandeja de entrada")
			
		except Exception as e:
			print(f"\n❌ Error enviando email: {e}")
			pytest.fail(f"Error en envío SMTP: {e}")
	
	@pytest.mark.skipif(
		not settings.is_resend_configured(),
		reason="Resend no configurado"
	)
	def test_enviar_reset_password_resend(self, email_service):
		"""
		Prueba el envío de reset de contraseña por Resend.
		
		⚠️ IMPORTANTE: Cambia el email destinatario por el tuyo.
		"""
		print("\n" + "="*60)
		print("TEST: Enviar reset de contraseña por Resend")
		print("="*60)
		
		# ⚠️ CAMBIAR ESTE EMAIL POR EL TUYO
		email_destinatario = "fernando.prada@proton.me"
		
		print(f"\n⚠️  ATENCIÓN: Este test enviará un email real a: {email_destinatario}")
		print("   Si no quieres enviar el email, cancela el test (Ctrl+C)")
		print("   O cambia 'email_destinatario' en el código del test\n")
		
		# Generar link de reset fake
		reset_link = f"{settings.app_url}/reset-password?token=test_token_abc123"
		
		print(f"📧 Enviando a: {email_destinatario}")
		print(f"📨 Desde: {settings.email_from_system}")
		print(f"🔗 Link: {reset_link}")
		
		# Enviar email
		try:
			resultado = email_service.enviar_reset_password(
				email_destinatario=email_destinatario,
				reset_link=reset_link,
				nombre="Usuario de Prueba"
			)
			
			assert resultado == True
			
			print("\n✅ Email enviado correctamente por Resend")
			print("   Revisa tu bandeja de entrada")
			
		except Exception as e:
			print(f"\n❌ Error enviando email: {e}")
			pytest.fail(f"Error en envío Resend: {e}")


def test_configuracion_completa():
	"""Muestra un resumen completo de la configuración de email."""
	print("\n" + "="*60)
	print("RESUMEN DE CONFIGURACIÓN DE EMAIL")
	print("="*60)
	
	print("\n📧 SMTP (Presupuestos):")
	print(f"   Configurado: {'✅ Sí' if settings.is_smtp_configured() else '❌ No'}")
	if settings.is_smtp_configured():
		print(f"   Host: {settings.smtp_host}")
		print(f"   Puerto: {settings.smtp_port}")
		print(f"   Usuario: {settings.smtp_username}")
		print(f"   SSL: {settings.smtp_use_ssl}")
		print(f"   Email remitente: {settings.email_from_budgets}")
	
	print("\n🔐 Resend (Reset Contraseñas):")
	print(f"   Configurado: {'✅ Sí' if settings.is_resend_configured() else '❌ No'}")
	if settings.is_resend_configured():
		print(f"   API Key: {settings.resend_api_key[:10]}...")
		print(f"   Email sistema: {settings.email_from_system}")
	
	print("\n🏢 Empresa:")
	print(f"   Nombre: {settings.empresa_nombre}")
	print(f"   Email: {settings.empresa_email}")
	print(f"   Teléfono: {settings.empresa_telefono}")
	print(f"   Web: {settings.empresa_web}")
	
	print("\n🌐 Aplicación:")
	print(f"   URL: {settings.app_url}")
	print(f"   Entorno: {settings.environment}")
	
	print("\n" + "="*60)


if __name__ == "__main__":
	"""Ejecutar tests directamente."""
	print("\n🧪 EJECUTANDO TESTS DE EMAIL SERVICE")
	print("="*60)
	
	# Mostrar configuración
	test_configuracion_completa()
	
	# Ejecutar tests
	pytest.main([
		__file__,
		"-v",
		"-s",  # Mostrar prints
		"--tb=short"  # Traceback corto
	])