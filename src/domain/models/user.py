"""
User Model - Modelo de usuario del sistema.
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
import uuid


class User(BaseModel):
    """
    Usuario del sistema.
    
    Representa un usuario registrado que puede generar presupuestos.
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID único del usuario"
    )
    
    email: EmailStr = Field(
        ...,
        description="Email del usuario (usado como username)"
    )
    
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre completo del usuario"
    )
    
    telefono: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Teléfono de contacto"
    )
    
    empresa: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nombre de la empresa (opcional)"
    )
    
    # Seguridad
    password_hash: str = Field(
        ...,
        description="Hash de la contraseña (SHA-256)"
    )
    
    # Metadata
    fecha_registro: datetime = Field(
        default_factory=datetime.now,
        description="Fecha de registro"
    )
    
    ultimo_acceso: Optional[datetime] = Field(
        default=None,
        description="Fecha del último acceso"
    )
    
    activo: bool = Field(
        default=True,
        description="Si el usuario está activo"
    )
    
    # Estadísticas
    num_presupuestos: int = Field(
        default=0,
        description="Número de presupuestos generados"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "nombre": "Juan Pérez",
                "telefono": "600123456",
                "empresa": "Reformas JP"
            }
        }
    
    def to_dict_safe(self) -> dict:
        """
        Retorna diccionario sin datos sensibles.
        
        Returns:
            dict: Datos del usuario sin password_hash
        """
        data = self.model_dump()
        data.pop("password_hash", None)
        return data
    
    def actualizar_ultimo_acceso(self) -> None:
        """Actualiza la fecha del último acceso."""
        self.ultimo_acceso = datetime.now()
    
    def incrementar_presupuestos(self) -> None:
        """Incrementa el contador de presupuestos."""
        self.num_presupuestos += 1
