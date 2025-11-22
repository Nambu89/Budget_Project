"""
Modelo BudgetItem para partidas del presupuesto.

Representa una línea individual dentro del presupuesto,
ya sea una partida suelta o parte de un paquete.
"""

from typing import Optional
from pydantic import BaseModel, Field, computed_field
from ..enums.work_category import WorkCategory
from ..enums.quality_level import QualityLevel


class BudgetItem(BaseModel):
    """
    Modelo de partida presupuestaria.
    
    Representa una línea individual del presupuesto con
    su descripción, cantidad, precio y totales.
    
    Attributes:
        categoria: Categoría de trabajo (albañilería, fontanería, etc.)
        codigo: Código interno de la partida
        descripcion: Descripción detallada de la partida
        unidad: Unidad de medida (m2, ud, ml, etc.)
        cantidad: Cantidad de unidades
        precio_unitario: Precio por unidad sin IVA
        calidad: Nivel de calidad seleccionado
        es_paquete: Si forma parte de un paquete (no aplica markup)
        notas: Notas adicionales
    """
    
    categoria: WorkCategory = Field(
        ...,
        description="Categoría de trabajo"
    )
    
    codigo: str = Field(
        ...,
        max_length=20,
        description="Código interno de la partida"
    )
    
    descripcion: str = Field(
        ...,
        max_length=300,
        description="Descripción detallada de la partida"
    )
    
    unidad: str = Field(
        ...,
        max_length=20,
        description="Unidad de medida"
    )
    
    cantidad: float = Field(
        ...,
        gt=0,
        description="Cantidad de unidades"
    )
    
    precio_unitario: float = Field(
        ...,
        ge=0,
        description="Precio por unidad sin IVA"
    )
    
    calidad: QualityLevel = Field(
        default=QualityLevel.ESTANDAR,
        description="Nivel de calidad"
    )
    
    es_paquete: bool = Field(
        default=False,
        description="Si forma parte de un paquete"
    )
    
    nombre_paquete: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nombre del paquete (si es_paquete=True)"
    )
    
    items_incluidos: Optional[list[str]] = Field(
        default=None,
        description="Lista de items incluidos en el paquete"
    )
    
    notas: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Notas adicionales"
    )
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """
        Calcula el subtotal de la partida (cantidad * precio_unitario).
        
        Returns:
            float: Subtotal sin IVA
        """
        return round(self.cantidad * self.precio_unitario, 2)
    
    @property
    def categoria_nombre(self) -> str:
        """Nombre de la categoría para mostrar."""
        return self.categoria.display_name
    
    @property
    def calidad_nombre(self) -> str:
        """Nombre del nivel de calidad para mostrar."""
        return self.calidad.display_name
    
    def aplicar_markup(self, porcentaje: float) -> "BudgetItem":
        """
        Crea una copia con el markup aplicado al precio.
        
        Solo aplica si NO es parte de un paquete.
        
        Args:
            porcentaje: Porcentaje de markup (ej: 15 para 15%)
            
        Returns:
            BudgetItem: Nueva instancia con precio actualizado
        """
        if self.es_paquete:
            return self
        
        factor = 1 + (porcentaje / 100)
        nuevo_precio = round(self.precio_unitario * factor, 2)
        
        return self.model_copy(update={"precio_unitario": nuevo_precio})
    
    def to_dict_pdf(self) -> dict:
        """
        Retorna diccionario con datos formateados para el PDF.
        
        Returns:
            dict: Datos listos para insertar en el PDF
        """
        return {
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "unidad": self.unidad,
            "cantidad": f"{self.cantidad:.2f}",
            "precio_unitario": f"{self.precio_unitario:.2f} €",
            "subtotal": f"{self.subtotal:.2f} €",
            "calidad": self.calidad_nombre,
        }
    
    @classmethod
    def crear_partida(
        cls,
        categoria: WorkCategory,
        nombre_partida: str,
        descripcion: str,
        unidad: str,
        cantidad: float,
        precio: float,
        calidad: QualityLevel = QualityLevel.ESTANDAR,
    ) -> "BudgetItem":
        """
        Factory method para crear partidas de forma sencilla.
        
        Args:
            categoria: Categoría de trabajo
            nombre_partida: Nombre corto de la partida
            descripcion: Descripción completa
            unidad: Unidad de medida
            cantidad: Cantidad
            precio: Precio unitario
            calidad: Nivel de calidad
            
        Returns:
            BudgetItem: Nueva instancia
        """
        # Generar código automático
        codigo = f"{categoria.value[:3].upper()}-{nombre_partida[:5].upper()}"
        
        return cls(
            categoria=categoria,
            codigo=codigo,
            descripcion=descripcion,
            unidad=unidad,
            cantidad=cantidad,
            precio_unitario=precio,
            calidad=calidad,
            es_paquete=False,
        )