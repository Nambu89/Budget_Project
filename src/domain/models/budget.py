"""
Modelo Budget para datos del presupuesto completo.

Representa un presupuesto de reforma completo con proyecto,
cliente, partidas y totales.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, computed_field
from .project import Project
from .customer import Customer
from .budget_item import BudgetItem


class Budget(BaseModel):
    """
    Modelo de presupuesto completo.

    Contiene toda la información necesaria para generar un presupuesto
    de reforma: proyecto, cliente opcional, partidas y cálculos de totales.

    Attributes:
        proyecto: Datos del proyecto de reforma
        cliente: Datos del cliente (opcional)
        partidas: Lista de partidas del presupuesto
        descuento_porcentaje: Porcentaje de descuento aplicado (0-100)
        dias_validez: Días de validez del presupuesto
        fecha_creacion: Fecha de creación del presupuesto
    """

    model_config = {"validate_assignment": True}

    proyecto: Project = Field(..., description="Datos del proyecto")
    cliente: Optional[Customer] = Field(default=None, description="Datos del cliente")
    partidas: List[BudgetItem] = Field(default_factory=list, description="Partidas del presupuesto")
    descuento_porcentaje: float = Field(default=0.0, ge=0, le=100, description="Porcentaje de descuento")
    dias_validez: int = Field(default=30, gt=0, description="Días de validez del presupuesto")
    fecha_creacion: datetime = Field(default_factory=datetime.now, description="Fecha de creación")

    @computed_field
    @property
    def fecha_emision(self) -> datetime:
        """Fecha de emisión del presupuesto."""
        return self.fecha_creacion

    @computed_field
    @property
    def num_partidas(self) -> int:
        """Número de partidas en el presupuesto."""
        return len(self.partidas)

    @computed_field
    @property
    def numero_presupuesto(self) -> str:
        """Número único del presupuesto."""
        timestamp = self.fecha_creacion.strftime("%Y%m%d%H%M%S")
        return f"PRES-{timestamp}"

    @computed_field
    @property
    def fecha_emision_str(self) -> str:
        """Fecha de emisión formateada."""
        return self.fecha_creacion.strftime("%d/%m/%Y")

    @computed_field
    @property
    def fecha_validez_str(self) -> str:
        """Fecha de validez formateada."""
        fecha_validez = self.fecha_creacion + timedelta(days=self.dias_validez)
        return fecha_validez.strftime("%d/%m/%Y")

    @property
    def fecha_validez(self) -> datetime:
        """Fecha de validez del presupuesto."""
        return self.fecha_creacion + timedelta(days=self.dias_validez)

    @computed_field
    @property
    def tiene_cliente(self) -> bool:
        """Indica si el presupuesto tiene cliente asignado."""
        return self.cliente is not None

    @computed_field
    @property
    def subtotal(self) -> float:
        """Subtotal sin descuento ni IVA."""
        return sum(partida.subtotal for partida in self.partidas)

    @computed_field
    @property
    def importe_descuento(self) -> float:
        """Importe del descuento aplicado."""
        return self.subtotal * (self.descuento_porcentaje / 100)

    @computed_field
    @property
    def base_imponible(self) -> float:
        """Base imponible después del descuento."""
        return self.subtotal - self.importe_descuento

    @computed_field
    @property
    def iva_porcentaje(self) -> float:
        """Porcentaje de IVA aplicable."""
        return self.proyecto.iva_aplicable

    @computed_field
    @property
    def importe_iva(self) -> float:
        """Importe del IVA."""
        return self.base_imponible * (self.iva_porcentaje / 100)

    @computed_field
    @property
    def total(self) -> float:
        """Total final con IVA."""
        return self.base_imponible + self.importe_iva

    def agregar_partida(self, partida: BudgetItem) -> None:
        """
        Agrega una partida al presupuesto.

        Args:
            partida: Partida a agregar
        """
        self.partidas.append(partida)

    def agregar_partidas(self, partidas: List[BudgetItem]) -> None:
        """
        Agrega múltiples partidas al presupuesto.

        Args:
            partidas: Lista de partidas a agregar
        """
        self.partidas.extend(partidas)

    def limpiar_partidas(self) -> None:
        """Elimina todas las partidas del presupuesto."""
        self.partidas.clear()

    def eliminar_partida(self, indice: int) -> bool:
        """
        Quita una partida por índice.

        Args:
            indice: Índice de la partida a quitar

        Returns:
            bool: True si se quitó correctamente
        """
        if 0 <= indice < len(self.partidas):
            self.partidas.pop(indice)
            return True
        return False

    def resumen_por_categorias(self) -> dict:
        """
        Resumen de importes por categoría.

        Returns:
            dict: Diccionario con categoría -> importe
        """
        resumen = {}
        for partida in self.partidas:
            categoria = partida.categoria.display_name
            resumen[categoria] = resumen.get(categoria, 0) + partida.subtotal
        return resumen

    @property
    def resumen_texto(self) -> str:
        """
        Resumen textual del presupuesto.

        Returns:
            str: Descripción textual del presupuesto
        """
        lineas = [
            f"Presupuesto {self.numero_presupuesto}",
            f"Proyecto: {self.proyecto.tipo_inmueble.display_name} de {self.proyecto.metros_cuadrados}m²",
            f"Calidad: {self.proyecto.calidad_general.display_name}",
            f"Partidas: {self.num_partidas}",
            f"Subtotal: {self.subtotal:.2f}€",
            f"IVA ({self.iva_porcentaje}%): {self.importe_iva:.2f}€",
            f"Total: {self.total:.2f}€"
        ]
        if self.cliente:
            lineas.insert(1, f"Cliente: {self.cliente.nombre}")
        return "\n".join(lineas)
        """Representación string del presupuesto."""
        return f"Presupuesto {self.numero_presupuesto} - {self.total:.2f}€"
