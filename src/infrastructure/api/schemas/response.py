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


class CategoriaInfo(BaseModel):
    """Información de una categoría de trabajo."""
    
    id: str
    nombre: str
    icono: str
    partidas: List[str]


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
