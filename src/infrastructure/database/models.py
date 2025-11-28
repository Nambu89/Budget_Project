"""
Database models using SQLAlchemy ORM.
"""

from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from . import Base


class User(Base):
    """
    Modelo de usuario en la base de datos.
    
    Almacena información de autenticación y perfil de usuarios.
    """
    __tablename__ = "users"
    
    # Campos principales
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Información adicional
    telefono = Column(String, nullable=True)
    empresa = Column(String, nullable=True)
    
    # Metadata
    fecha_registro = Column(DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acceso = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Estadísticas
    num_presupuestos = Column(Integer, default=0, nullable=False)
    
    # Relationships
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    reset_tokens = relationship("PasswordResetToken", back_populates="user", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Compatible con el formato anterior de JSON para mantener
        compatibilidad con el código existente.
        
        Returns:
            dict: Representación del usuario
        """
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            "password_hash": self.password_hash,
            "telefono": self.telefono,
            "empresa": self.empresa,
            "fecha_registro": self.fecha_registro.isoformat() if self.fecha_registro else None,
            "ultimo_acceso": self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            "activo": self.activo,
            "num_presupuestos": self.num_presupuestos
        }
    
    def to_dict_safe(self) -> dict:
        """
        Convierte a diccionario sin información sensible.
        
        Returns:
            dict: Datos del usuario sin password_hash
        """
        data = self.to_dict()
        data.pop("password_hash", None)
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """
        Crea un usuario desde un diccionario.
        
        Útil para migración desde JSON.
        
        Args:
            data: Diccionario con datos del usuario
            
        Returns:
            User: Instancia del modelo
        """
        # Convertir fechas si son strings
        if isinstance(data.get('fecha_registro'), str):
            data['fecha_registro'] = datetime.fromisoformat(data['fecha_registro'])
        
        if isinstance(data.get('ultimo_acceso'), str):
            data['ultimo_acceso'] = datetime.fromisoformat(data['ultimo_acceso'])
        
        return cls(**data)
    
    def __repr__(self) -> str:
        return f"<User(email='{self.email}', nombre='{self.nombre}')>"


class PasswordResetToken(Base):
    """
    Modelo para tokens de recuperación de contraseña.
    
    Almacena tokens temporales para reset de contraseña con expiración.
    """
    __tablename__ = "password_reset_tokens"
    
    # Campos principales
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Relación con usuario
    user = relationship("User", back_populates="reset_tokens")
    
    @classmethod
    def create_token(cls, user_id: str, expiration_hours: int = 1) -> "PasswordResetToken":
        """
        Crea un nuevo token de reset.
        
        Args:
            user_id: ID del usuario
            expiration_hours: Horas hasta expiración (default: 1)
            
        Returns:
            PasswordResetToken: Token creado
        """
        token = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(hours=expiration_hours)
        
        return cls(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
    
    def is_valid(self) -> bool:
        """
        Verifica si el token es válido.
        
        Returns:
            bool: True si válido (no usado y no expirado)
        """
        if self.used:
            return False
        
        if datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    def mark_as_used(self) -> None:
        """Marca el token como usado."""
        self.used = True
        self.used_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<PasswordResetToken(user_id='{self.user_id}', valid={self.is_valid()})>"


# Import Budget model
from .budget_model import Budget  # noqa: F401
