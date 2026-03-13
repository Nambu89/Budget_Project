"""
Response Schemas - Modelos Pydantic para responses de la API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import date


class PartidaResponse(BaseModel):
    """Partida en el presupuesto."""
    
    descripcion: str
    categoria: str
    cantidad: float
    unidad: str
    precio_unitario: float
    subtotal: float
    es_paquete: bool = False
    calidad: str


class PresupuestoResponse(BaseModel):
    """Presupuesto calculado."""
    
    numero: str = Field(..., description="Número único del presupuesto")
    fecha_emision: str = Field(..., description="Fecha de emisión")
    fecha_validez: str = Field(..., description="Fecha de validez")
    
    # Totales
    subtotal: float = Field(..., description="Subtotal sin IVA")
    iva_porcentaje: int = Field(..., description="Porcentaje de IVA aplicado")
    iva_importe: float = Field(..., description="Importe del IVA")
    total: float = Field(..., description="Total con IVA")
    
    # Partidas
    partidas: List[PartidaResponse] = Field(
        default_factory=list,
        description="Lista de partidas"
    )
    
    # Desglose
    desglose_por_categoria: Dict[str, float] = Field(
        default_factory=dict,
        description="Desglose por categoría"
    )
    
    # Metadata
    num_partidas: int = Field(..., description="Número de partidas")
    dias_validez: int = Field(..., description="Días de validez")


class PaqueteInfo(BaseModel):
    """Información de un paquete disponible."""
    
    id: str
    nombre: str
    descripcion: str
    incluye: List[str]
    precios: Dict[str, Dict[str, Any]]  # {calidad: {precio_base, m2_referencia}}


class PartidaCatalogoInfo(BaseModel):
    """Información de una partida en el catálogo."""

    nombre: str
    unidad: str
    descripcion: str = ""


class CategoriaInfo(BaseModel):
    """Información de una categoría de trabajo."""

    id: str
    nombre: str
    icono: str
    partidas: List[PartidaCatalogoInfo]


class PaquetesResponse(BaseModel):
    """Lista de paquetes disponibles."""
    
    paquetes: List[PaqueteInfo]
    total: int


class CategoriasResponse(BaseModel):
    """Lista de categorías disponibles."""
    
    categorias: List[CategoriaInfo]
    total: int


class ErrorResponse(BaseModel):
    """Response de error."""
    
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class ExplicacionResponse(BaseModel):
    """Explicación del presupuesto generada por IA."""

    resumen_ejecutivo: str
    desglose_capitulos: List[Dict[str, Any]]
    observaciones_tecnicas: List[str]
    limitaciones_presupuesto: str
    texto_legal: str


class UserBudgetResponse(BaseModel):
    """Presupuesto guardado de un usuario."""

    id: str
    numero_presupuesto: str
    datos_proyecto: Dict[str, Any]
    partidas: List[Dict[str, Any]]
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[str] = None
    total_sin_iva: float
    total_con_iva: float
    iva_aplicado: float
    fecha_creacion: Optional[str] = None
    fecha_validez: Optional[str] = None


class UserBudgetsListResponse(BaseModel):
    """Lista de presupuestos de un usuario."""

    presupuestos: List[UserBudgetResponse]
    total: int


class GuardarPresupuestoResponse(BaseModel):
    """Respuesta tras guardar presupuesto."""

    id: str
    numero_presupuesto: str
    total: float
    guardado: bool
