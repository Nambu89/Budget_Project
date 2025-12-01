"""
Configuración centralizada con soporte automático para SQLite y PostgreSQL.

Detecta el entorno y ajusta la configuración automáticamente:
- Desarrollo: SQLite local
- Producción con SQLite: Volumen persistente en Railway
- Producción con PostgreSQL: Base de datos externa
"""

from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, computed_field
from functools import lru_cache
import secrets
import os


class Settings(BaseSettings):
	"""
	Configuración principal con detección automática de entorno.
	
	Soporta:
	- SQLite local (desarrollo)
	- SQLite en Railway con volumen persistente
	- PostgreSQL en Railway o cualquier proveedor
	"""
	
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
		case_sensitive=False,
		extra="ignore",
	)
	
	# ==========================================
	# Security
	# ==========================================
	secret_key: str = Field(
		default_factory=lambda: secrets.token_urlsafe(32),
		description="Clave secreta para firmar tokens"
	)
	
	# ==========================================
	# Environment
	# ==========================================
	environment: Literal["development", "staging", "production"] = Field(
		default="development",
		description="Entorno de ejecución"
	)
	
	debug: bool = Field(
		default=True,
		description="Modo debug activado"
	)
	
	# ==========================================
	# Database (Dinámico)
	# ==========================================
	database_url: Optional[str] = Field(
		default=None,
		description="URL de conexión a la base de datos (auto-detecta si no se especifica)"
	)
	
	# ==========================================
	# Proveedor LLM
	# ==========================================
	llm_provider: Literal["azure", "openai"] = Field(
		default="azure",
		description="Proveedor de LLM a utilizar"
	)
	
	# ==========================================
	# Azure OpenAI
	# ==========================================
	azure_openai_endpoint: str = Field(
		default="",
		description="Endpoint de Azure OpenAI"
	)
	azure_openai_api_key: str = Field(
		default="",
		description="API Key de Azure OpenAI"
	)
	azure_openai_api_version: str = Field(
		default="2024-02-15-preview",
		description="Versión de la API de Azure OpenAI"
	)
	azure_openai_deployment_name: str = Field(
		default="gpt-4o-mini",
		description="Nombre del deployment en Azure"
	)
	
	# ==========================================
	# OpenAI Directo
	# ==========================================
	openai_api_key: str = Field(
		default="",
		description="API Key de OpenAI"
	)
	openai_model: str = Field(
		default="gpt-4o-mini",
		description="Modelo de OpenAI a usar"
	)
	
	# ==========================================
	# Resend Email Service
	# ==========================================
	resend_api_key: Optional[str] = Field(
		default=None,
		description="API Key de Resend para envío de emails"
	)
	email_from: str = Field(
		default="presupuestos@easyobras.es",
		description="Email remitente"
	)
	
	# ==========================================
	# Configuración de negocio
	# ==========================================
	iva_general: int = Field(
		default=21,
		description="IVA general (%)",
		ge=0,
		le=100
	)
	iva_reducido: int = Field(
		default=10,
		description="IVA reducido para vivienda habitual (%)",
		ge=0,
		le=100
	)
	markup_partidas_individuales: int = Field(
		default=15,
		description="Markup para partidas individuales vs paquetes (%)",
		ge=0,
		le=100
	)
	redondeo_alza: int = Field(
		default=5,
		description="Redondeo al alza sobre el total (%)",
		ge=0,
		le=100
	)
	validez_presupuesto_dias: int = Field(
		default=30,
		description="Días de validez del presupuesto",
		ge=1
	)
	
	# ==========================================
	# Configuración PDF
	# ==========================================
	logos_path: str = Field(
		default="./assets/logos/",
		description="Ruta para logos de clientes"
	)
	empresa_nombre: str = Field(
		default="ISI Obras",
		description="Nombre de la empresa"
	)
	empresa_telefono: str = Field(
		default="+34 900 000 000",
		description="Teléfono de la empresa"
	)
	empresa_email: str = Field(
		default="info@easyobras.es",
		description="Email de la empresa"
	)
	empresa_web: str = Field(
		default="https://isiobrasyservicios.com/",
		description="Web de la empresa"
	)
	
	# ==========================================
	# Precios e IPC
	# ==========================================
	ano_base_precios: int = Field(
		default=2024,
		description="Año base para los precios del catálogo"
	)
	
	ipc_anual: float = Field(
		default=3.5,
		description="IPC anual estimado para ajuste de precios (%)"
	)
	
	# ==========================================
	# Computed Fields (Auto-detectados)
	# ==========================================
	
	@computed_field
	@property
	def db_url(self) -> str:
		"""
		URL de base de datos con detección automática.
		
		Prioridad:
		1. DATABASE_URL explícita en .env
		2. Auto-detección según entorno
		
		Returns:
			str: URL de conexión a la base de datos
		"""
		# Si hay DATABASE_URL explícita, usarla
		if self.database_url:
			url = self.database_url
			
			# Railway a veces usa postgres:// en lugar de postgresql://
			if url.startswith("postgres://"):
				url = url.replace("postgres://", "postgresql://", 1)
			
			return url
		
		# Auto-detección según entorno
		if self.environment == "production":
			# Railway con volumen persistente
			# Verificar si existe DATABASE_URL de Railway (PostgreSQL)
			railway_db = os.getenv("DATABASE_URL")
			if railway_db and "postgresql" in railway_db:
				# PostgreSQL de Railway
				if railway_db.startswith("postgres://"):
					railway_db = railway_db.replace("postgres://", "postgresql://", 1)
				return railway_db
			else:
				# SQLite en volumen persistente de Railway
				return "sqlite:////app/data/budget.db"
		else:
			# Desarrollo local
			return "sqlite:///./data/budget.db"
	
	@computed_field
	@property
	def db_type(self) -> Literal["sqlite", "postgresql"]:
		"""
		Tipo de base de datos detectado.
		
		Returns:
			str: 'sqlite' o 'postgresql'
		"""
		return "postgresql" if "postgresql" in self.db_url else "sqlite"
	
	@computed_field
	@property
	def db_config(self) -> dict:
		"""
		Configuración de SQLAlchemy según tipo de BD.
		
		Returns:
			dict: Parámetros para create_engine()
		"""
		if self.db_type == "postgresql":
			return {
				"pool_size": 10,
				"max_overflow": 20,
				"pool_pre_ping": True,
				"pool_recycle": 3600,
				"echo": self.debug,
			}
		else:  # sqlite
			return {
				"connect_args": {"check_same_thread": False},
				"echo": self.debug,
			}
	
	# ==========================================
	# Validaciones de seguridad
	# ==========================================
	
	@field_validator("secret_key")
	@classmethod
	def validate_secret_key(cls, v: str, info) -> str:
		"""Valida que la clave secreta sea suficientemente fuerte."""
		environment = info.data.get("environment", "development")
		
		if environment == "production" and len(v) < 32:
			raise ValueError(
				"SECRET_KEY debe tener al menos 32 caracteres en producción. "
				"Genera una con: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
			)
		
		return v
	
	@field_validator("azure_openai_api_key", "openai_api_key", "resend_api_key")
	@classmethod
	def validate_no_placeholder_keys(cls, v: Optional[str], info) -> Optional[str]:
		"""Valida que no haya API keys de placeholder en producción."""
		if not v:
			return v
		
		environment = info.data.get("environment", "development")
		
		# Detectar placeholders comunes
		placeholders = ["tu-api-key", "your-api-key", "placeholder", "xxx", "TODO"]
		
		if environment == "production" and any(p in v.lower() for p in placeholders):
			field_name = info.field_name
			raise ValueError(
				f"{field_name} contiene un valor placeholder en producción. "
				f"Configura una API key real."
			)
		
		return v
	
	# ==========================================
	# Métodos de utilidad
	# ==========================================
	
	def is_production(self) -> bool:
		"""Verifica si está en producción."""
		return self.environment == "production"
	
	def is_development(self) -> bool:
		"""Verifica si está en desarrollo."""
		return self.environment == "development"
	
	def is_staging(self) -> bool:
		"""Verifica si está en staging."""
		return self.environment == "staging"
	
	def uses_sqlite(self) -> bool:
		"""Verifica si usa SQLite."""
		return self.db_type == "sqlite"
	
	def uses_postgresql(self) -> bool:
		"""Verifica si usa PostgreSQL."""
		return self.db_type == "postgresql"
	
	def is_azure_configured(self) -> bool:
		"""Verifica si Azure OpenAI está correctamente configurado."""
		return bool(
			self.azure_openai_endpoint and 
			self.azure_openai_api_key and
			self.azure_openai_deployment_name and
			"placeholder" not in self.azure_openai_api_key.lower()
		)
	
	def is_openai_configured(self) -> bool:
		"""Verifica si OpenAI directo está correctamente configurado."""
		return bool(
			self.openai_api_key and
			"placeholder" not in self.openai_api_key.lower()
		)
	
	def get_active_llm_config(self) -> dict:
		"""
		Retorna la configuración del LLM activo.
		
		Returns:
			dict: Configuración del proveedor LLM seleccionado
			
		Raises:
			ValueError: Si el LLM no está configurado correctamente
		"""
		if self.llm_provider == "azure":
			if not self.is_azure_configured():
				raise ValueError(
					"Azure OpenAI no está configurado correctamente. "
					"Verifica AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY y AZURE_OPENAI_DEPLOYMENT_NAME"
				)
			return {
				"provider": "azure",
				"endpoint": self.azure_openai_endpoint,
				"api_key": self.azure_openai_api_key,
				"api_version": self.azure_openai_api_version,
				"deployment": self.azure_openai_deployment_name,
			}
		else:
			if not self.is_openai_configured():
				raise ValueError(
					"OpenAI no está configurado correctamente. "
					"Verifica OPENAI_API_KEY"
				)
			return {
				"provider": "openai",
				"api_key": self.openai_api_key,
				"model": self.openai_model,
			}
	
	def get_database_info(self) -> dict:
		"""
		Retorna información sobre la base de datos configurada.
		
		Returns:
			dict: Información de la BD (sin credenciales)
		"""
		# Ocultar credenciales
		url_safe = self.db_url
		if "@" in url_safe:
			url_safe = url_safe.split("@")[0] + "@***"
		
		return {
			"type": self.db_type,
			"url": url_safe,
			"environment": self.environment,
			"config": {
				k: v for k, v in self.db_config.items()
				if k not in ["echo"]  # Ocultar detalles técnicos
			}
		}
	
	def validate_production_config(self) -> tuple[bool, list[str]]:
		"""
		Valida que la configuración sea apropiada para producción.
		
		Returns:
			tuple: (is_valid, list_of_errors)
		"""
		if not self.is_production():
			return True, []
		
		errors = []
		
		# Verificar SECRET_KEY
		if len(self.secret_key) < 32:
			errors.append("SECRET_KEY debe tener al menos 32 caracteres")
		
		# Verificar DEBUG
		if self.debug:
			errors.append("DEBUG debe ser False en producción")
		
		# Verificar LLM
		try:
			self.get_active_llm_config()
		except ValueError as e:
			errors.append(f"LLM: {str(e)}")
		
		# Advertir sobre SQLite en producción (no es error, solo warning)
		if self.uses_sqlite():
			errors.append(
				"ADVERTENCIA: Usando SQLite en producción. "
				"Considera PostgreSQL para escalabilidad futura."
			)
		
		return len(errors) == 0, errors


@lru_cache()
def get_settings() -> Settings:
	"""
	Obtiene la instancia de configuración (singleton cacheado).
	
	Returns:
		Settings: Instancia única de configuración
	"""
	return Settings()


# Instancia global para importación directa
settings = get_settings()


# ==========================================
# Validación automática al importar
# ==========================================
if __name__ != "__main__":
	# Solo validar en producción
	if settings.is_production():
		is_valid, errors = settings.validate_production_config()
		if not is_valid:
			from loguru import logger
			logger.warning("⚠️ Configuración de producción tiene problemas:")
			for error in errors:
				logger.warning(f"  - {error}")