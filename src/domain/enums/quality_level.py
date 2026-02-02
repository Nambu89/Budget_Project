"""
Enum para niveles de calidad.

Define los diferentes niveles de acabados y materiales
disponibles en el sistema de presupuestos.
"""

from enum import Enum


class QualityLevel(str, Enum):
	"""
	Niveles de calidad para materiales y acabados.
	
	Cada nivel tiene un factor de precio diferente
	y características específicas.
	"""
	
	BASICO = "basico"
	ESTANDAR = "estandar"
	PREMIUM = "premium"
	
	@property
	def display_name(self) -> str:
		"""Nombre para mostrar en la UI."""
		nombres = {
			self.BASICO: "Básico",
			self.ESTANDAR: "Estándar",
			self.PREMIUM: "Premium",
		}
		return nombres.get(self, self.value)
	
	@property
	def descripcion(self) -> str:
		"""Descripción del nivel de calidad."""
		descripciones = {
			self.BASICO: "Materiales económicos de buena relación calidad-precio. Ideal para inversiones o alquiler.",
			self.ESTANDAR: "Materiales de calidad media-alta. Equilibrio perfecto entre precio y durabilidad.",
			self.PREMIUM: "Materiales de alta gama y acabados de lujo. Máxima calidad y diseño.",
		}
		return descripciones.get(self, "")
	
	@property
	def icono(self) -> str:
		"""Icono emoji para la UI."""
		iconos = {
			self.BASICO: "",
			self.ESTANDAR: "",
			self.PREMIUM: "",
		}
		return iconos.get(self, "")
	
	@property
	def color(self) -> str:
		"""Color asociado para la UI (hex)."""
		colores = {
			self.BASICO: "#6c757d",      # Gris
			self.ESTANDAR: "#0d6efd",    # Azul
			self.PREMIUM: "#ffc107",     # Dorado
		}
		return colores.get(self, "#000000")
	
	@property
	def multiplicador(self) -> float:
		"""
		Factor multiplicador para precios según calidad.
		
		Returns:
			float: Factor de precio (0.8 para básico, 1.0 estándar, 1.5 premium)
		"""
		multiplicadores = {
			self.BASICO: 0.8,
			self.ESTANDAR: 1.0,
			self.PREMIUM: 1.5,
		}
		return multiplicadores.get(self, 1.0)
	
	@classmethod
	def get_choices(cls) -> list[tuple[str, str]]:
		"""
		Retorna opciones para selectores de formulario.

		Returns:
			Lista de tuplas (valor, nombre_display)
		"""
		return [(item.value, item.display_name) for item in cls]
	
	@classmethod
	def get_default(cls) -> "QualityLevel":
		"""Retorna el nivel de calidad por defecto."""
		return cls.ESTANDAR