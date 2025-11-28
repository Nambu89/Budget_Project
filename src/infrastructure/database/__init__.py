"""
Database configuration con soporte automático SQLite/PostgreSQL.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from typing import Generator
from loguru import logger

from src.config.settings import settings

# Base declarativa
Base = declarative_base()

# Crear engine con configuración automática
engine = create_engine(
	settings.db_url,
	**settings.db_config
)

logger.info(f"Database engine creado")
logger.info(f"  Tipo: {settings.db_type}")
logger.info(f"  Entorno: {settings.environment}")

# Session factory
SessionLocal = sessionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine
)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
	"""Context manager para sesiones de BD."""
	session = SessionLocal()
	try:
		yield session
		session.commit()
	except Exception as e:
		session.rollback()
		logger.error(f"Error en transacción: {e}")
		raise
	finally:
		session.close()


def init_db():
	"""Inicializa la BD creando tablas."""
	try:
		from .models import User, PasswordResetToken, Budget  # noqa: F401
		
		# Crear directorio si es SQLite
		if settings.uses_sqlite():
			import os
			db_path = settings.db_url.replace("sqlite:///", "")
			os.makedirs(os.path.dirname(db_path), exist_ok=True)
			logger.info(f"Directorio BD creado: {os.path.dirname(db_path)}")
		
		logger.info("Creando tablas...")
		Base.metadata.create_all(bind=engine)
		logger.info("Tablas verificadas/creadas")
		
	except Exception as e:
		logger.error(f"Error inicializando BD: {e}")
		raise


def drop_all_tables():
	"""Elimina todas las tablas (solo desarrollo)."""
	if settings.environment == "production":
		raise ValueError("No se puede drop_all_tables en producción")
	
	from .models import User, PasswordResetToken, Budget  # noqa: F401
	Base.metadata.drop_all(bind=engine)


def test_connection():
	"""Prueba la conexión a la BD."""
	try:
		with engine.connect() as conn:
			result = conn.execute(text("SELECT 1"))
			result.fetchone()
		logger.info("Conexión a BD exitosa")
		return True
	except Exception as e:
		logger.error(f"Error conectando a BD: {e}")
		return False