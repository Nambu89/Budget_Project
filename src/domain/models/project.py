"""
Modelo Project para datos del proyecto de reforma.

Representa la información del proyecto/obra que se
va a presupuestar.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from ..enums.property_type import PropertyType
from ..enums.quality_level import QualityLevel


class Project(BaseModel):
    """
    Modelo de proyecto de reforma.
    
    Almacena la información básica del proyecto que
    se utilizará para generar el presupuesto.
    
    Attributes:
        tipo_inmueble: Tipo de propiedad (piso, vivienda, oficina, local)
        metros_cuadrados: Superficie total en m²
        calidad_general: Nivel de calidad por defecto
        es_vivienda_habitual: Si es vivienda habitual del cliente (IVA reducido)
        estado_actual: Estado actual del inmueble
        descripcion: Descripción adicional del proyecto
        ubicacion: Ciudad/zona donde se ubica
    """
    
    tipo_inmueble: PropertyType = Field(
        ...,
        description="Tipo de inmueble a reformar"
    )
    
    metros_cuadrados: float = Field(
        ...,
        gt=0,
        le=10000,
        description="Superficie total en metros cuadrados"
    )
    
    calidad_general: QualityLevel = Field(
        default=QualityLevel.ESTANDAR,
        description="Nivel de calidad por defecto para el proyecto"
    )
    
    es_vivienda_habitual: bool = Field(
        default=False,
        description="Si es la vivienda habitual del cliente"
    )
    
    estado_actual: Optional[str] = Field(
        default="normal",
        description="Estado actual del inmueble: nuevo, normal, antiguo, ruina"
    )
    
    descripcion: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Descripción adicional del proyecto"
    )
    
    ubicacion: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Ciudad/zona donde se ubica el inmueble"
    )
    
    @field_validator("estado_actual")
    @classmethod
    def validar_estado(cls, v: str) -> str:
        """Valida que el estado sea uno de los permitidos."""
        estados_validos = ["nuevo", "normal", "antiguo", "ruina"]
        if v and v.lower() not in estados_validos:
            raise ValueError(
                f"Estado inválido. Use uno de: {', '.join(estados_validos)}"
            )
        return v.lower() if v else "normal"
    
    @property
    def tipo_inmueble_nombre(self) -> str:
        """Nombre del tipo de inmueble para mostrar."""
        return self.tipo_inmueble.display_name
    
    @property
    def calidad_nombre(self) -> str:
        """Nombre del nivel de calidad para mostrar."""
        return self.calidad_general.display_name
    
    @property
    def puede_iva_reducido(self) -> bool:
        """
        Indica si el proyecto puede aplicar IVA reducido.
        
        Requiere que sea vivienda (piso/vivienda) Y sea vivienda habitual.
        """
        return (
            self.tipo_inmueble.es_vivienda_habitual and 
            self.es_vivienda_habitual
        )
    
    @property
    def iva_aplicable(self) -> int:
        """
        Retorna el porcentaje de IVA aplicable.
        
        Returns:
            int: 10 si aplica IVA reducido, 21 si no
        """
        return 10 if self.puede_iva_reducido else 21
    
    @property
    def factor_estado(self) -> float:
        """
        Factor multiplicador según estado del inmueble.
        
        Los inmuebles en peor estado pueden requerir más trabajo.
        
        Returns:
            float: Factor multiplicador (1.0 - 1.3)
        """
        factores = {
            "nuevo": 0.95,      # Menos trabajo
            "normal": 1.0,     # Base
            "antiguo": 1.1,    # Algo más de trabajo
            "ruina": 1.25,     # Mucho más trabajo
        }
        return factores.get(self.estado_actual, 1.0)
    
    def to_dict_pdf(self) -> dict:
        """
        Retorna diccionario con datos formateados para el PDF.
        
        Returns:
            dict: Datos listos para insertar en el PDF
        """
        return {
            "tipo_inmueble": self.tipo_inmueble_nombre,
            "metros": f"{self.metros_cuadrados:.2f} m²",
            "calidad": self.calidad_nombre,
            "estado": self.estado_actual.capitalize(),
            "vivienda_habitual": "Sí" if self.es_vivienda_habitual else "No",
            "iva": f"{self.iva_aplicable}%",
            "ubicacion": self.ubicacion or "No especificada",
            "descripcion": self.descripcion or "",
        }
    
    def resumen_corto(self) -> str:
        """
        Genera un resumen corto del proyecto.
        
        Returns:
            str: Resumen en una línea
        """
        return (
            f"{self.tipo_inmueble.icono} {self.tipo_inmueble_nombre} "
            f"de {self.metros_cuadrados:.0f} m² "
            f"({self.calidad_nombre})"
        )