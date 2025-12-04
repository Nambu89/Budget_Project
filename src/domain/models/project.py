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
		num_habitaciones: Número de habitaciones/salas (opcional) - NUEVO FASE 2
		calidad_general: Nivel de calidad por defecto
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
	
	num_habitaciones: Optional[int] = Field(
		default=None,
		ge=1,
		le=50,
		description="Número de habitaciones/salas/espacios"
	)
	
	calidad_general: QualityLevel = Field(
		default=QualityLevel.ESTANDAR,
		description="Nivel de calidad por defecto para el proyecto"
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
	def iva_aplicable(self) -> int:
		"""
		Retorna el porcentaje de IVA aplicable.
		
		NOTA: Desde FASE 1, siempre es 21% para todos los inmuebles.
		
		Returns:
			int: 21 (IVA general único)
		"""
		return 21
	
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
	
	@property
	def metros_por_habitacion(self) -> Optional[float]:
		"""
		Calcula metros cuadrados promedio por habitación.
		
		NUEVO FASE 2: Útil para validar coherencia de estimaciones.
		
		Returns:
			float: m² por habitación o None si no hay num_habitaciones
		"""
		if self.num_habitaciones and self.num_habitaciones > 0:
			return round(self.metros_cuadrados / self.num_habitaciones, 2)
		return None
	
	def to_dict_pdf(self) -> dict:
		"""
		Retorna diccionario con datos formateados para el PDF.
		
		Returns:
			dict: Datos listos para insertar en el PDF
		"""
		result = {
			"tipo_inmueble": self.tipo_inmueble_nombre,
			"metros": f"{self.metros_cuadrados:.2f} m²",
			"calidad": self.calidad_nombre,
			"estado": self.estado_actual.capitalize(),
			"iva": "21%",
			"ubicacion": self.ubicacion or "No especificada",
			"descripcion": self.descripcion or "",
		}
		
		# NUEVO FASE 2: Incluir info de habitaciones si existe
		if self.num_habitaciones:
			result["num_habitaciones"] = f"{self.num_habitaciones} habitaciones/salas"
			result["m2_por_habitacion"] = f"{self.metros_por_habitacion:.2f} m²/hab"
		
		return result
	
	def resumen_corto(self) -> str:
		"""
		Genera un resumen corto del proyecto.
		
		Returns:
			str: Resumen en una línea
		"""
		base = (
			f"{self.tipo_inmueble.icono} {self.tipo_inmueble_nombre} "
			f"de {self.metros_cuadrados:.0f} m² "
			f"({self.calidad_nombre})"
		)
		
		# NUEVO FASE 2: Añadir habitaciones al resumen
		if self.num_habitaciones:
			base += f" • {self.num_habitaciones} hab."
		
		return base