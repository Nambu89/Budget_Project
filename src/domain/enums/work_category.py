"""
Enum para categorías de trabajo.

Define las diferentes categorías de partidas
disponibles en el sistema de presupuestos.

ACTUALIZADO: Añadida categoría PAQUETE
"""

from enum import Enum


class WorkCategory(str, Enum):
	"""
	Categorías de trabajo/partidas disponibles.
	
	Cada categoría agrupa partidas relacionadas
	del mismo oficio o especialidad.
	"""
	
	ALBANILERIA = "albanileria"
	FONTANERIA = "fontaneria"
	ELECTRICIDAD = "electricidad"
	CARPINTERIA = "carpinteria"
	PAQUETE = "paquete"
	
	@property
	def display_name(self) -> str:
		"""Nombre para mostrar en la UI."""
		nombres = {
			self.ALBANILERIA: "Albañilería",
			self.FONTANERIA: "Fontanería",
			self.ELECTRICIDAD: "Electricidad",
			self.CARPINTERIA: "Carpintería",
			self.PAQUETE: "Paquete Completo",
		}
		return nombres.get(self, self.value)

	@property
	def descripcion(self) -> str:
		"""Descripción de la categoría."""
		descripciones = {
			self.ALBANILERIA: "Suelos, paredes, alicatados, pintura y demoliciones",
			self.FONTANERIA: "Sanitarios, griferías e instalaciones de agua",
			self.ELECTRICIDAD: "Instalación eléctrica, puntos de luz y cuadros",
			self.CARPINTERIA: "Puertas, ventanas y armarios",
			self.PAQUETE: "Conjunto completo de trabajos (baño, cocina, reforma integral)",
		}
		return descripciones.get(self, "")

	@property
	def icono(self) -> str:
		"""Icono emoji para la UI."""
		iconos = {
			self.ALBANILERIA: "",
			self.FONTANERIA: "",
			self.ELECTRICIDAD: "",
			self.CARPINTERIA: "",
			self.PAQUETE: "",
		}
		return iconos.get(self, "")

	@property
	def color(self) -> str:
		"""Color asociado para la UI (hex)."""
		colores = {
			self.ALBANILERIA: "#dc3545",
			self.FONTANERIA: "#0dcaf0",
			self.ELECTRICIDAD: "#ffc107",
			self.CARPINTERIA: "#795548",
			self.PAQUETE: "#6f42c1",
		}
		return colores.get(self, "#000000")
	
	@classmethod
	def get_choices(cls) -> list[tuple[str, str]]:
		"""
		Retorna opciones para selectores de formulario.
		
		Returns:
			Lista de tuplas (valor, nombre_display)
		"""
		return [(item.value, f"{item.icono} {item.display_name}") for item in cls]
	
	@classmethod
	def get_all_with_info(cls) -> list[dict]:
		"""
		Retorna toda la información de las categorías.
		
		Returns:
			Lista de diccionarios con info completa
		"""
		return [
			{
				"value": item.value,
				"name": item.display_name,
				"description": item.descripcion,
				"icon": item.icono,
				"color": item.color,
			}
			for item in cls
		]