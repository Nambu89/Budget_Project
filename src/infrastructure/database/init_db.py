"""
Script para inicializar la base de datos.
"""

from loguru import logger
from . import Base, engine
from .models import User, Budget


def init_db():
	"""Crea todas las tablas en la base de datos."""
	try:
		logger.info("Creando tablas en la base de datos...")
		Base.metadata.create_all(bind=engine)
		logger.info("✓ Base de datos inicializada correctamente")
	except Exception as e:
		logger.error(f"Error inicializando base de datos: {e}")
		raise


if __name__ == "__main__":
	init_db()