"""
Modelo Budget para presupuestos de usuario.

Este archivo contiene el modelo Budget que se importará en models.py
"""

from sqlalchemy import Column, String, DateTime, Float, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import json

from src.infrastructure.database import Base


class Budget(Base):
    """
    Modelo de presupuesto en la base de datos.
    
    Almacena presupuestos vectorizados asociados a usuarios.
    El PDF se genera on-demand para ahorrar espacio.
    """
    __tablename__ = "budgets"
    
    # Campos principales
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    numero_presupuesto = Column(String, unique=True, nullable=False, index=True)
    
    # Datos del proyecto (JSON)
    datos_proyecto = Column(Text, nullable=False)  # JSON: {tipo, metros, calidad, etc}
    partidas = Column(Text, nullable=False)  # JSON: lista de partidas
    paquetes = Column(Text, nullable=False)  # JSON: lista de paquetes
    
    # Totales
    total_sin_iva = Column(Float, nullable=False)
    total_con_iva = Column(Float, nullable=False)
    iva_aplicado = Column(Float, nullable=False)
    
    # Metadata
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_validez = Column(DateTime, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    
    def to_dict(self) -> dict:
        """
        Convierte el modelo a diccionario.
        
        Returns:
            dict: Representación del presupuesto
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "numero_presupuesto": self.numero_presupuesto,
            "datos_proyecto": json.loads(self.datos_proyecto) if isinstance(self.datos_proyecto, str) else self.datos_proyecto,
            "partidas": json.loads(self.partidas) if isinstance(self.partidas, str) else self.partidas,
            "paquetes": json.loads(self.paquetes) if isinstance(self.paquetes, str) else self.paquetes,
            "total_sin_iva": self.total_sin_iva,
            "total_con_iva": self.total_con_iva,
            "iva_aplicado": self.iva_aplicado,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_validez": self.fecha_validez.isoformat() if self.fecha_validez else None,
            "activo": self.activo
        }
    
    def __repr__(self) -> str:
        return f"<Budget(numero='{self.numero_presupuesto}', user_id='{self.user_id}')>"
