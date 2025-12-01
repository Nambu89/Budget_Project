"""
Modelo Budget para el presupuesto completo.

Representa el presupuesto final con todos sus componentes:
proyecto, cliente, partidas, totales y metadatos.
"""

from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, computed_field
from uuid import uuid4

from .project import Project
from .customer import Customer
from .budget_item import BudgetItem
from ..enums.work_category import WorkCategory


class Budget(BaseModel):
    """
    Modelo de presupuesto completo.
    
    Agrupa toda la información del presupuesto incluyendo
    proyecto, cliente, partidas, cálculos y metadatos.
    
    Attributes:
        id: Identificador único del presupuesto
        numero_presupuesto: Número legible para mostrar
        proyecto: Datos del proyecto de reforma
        cliente: Datos del cliente
        partidas: Lista de partidas presupuestarias
        fecha_emision: Fecha de creación del presupuesto
        dias_validez: Días de validez del presupuesto
        notas_internas: Notas internas (no van al PDF)
        descuento_porcentaje: Descuento global aplicado
    """
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Identificador único"
    )
    
    numero_presupuesto: str = Field(
        default_factory=lambda: f"PRES-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:4].upper()}",
        description="Número de presupuesto legible"
    )
    
    proyecto: Project = Field(
        ...,
        description="Datos del proyecto de reforma"
    )
    
    cliente: Optional[Customer] = Field(
        default=None,
        description="Datos del cliente (opcional hasta el final)"
    )
    
    partidas: list[BudgetItem] = Field(
        default_factory=list,
        description="Lista de partidas presupuestarias"
    )
    
    fecha_emision: datetime = Field(
        default_factory=datetime.now,
        description="Fecha de emisión del presupuesto"
    )
    
    dias_validez: int = Field(
        default=30,
        ge=1,
        description="Días de validez del presupuesto"
    )
    
    notas_internas: Optional[str] = Field(
        default=None,
        description="Notas internas (no van al PDF)"
    )
    
    descuento_porcentaje: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Descuento global aplicado (%)"
    )
    
    # ==========================================
    # Campos calculados
    # ==========================================
    
    @computed_field
    @property
    def subtotal(self) -> float:
        """
        Suma de todas las partidas sin IVA ni descuentos.
        
        Returns:
            float: Subtotal bruto
        """
        return round(sum(p.subtotal for p in self.partidas), 2)
    
    @computed_field
    @property
    def importe_descuento(self) -> float:
        """
        Importe del descuento aplicado.
        
        Returns:
            float: Importe del descuento
        """
        return round(self.subtotal * (self.descuento_porcentaje / 100), 2)
    
    @computed_field
    @property
    def base_imponible(self) -> float:
        """
        Base imponible (subtotal - descuento).
        
        Returns:
            float: Base imponible SIN redondeo
        """
        return round(self.subtotal - self.importe_descuento, 2)
    
    @computed_field
    @property
    def base_con_redondeo(self) -> float:
        """
        Base imponible CON redondeo al alza del 5%.
        
        Returns:
            float: Base imponible redondeada
        """
        factor = 1.05  # 5% de redondeo al alza
        return round(self.base_imponible * factor, 2)
    
    @computed_field
    @property
    def importe_redondeo(self) -> float:
        """
        Importe del redondeo al alza (5%).
        
        Returns:
            float: Diferencia entre base con y sin redondeo
        """
        return round(self.base_con_redondeo - self.base_imponible, 2)
    
    @computed_field
    @property
    def iva_porcentaje(self) -> int:
        """
        Porcentaje de IVA aplicable según el proyecto.
        
        Returns:
            int: Porcentaje de IVA (10 o 21)
        """
        return self.proyecto.iva_aplicable
    
    @computed_field
    @property
    def importe_iva(self) -> float:
        """
        Importe del IVA calculado sobre la base CON redondeo.
        
        Returns:
            float: Importe del IVA
        """
        return round(self.base_con_redondeo * (self.iva_porcentaje / 100), 2)
    
    @computed_field
    @property
    def total(self) -> float:
        """
        Total del presupuesto (base con redondeo + IVA).
        
        Returns:
            float: Total final
        """
        return round(self.base_con_redondeo + self.importe_iva, 2)
    
    @property
    def fecha_validez(self) -> datetime:
        """Fecha hasta la que es válido el presupuesto."""
        return self.fecha_emision + timedelta(days=self.dias_validez)
    
    @property
    def fecha_emision_str(self) -> str:
        """Fecha de emisión formateada."""
        return self.fecha_emision.strftime("%d/%m/%Y")
    
    @property
    def fecha_validez_str(self) -> str:
        """Fecha de validez formateada."""
        return self.fecha_validez.strftime("%d/%m/%Y")
    
    @property
    def num_partidas(self) -> int:
        """Número total de partidas."""
        return len(self.partidas)
    
    @property
    def tiene_cliente(self) -> bool:
        """Indica si tiene datos de cliente."""
        return self.cliente is not None
    
    # ==========================================
    # Métodos de agregación
    # ==========================================
    
    def agregar_partida(self, partida: BudgetItem) -> None:
        """
        Agrega una partida al presupuesto.
        
        Args:
            partida: Partida a agregar
        """
        self.partidas.append(partida)
    
    def agregar_partidas(self, partidas: list[BudgetItem]) -> None:
        """
        Agrega múltiples partidas al presupuesto.
        
        Args:
            partidas: Lista de partidas a agregar
        """
        self.partidas.extend(partidas)
    
    def eliminar_partida(self, indice: int) -> Optional[BudgetItem]:
        """
        Elimina una partida por índice.
        
        Args:
            indice: Índice de la partida a eliminar
            
        Returns:
            BudgetItem eliminado o None si índice inválido
        """
        if 0 <= indice < len(self.partidas):
            return self.partidas.pop(indice)
        return None
    
    def limpiar_partidas(self) -> None:
        """Elimina todas las partidas."""
        self.partidas.clear()
    
    # ==========================================
    # Métodos de consulta
    # ==========================================
    
    def partidas_por_categoria(self, categoria: WorkCategory) -> list[BudgetItem]:
        """
        Filtra partidas por categoría.
        
        Args:
            categoria: Categoría a filtrar
            
        Returns:
            Lista de partidas de esa categoría
        """
        return [p for p in self.partidas if p.categoria == categoria]
    
    def subtotal_por_categoria(self, categoria: WorkCategory) -> float:
        """
        Subtotal de una categoría específica.
        
        Args:
            categoria: Categoría a sumar
            
        Returns:
            float: Subtotal de la categoría
        """
        return round(
            sum(p.subtotal for p in self.partidas_por_categoria(categoria)),
            2
        )
    
    def resumen_por_categorias(self) -> dict[str, float]:
        """
        Resumen de subtotales por categoría.
        
        Returns:
            dict: Categoría -> subtotal
        """
        resumen = {}
        for categoria in WorkCategory:
            subtotal = self.subtotal_por_categoria(categoria)
            if subtotal > 0:
                resumen[categoria.display_name] = subtotal
        return resumen
    
    # ==========================================
    # Métodos de aplicación de reglas de negocio
    # ==========================================
    
    def aplicar_markup_partidas_individuales(self, porcentaje: float) -> None:
        """
        Aplica markup a las partidas que no son de paquete.
        
        Args:
            porcentaje: Porcentaje de markup (ej: 15)
        """
        self.partidas = [
            p.aplicar_markup(porcentaje) for p in self.partidas
        ]
    
    def aplicar_redondeo_alza(self, porcentaje: float) -> float:
        """
        Calcula el total con redondeo al alza.
        
        Nota: No modifica el presupuesto, solo calcula.
        
        Args:
            porcentaje: Porcentaje de redondeo (ej: 5)
            
        Returns:
            float: Total redondeado al alza
        """
        factor = 1 + (porcentaje / 100)
        return round(self.total * factor, 2)
    
    # ==========================================
    # Métodos de exportación
    # ==========================================
    
    def to_dict_pdf(self) -> dict:
        """
        Retorna diccionario con todos los datos para el PDF.
        
        Returns:
            dict: Datos completos para generar el PDF
        """
        return {
            "numero": self.numero_presupuesto,
            "fecha_emision": self.fecha_emision_str,
            "fecha_validez": self.fecha_validez_str,
            "proyecto": self.proyecto.to_dict_pdf(),
            "cliente": self.cliente.to_dict_pdf() if self.cliente else {},
            "partidas": [p.to_dict_pdf() for p in self.partidas],
            "resumen_categorias": self.resumen_por_categorias(),
            "subtotal": f"{self.subtotal:,.2f} €",
            "descuento": f"{self.importe_descuento:,.2f} €" if self.descuento_porcentaje > 0 else None,
            "descuento_porcentaje": f"{self.descuento_porcentaje:.1f}%" if self.descuento_porcentaje > 0 else None,
            "base_imponible": f"{self.base_imponible:,.2f} €",
            "iva_porcentaje": f"{self.iva_porcentaje}%",
            "importe_iva": f"{self.importe_iva:,.2f} €",
            "total": f"{self.total:,.2f} €",
            "num_partidas": self.num_partidas,
        }
    
    def resumen_texto(self) -> str:
        """
        Genera un resumen en texto del presupuesto.
        
        Returns:
            str: Resumen legible
        """
        lineas = [
            f"📋 Presupuesto {self.numero_presupuesto}",
            f"📅 Emitido: {self.fecha_emision_str}",
            f"",
            f"🏠 {self.proyecto.resumen_corto()}",
            f"",
            f"📊 Resumen:",
            f"   Partidas: {self.num_partidas}",
            f"   Subtotal: {self.subtotal:,.2f} €",
        ]
        
        if self.descuento_porcentaje > 0:
            lineas.append(f"   Descuento ({self.descuento_porcentaje:.1f}%): -{self.importe_descuento:,.2f} €")
        
        lineas.extend([
            f"   Base imponible: {self.base_imponible:,.2f} €",
            f"   IVA ({self.iva_porcentaje}%): {self.importe_iva:,.2f} €",
            f"   ─────────────────",
            f"   💰 TOTAL: {self.total:,.2f} €",
        ])
        
        return "\n".join(lineas)