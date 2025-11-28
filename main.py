"""
Entry point principal con health check mejorado.
"""

import sys
import os
from loguru import logger
from datetime import datetime

# Configurar logging
logger.remove()
logger.add(
	sys.stderr,
	format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
	level="INFO" if os.getenv("ENVIRONMENT") == "production" else "DEBUG",
)


def health_check() -> dict:
	"""
	Health check completo con métricas del sistema.
	
	Returns:
		dict: Estado del sistema
	"""
	from src.config.settings import settings
	from src.infrastructure.database import test_connection
	
	# Verificar BD
	db_ok = test_connection()
	
	# Verificar LLM
	llm_ok = False
	try:
		settings.get_active_llm_config()
		llm_ok = True
	except Exception as e:
		logger.warning(f"LLM config issue: {e}")
	
	# Determinar estado general
	status = "healthy"
	if not db_ok:
		status = "degraded"
	if not db_ok and not llm_ok:
		status = "unhealthy"
	
	result = {
		"status": status,
		"timestamp": datetime.now().isoformat(),
		"environment": settings.environment,
		"components": {
			"database": {
				"status": "up" if db_ok else "down",
				"type": settings.db_type
			},
			"llm": {
				"status": "up" if llm_ok else "down",
				"provider": settings.llm_provider
			}
		},
		"version": "1.0.0"  # Actualizar según tu versión
	}
	
	return result


# Health check para Railway
if len(sys.argv) > 1 and sys.argv[1] == "health":
	result = health_check()
	print(result)
	sys.exit(0 if result["status"] in ["healthy", "degraded"] else 1)

# Importar después de configurar logging
from src.application.presentation.streamlit_app import main as app_main


def run():
	"""Ejecuta la aplicación principal con inicialización mejorada."""
	logger.info("=" * 60)
	logger.info("🚀 Iniciando Easy Obras - Calculadora de Presupuestos")
	logger.info("=" * 60)
	
	try:
		from src.config.settings import settings
		
		# Logging de configuración
		logger.info(f"Entorno: {settings.environment}")
		logger.info(f"Debug: {settings.debug}")
		logger.info(f"LLM Provider: {settings.llm_provider}")
		logger.info(f"Database Type: {settings.db_type}")
		
		# Ocultar credenciales
		db_info = settings.get_database_info()
		logger.info(f"Database URL: {db_info['url']}")
		
		# Validar configuración en producción
		if settings.is_production():
			is_valid, errors = settings.validate_production_config()
			if not is_valid:
				logger.warning("⚠️ Configuración de producción tiene advertencias:")
				for error in errors:
					logger.warning(f"  - {error}")
		
		# Inicializar BD
		from src.infrastructure.database import init_db, test_connection
		
		logger.info("Verificando conexión a base de datos...")
		if test_connection():
			init_db()
			logger.info("✓ Base de datos lista")
		else:
			logger.error("✗ No se pudo conectar a la base de datos")
			if settings.is_production():
				raise RuntimeError("BD no disponible en producción")
		
		# Log de inicio exitoso
		from src.infrastructure.logging.metrics import metrics
		metrics.log_event(
			"APP_STARTED",
			environment=settings.environment,
			db_type=settings.db_type
		)
		
		logger.info("=" * 60)
		logger.info("✓ Inicialización completada - Iniciando interfaz Streamlit")
		logger.info("=" * 60)
		
		# Ejecutar aplicación Streamlit
		app_main()
		
	except Exception as e:
		logger.exception(f"Error fatal durante inicialización: {e}")
		raise


# Entry point
if __name__ == "__main__":
	run()