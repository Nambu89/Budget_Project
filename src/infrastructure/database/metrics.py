"""
Sistema de métricas y logging mejorado.

Centraliza el logging de eventos de negocio importantes
para facilitar el monitoreo sin necesidad de Prometheus.
"""

from loguru import logger
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps
import time


class MetricsLogger:
	"""
	Logger de métricas de negocio.
	
	Formato estructurado para facilitar búsqueda en Railway logs.
	"""
	
	@staticmethod
	def log_event(
		event_type: str,
		user_id: Optional[str] = None,
		**kwargs
	) -> None:
		"""
		Loguea un evento de negocio.
		
		Args:
			event_type: Tipo de evento (ej: PRESUPUESTO_CREADO)
			user_id: ID del usuario (opcional)
			**kwargs: Datos adicionales del evento
		"""
		# Construir mensaje estructurado
		parts = [f"EVENT={event_type}"]
		
		if user_id:
			parts.append(f"user_id={user_id}")
		
		# Añadir todos los kwargs
		for key, value in kwargs.items():
			# Formatear valores numéricos
			if isinstance(value, float):
				parts.append(f"{key}={value:.2f}")
			else:
				parts.append(f"{key}={value}")
		
		message = " | ".join(parts)
		logger.info(message)
	
	@staticmethod
	def log_error(
		error_type: str,
		error: Exception,
		user_id: Optional[str] = None,
		**kwargs
	) -> None:
		"""
		Loguea un error con contexto.
		
		Args:
			error_type: Tipo de error (ej: DB_ERROR)
			error: Excepción capturada
			user_id: ID del usuario (opcional)
			**kwargs: Contexto adicional
		"""
		parts = [f"ERROR={error_type}"]
		
		if user_id:
			parts.append(f"user_id={user_id}")
		
		parts.append(f"message={str(error)}")
		
		for key, value in kwargs.items():
			parts.append(f"{key}={value}")
		
		message = " | ".join(parts)
		logger.error(message)
	
	@staticmethod
	def log_performance(
		operation: str,
		duration_ms: float,
		user_id: Optional[str] = None,
		**kwargs
	) -> None:
		"""
		Loguea métricas de performance.
		
		Args:
			operation: Nombre de la operación
			duration_ms: Duración en milisegundos
			user_id: ID del usuario (opcional)
			**kwargs: Contexto adicional
		"""
		parts = [
			f"PERF={operation}",
			f"duration_ms={duration_ms:.2f}"
		]
		
		if user_id:
			parts.append(f"user_id={user_id}")
		
		for key, value in kwargs.items():
			parts.append(f"{key}={value}")
		
		message = " | ".join(parts)
		
		# Warning si es lento
		if duration_ms > 5000:  # > 5 segundos
			logger.warning(message)
		else:
			logger.info(message)


def track_performance(operation_name: str):
	"""
	Decorator para trackear performance de funciones.
	
	Usage:
		@track_performance("generar_pdf")
		def generar_pdf(presupuesto):
			...
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			start_time = time.time()
			
			try:
				result = func(*args, **kwargs)
				duration_ms = (time.time() - start_time) * 1000
				
				MetricsLogger.log_performance(
					operation=operation_name,
					duration_ms=duration_ms,
					status="success"
				)
				
				return result
				
			except Exception as e:
				duration_ms = (time.time() - start_time) * 1000
				
				MetricsLogger.log_performance(
					operation=operation_name,
					duration_ms=duration_ms,
					status="error",
					error=str(e)
				)
				
				raise
		
		return wrapper
	return decorator


# Instancia global
metrics = MetricsLogger()