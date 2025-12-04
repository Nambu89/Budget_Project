"""
Enum para tipos de inmueble.

Define los diferentes tipos de propiedades que pueden
ser objeto de reforma en el sistema.
"""

from enum import Enum


class PropertyType(str, Enum):
	"""
	Tipos de inmueble disponibles para reforma.
	
	Hereda de str para facilitar serialización JSON
	y comparaciones con strings.
	"""
	
	PISO = "piso"
	VIVIENDA = "vivienda"
	OFICINA = "oficina"
	LOCAL = "local"
	
	@property
	def display_name(self) -> str:
		"""Nombre para mostrar en la UI."""
		nombres = {
			self.PISO: "Piso",
			self.VIVIENDA: "Vivienda independiente",
			self.OFICINA: "Oficina",
			self.LOCAL: "Local comercial",
		}
		return nombres.get(self, self.value)
	
	@property
	def icono(self) -> str:
		"""Icono emoji para la UI."""
		iconos = {
			self.PISO: "🏢",
			self.VIVIENDA: "🏠",
			self.OFICINA: "🏢",
			self.LOCAL: "🏪",
		}
		return iconos.get(self, "🏗️")
	
	@classmethod
	def get_choices(cls) -> list[tuple[str, str]]:
		"""
		Retorna opciones para selectores de formulario.
		
		Returns:
			Lista de tuplas (valor, nombre_display)
		"""
		return [(item.value, f"{item.icono} {item.display_name}") for item in cls]