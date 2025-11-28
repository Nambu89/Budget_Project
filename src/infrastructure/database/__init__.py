"""
Database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from typing import Generator

from src.config.settings import settings

# Base declarativa para modelos
Base = declarative_base()

# Crear engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,  # Log SQL queries en debug
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sesiones de base de datos.
    
    Maneja automáticamente commit/rollback y cierre de sesión.
    
    Yields:
        Session: Sesión de SQLAlchemy
        
    Example:
        with get_db_session() as session:
            user = session.query(User).first()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    
    Debe llamarse al inicio de la aplicación.
    """
    # Importar modelos para que Base.metadata los conozca
    from .models import User, PasswordResetToken, Budget  # noqa: F401
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """
    Elimina todas las tablas (solo para desarrollo/testing).
    
    ⚠️ CUIDADO: Esto borra todos los datos.
    """
    from .models import User, PasswordResetToken, Budget  # noqa: F401
    Base.metadata.drop_all(bind=engine)
