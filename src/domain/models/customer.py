"""
Modelo Customer para datos del cliente con sanitización de seguridad.
"""

from typing import Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re
import html


class Customer(BaseModel):
	"""
	Modelo de datos del cliente con sanitización automática.
	
	Previene inyecciones XSS sanitizando todos los inputs de texto.
	"""
	
	nombre: str = Field(
		...,
		min_length=2,
		max_length=100,
		description="Nombre completo del cliente"
	)
	
	email: EmailStr = Field(
		...,
		description="Correo electrónico de contacto"
	)
	
	telefono: str = Field(
		...,
		min_length=9,
		max_length=15,
		description="Teléfono de contacto"
	)
	
	direccion_obra: Optional[str] = Field(
		default=None,
		max_length=200,
		description="Dirección donde se realizará la obra"
	)
	
	logo_path: Optional[str] = Field(
		default=None,
		description="Ruta al logo del cliente para el PDF"
	)
	
	notas: Optional[str] = Field(
		default=None,
		max_length=500,
		description="Notas adicionales del cliente"
	)
	
	@field_validator("telefono")
	@classmethod
	def validar_telefono(cls, v: str) -> str:
		"""
		Valida y normaliza el formato del teléfono.
		
		Acepta formatos españoles: +34 XXX XXX XXX, 6XX XXX XXX, 9XX XXX XXX
		"""
		# Eliminar espacios y guiones
		telefono_limpio = re.sub(r"[\s\-\.]", "", v)
		
		# Si empieza con 00, cambiar a +
		if telefono_limpio.startswith("00"):
			telefono_limpio = "+" + telefono_limpio[2:]
		
		# Validar formato
		patron = r"^(\+34)?[6789]\d{8}$"
		if not re.match(patron, telefono_limpio):
			raise ValueError(
				"Formato de teléfono inválido. Use formato español: "
				"+34 6XX XXX XXX o 6XX XXX XXX"
			)
		
		return telefono_limpio
	
	@field_validator("nombre", "direccion_obra", "notas")
	@classmethod
	def sanitize_text_inputs(cls, v: Optional[str]) -> Optional[str]:
		"""
		SEGURIDAD: Sanitiza inputs de texto para prevenir XSS.
		
		Escapa caracteres HTML peligrosos: <, >, &, ", '
		"""
		if v is None:
			return None
		
		# Sanitizar HTML
		sanitized = html.escape(v.strip())
		
		# Limitar caracteres especiales excesivos
		if len(sanitized) != len(v.strip()):
			# Se detectaron caracteres especiales, loguear por seguridad
			from loguru import logger
			logger.warning(f"Input sanitizado detectado: caracteres HTML escapados")
		
		return sanitized
	
	@field_validator("email")
	@classmethod
	def normalizar_email(cls, v: str) -> str:
		"""Normaliza el email a minúsculas."""
		return v.lower().strip()
	
	@property
	def telefono_formateado(self) -> str:
		"""Retorna el teléfono en formato legible."""
		tel = self.telefono
		if tel.startswith("+34"):
			tel = tel[3:]
		# Formato XXX XXX XXX
		return f"{tel[:3]} {tel[3:6]} {tel[6:]}"
	
	@property
	def tiene_logo(self) -> bool:
		"""Indica si el cliente tiene logo configurado."""
		return bool(self.logo_path)
	
	def to_dict_pdf(self) -> dict:
		"""
		Retorna diccionario con datos formateados para el PDF.
		
		Returns:
			dict: Datos listos para insertar en el PDF (ya sanitizados)
		"""
		return {
			"nombre": self.nombre,
			"email": self.email,
			"telefono": self.telefono_formateado,
			"direccion": self.direccion_obra or "No especificada",
			"notas": self.notas or "",
		}