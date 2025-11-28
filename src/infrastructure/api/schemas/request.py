"""
Request Schemas - Modelos Pydantic para requests de la API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProyectoRequest(BaseModel):
    """Datos del proyecto para calcular presupuesto."""
    
    tipo_inmueble: str = Field(
        ...,
        description="Tipo de inmueble: piso, vivienda, local, oficina"
    )
    metros_cuadrados: float = Field(
        ...,
        description="Superficie en metros cuadrados",
        gt=0
    )
    estado_actual: str = Field(
        default="normal",
        description="Estado: nuevo, normal, antiguo, ruina"
    )
    es_vivienda_habitual: bool = Field(
        default=False,
        description="Si es vivienda habitual (IVA reducido)"
    )
    calidad_general: str = Field(
        default="estandar",
        description="Calidad: basico, estandar, premium"
    )


class PaqueteRequest(BaseModel):
    """Paquete de trabajo a incluir."""
    
    id: str = Field(..., description="ID del paquete (ej: bano_completo)")
    cantidad: int = Field(default=1, description="Cantidad de paquetes", ge=1)
    metros: Optional[float] = Field(
        None,
        description="Metros cuadrados si aplica",
        gt=0
    )


class PartidaRequest(BaseModel):
    """Partida individual a incluir."""
    
    categoria: str = Field(..., description="Categoría (ej: pintura)")
    partida: str = Field(..., description="ID de la partida")
    cantidad: float = Field(..., description="Cantidad", gt=0)
    calidad: Optional[str] = Field(
        None,
        description="Calidad específica si difiere de la general"
    )


class TrabajosRequest(BaseModel):
    """Trabajos a realizar (paquetes + partidas)."""
    
    paquetes: List[PaqueteRequest] = Field(
        default_factory=list,
        description="Lista de paquetes"
    )
    partidas: List[PartidaRequest] = Field(
        default_factory=list,
        description="Lista de partidas individuales"
    )


class CalcularPresupuestoRequest(BaseModel):
    """Request completo para calcular presupuesto."""
    
    proyecto: ProyectoRequest
    trabajos: TrabajosRequest
    modo: str = Field(
        default="particular",
        description="Modo: particular o profesional"
    )
    pais: str = Field(
        default="ES",
        description="Código de país (ES, FR, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "proyecto": {
                    "tipo_inmueble": "piso",
                    "metros_cuadrados": 80,
                    "estado_actual": "normal",
                    "es_vivienda_habitual": True,
                    "calidad_general": "estandar"
                },
                "trabajos": {
                    "paquetes": [
                        {"id": "bano_completo", "cantidad": 1, "metros": 5}
                    ],
                    "partidas": [
                        {
                            "categoria": "pintura",
                            "partida": "pintura_plastica",
                            "cantidad": 200
                        }
                    ]
                },
                "modo": "particular",
                "pais": "ES"
            }
        }


class ClienteRequest(BaseModel):
    """Datos del cliente para generar PDF."""
    
    nombre: str = Field(..., description="Nombre completo")
    email: str = Field(..., description="Email")
    telefono: str = Field(..., description="Teléfono")
    direccion_obra: Optional[str] = Field(
        None,
        description="Dirección de la obra"
    )


class GenerarPDFRequest(BaseModel):
    """Request para generar PDF."""
    
    presupuesto_id: Optional[str] = Field(
        None,
        description="ID del presupuesto ya calculado"
    )
    cliente: ClienteRequest
    # Si no hay presupuesto_id, incluir datos completos
    presupuesto_data: Optional[dict] = Field(
        None,
        description="Datos completos del presupuesto si no hay ID"
    )
