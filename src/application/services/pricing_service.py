"""
Servicio de cálculo de precios.

Implementa toda la lógica de negocio para calcular
precios de partidas, paquetes y aplicar reglas comerciales.
"""

from typing import Optional
from loguru import logger

from ...config.settings import settings
from ...config.pricing_data import (
	PRICING_DATA,
	PACKAGES_DATA,
	get_precio_partida,
	get_precio_paquete,
	get_todas_categorias,
	get_partidas_categoria,
	get_todos_paquetes,
)
from ...domain.enums import PropertyType, QualityLevel, WorkCategory
from ...domain.models import BudgetItem


class PricingService:
	"""
	Servicio para cálculo de precios y reglas de negocio.
	
	Centraliza toda la lógica de:
	- Obtención de precios base
	- Aplicación de markup a partidas individuales
	- Cálculo de paquetes completos
	- Redondeo al alza
	- Cálculo de IVA
	"""
	
	def __init__(
		self,
		markup_partidas: Optional[float] = None,
		redondeo_alza: Optional[float] = None,
		iva_general: Optional[int] = None,
		iva_reducido: Optional[int] = None,
	):
		"""
		Inicializa el servicio de precios.
		
		Args:
			markup_partidas: % markup para partidas individuales (default: settings)
			redondeo_alza: % redondeo al alza (default: settings)
			iva_general: % IVA general (default: settings)
			iva_reducido: % IVA reducido vivienda habitual (default: settings)
		"""
		self.markup_partidas = markup_partidas or settings.markup_partidas_individuales
		self.redondeo_alza = redondeo_alza or settings.redondeo_alza
		self.iva_general = iva_general or settings.iva_general
		self.iva_reducido = iva_reducido or settings.iva_reducido
		
		logger.debug(
			f"PricingService inicializado: markup={self.markup_partidas}%, "
			f"redondeo={self.redondeo_alza}%, IVA={self.iva_general}/{self.iva_reducido}%"
		)
	

	def ajustar_precio_por_ipc(
		self,
		precio_base: float,
		ano_base: int = None,
		ano_actual: int = None,
		ipc_anual: float = None
	) -> float:
		"""Ajusta un precio según el IPC acumulado."""
		from datetime import datetime
		
		ano_base = ano_base or settings.ano_base_precios
		ano_actual = ano_actual or datetime.now().year
		ipc_anual = ipc_anual or settings.ipc_anual
		
		anos_transcurridos = ano_actual - ano_base
		if anos_transcurridos <= 0:
			return precio_base
		
		factor_ipc = (1 + ipc_anual / 100) ** anos_transcurridos
		precio_ajustado = round(precio_base * factor_ipc, 2)
		
		logger.debug(
			f"IPC aplicado: {precio_base:.2f}€ ({ano_base}) → "
			f"{precio_ajustado:.2f}€ ({ano_actual}) | "
			f"Factor: {factor_ipc:.4f} ({anos_transcurridos} años @ {ipc_anual}%)"
		)
		
		return precio_ajustado
	
	# ==========================================
	# Obtención de precios base
	# ==========================================
	
	def obtener_precio_partida(
		self,
		categoria: str,
		partida: str,
		calidad: QualityLevel = QualityLevel.ESTANDAR,
	) -> float:
		"""
		Obtiene el precio base de una partida.
		
		Args:
			categoria: Categoría de trabajo
			partida: Nombre de la partida
			calidad: Nivel de calidad
			
		Returns:
			float: Precio base sin markup
		"""
		precio_base = get_precio_partida(categoria, partida, calidad.value)
		return self.ajustar_precio_por_ipc(precio_base)
	
	def obtener_precio_paquete(
		self,
		paquete: str,
		calidad: QualityLevel = QualityLevel.ESTANDAR,
		metros: Optional[float] = None,
	) -> float:
		"""
		Obtiene el precio de un paquete completo.
		
		Args:
			paquete: Nombre del paquete
			calidad: Nivel de calidad
			metros: Metros cuadrados (para reformas integrales)
			
		Returns:
			float: Precio del paquete
		"""
		precio_base = get_precio_paquete(paquete, calidad.value, metros)
		return self.ajustar_precio_por_ipc(precio_base)
	
	def obtener_info_partida(
		self,
		categoria: str,
		partida: str,
	) -> Optional[dict]:
		"""
		Obtiene información completa de una partida.
		
		Args:
			categoria: Categoría de trabajo
			partida: Nombre de la partida
			
		Returns:
			dict: Info de la partida o None si no existe
		"""
		try:
			return PRICING_DATA[categoria][partida].copy()
		except KeyError:
			return None
	
	def obtener_info_paquete(self, paquete: str) -> Optional[dict]:
		"""
		Obtiene información completa de un paquete.
		
		Args:
			paquete: Nombre del paquete
			
		Returns:
			dict: Info del paquete o None si no existe
		"""
		try:
			return PACKAGES_DATA[paquete].copy()
		except KeyError:
			return None
	
	# ==========================================
	# Creación de partidas presupuestarias
	# ==========================================
	
	def crear_partida(
		self,
		categoria: WorkCategory,
		partida: str,
		cantidad: float,
		calidad: QualityLevel = QualityLevel.ESTANDAR,
		aplicar_markup: bool = True,
	) -> Optional[BudgetItem]:
		"""
		Crea una partida presupuestaria con precio calculado.
		
		Args:
			categoria: Categoría de trabajo
			partida: Nombre de la partida
			cantidad: Cantidad (m2, uds, etc.)
			calidad: Nivel de calidad
			aplicar_markup: Si aplicar markup de partida individual
			
		Returns:
			BudgetItem: Partida creada o None si no existe
		"""
		info = self.obtener_info_partida(categoria.value, partida)
		if not info:
			logger.warning(f"Partida no encontrada: {categoria.value}/{partida}")
			return None
		
		# Obtener precio base
		precio_base = info.get(calidad.value, 0)
		
		# Aplicar markup si es partida individual
		if aplicar_markup:
			precio_final = self.aplicar_markup(precio_base)
		else:
			precio_final = precio_base
		
		# Generar código
		codigo = f"{categoria.value[:3].upper()}-{partida[:8].upper()}"
		
		return BudgetItem(
			categoria=categoria,
			codigo=codigo,
			descripcion=info.get("descripcion", partida),
			unidad=info.get("unidad", "ud"),
			cantidad=cantidad,
			precio_unitario=round(precio_final, 2),
			calidad=calidad,
			es_paquete=False,
		)
	
	def _generar_items_incluidos_paquete(
		self, 
		paquete: str, 
		calidad: QualityLevel,
		info: dict
	) -> list[str]:
		"""
		Genera la lista de items incluidos en un paquete.
		
		Si el paquete tiene 'incluye' definido en pricing_data, usa eso.
		Si no, genera una lista genérica basada en el tipo de paquete.
		
		Args:
			paquete: Nombre del paquete
			calidad: Nivel de calidad
			info: Info del paquete desde pricing_data
			
		Returns:
			list[str]: Lista de items incluidos
		"""
		# Si ya tiene items definidos, usarlos
		if 'incluye' in info and info['incluye']:
			return info['incluye']
		
		# Generación automática según tipo de paquete
		items_base = []
		
		if 'cocina' in paquete.lower():
			items_base = [
				"Demolición de revestimientos existentes",
				"Instalación de nuevos azulejos y suelos",
				"Muebles de cocina",
				"Encimera",
				"Fregadero y grifo",
				"Instalación eléctrica",
				"Instalación de fontanería",
				"Pintura de paredes y techos",
			]
		elif 'bano' in paquete.lower() or 'baño' in paquete.lower():
			items_base = [
				"Demolición de sanitarios y revestimientos",
				"Azulejos y pavimento",
				"Sanitarios (inodoro, lavabo, bañera/ducha)",
				"Grifería completa",
				"Instalación eléctrica",
				"Instalación de fontanería",
				"Mampara de ducha",
				"Pintura",
			]
		elif 'reforma' in paquete.lower() and 'integral' in paquete.lower():
			items_base = [
				"Demolición y preparación",
				"Instalación eléctrica completa",
				"Instalación de fontanería",
				"Carpintería interior (puertas)",
				"Suelos en todas las estancias",
				"Pintura completa",
				"Sanitarios y griferías",
				"Cocina equipada",
				"Gestión de residuos",
			]
		elif 'pintura' in paquete.lower():
			items_base = [
				"Preparación de superficies",
				"Pintura de paredes",
				"Pintura de techos",
				"Pintura de carpintería",
				"Materiales de calidad",
			]
		elif 'suelo' in paquete.lower():
			items_base = [
				"Levantado de suelo existente",
				"Preparación de base",
				"Instalación de nuevo pavimento",
				"Rodapiés",
				"Retirada de escombros",
			]
		else:
			# Genérico
			items_base = [
				f"Trabajos de {info.get('nombre', 'reforma')}",
				f"Materiales de calidad {calidad.value}",
				"Mano de obra especializada",
				"Gestión de residuos",
				"Limpieza final",
			]
		
		# Añadir nota sobre calidad
		if calidad == QualityLevel.PREMIUM:
			items_base.append("✨ Acabados premium con materiales de primera calidad")
		elif calidad == QualityLevel.BASICO:
			items_base.append("Materiales económicos de calidad estándar")
		
		return items_base
	
	def crear_partidas_paquete(
		self,
		paquete: str,
		calidad: QualityLevel = QualityLevel.ESTANDAR,
		metros: Optional[float] = None,
	) -> list[BudgetItem]:
		"""
		Crea las partidas de un paquete completo.
		
		Los paquetes NO tienen markup (son más baratos que partidas sueltas).
		
		Args:
			paquete: Nombre del paquete
			calidad: Nivel de calidad
			metros: Metros cuadrados (para reformas integrales)
			
		Returns:
			list[BudgetItem]: Lista de partidas del paquete
		"""
		info = self.obtener_info_paquete(paquete)
		if not info:
			logger.warning(f"Paquete no encontrado: {paquete}")
			return []
		
		# Obtener precio total del paquete
		precio_total = self.obtener_precio_paquete(paquete, calidad, metros)
		
		# Crear código único
		codigo = f"PKG-{paquete[:8].upper()}"
		
		# Obtener o generar items incluidos
		items_incluidos = self._generar_items_incluidos_paquete(paquete, calidad, info)
		
		# Crear partida única representando el paquete completo
		partida = BudgetItem(
			categoria=WorkCategory.ALBANILERIA,  # Categoría genérica para paquetes
			codigo=codigo,
			descripcion=f"{info['nombre']} - {info['descripcion']}",
			unidad="ud" if metros is None else "m2",
			cantidad=1.0 if metros is None else metros,
			precio_unitario=round(precio_total / (metros or 1), 2),
			calidad=calidad,
			es_paquete=True,
			nombre_paquete=info['nombre'],
			items_incluidos=items_incluidos,
			notas=f"Incluye {len(items_incluidos)} conceptos",
		)
		
		logger.debug(f"Paquete creado: {codigo} con {len(items_incluidos)} items incluidos")
		
		return [partida]
	
	# ==========================================
	# Aplicación de reglas de negocio
	# ==========================================
	
	def aplicar_markup(self, precio: float) -> float:
		"""
		Aplica el markup a un precio base.
		
		Args:
			precio: Precio base
			
		Returns:
			float: Precio con markup
		"""
		factor = 1 + (self.markup_partidas / 100)
		return round(precio * factor, 2)
	
	def aplicar_redondeo_alza(self, total: float) -> float:
		"""
		Aplica el redondeo al alza sobre un total.
		
		Args:
			total: Total a redondear
			
		Returns:
			float: Total redondeado al alza
		"""
		factor = 1 + (self.redondeo_alza / 100)
		return round(total * factor, 2)
	
	def calcular_iva(
		self,
		base_imponible: float,
		es_vivienda_habitual: bool = False,
	) -> tuple[int, float]:
		"""
		Calcula el IVA aplicable.
		
		Args:
			base_imponible: Base sobre la que calcular
			es_vivienda_habitual: Si aplica IVA reducido
			
		Returns:
			tuple: (porcentaje_iva, importe_iva)
		"""
		porcentaje = self.iva_reducido if es_vivienda_habitual else self.iva_general
		importe = round(base_imponible * (porcentaje / 100), 2)
		return porcentaje, importe
	
	def calcular_total_con_iva(
		self,
		base_imponible: float,
		es_vivienda_habitual: bool = False,
	) -> dict:
		"""
		Calcula todos los importes finales.
		
		Args:
			base_imponible: Base imponible
			es_vivienda_habitual: Si aplica IVA reducido
			
		Returns:
			dict: Desglose completo de importes
		"""
		# Aplicar redondeo al alza a la base
		base_redondeada = self.aplicar_redondeo_alza(base_imponible)
		
		# Calcular IVA
		porcentaje_iva, importe_iva = self.calcular_iva(
			base_redondeada, 
			es_vivienda_habitual
		)
		
		# Total final
		total = round(base_redondeada + importe_iva, 2)
		
		return {
			"base_original": base_imponible,
			"redondeo_porcentaje": self.redondeo_alza,
			"redondeo_importe": round(base_redondeada - base_imponible, 2),
			"base_imponible": base_redondeada,
			"iva_porcentaje": porcentaje_iva,
			"iva_importe": importe_iva,
			"total": total,
		}
	
	# ==========================================
	# Comparativas y utilidades
	# ==========================================
	
	def comparar_partidas_vs_paquete(
		self,
		paquete: str,
		partidas: list[tuple[str, str, float]],  # [(categoria, partida, cantidad), ...]
		calidad: QualityLevel = QualityLevel.ESTANDAR,
		metros: Optional[float] = None,
	) -> dict:
		"""
		Compara el precio de partidas sueltas vs paquete completo.
		
		Útil para mostrar al cliente el ahorro del paquete.
		
		Args:
			paquete: Nombre del paquete
			partidas: Lista de (categoria, partida, cantidad)
			calidad: Nivel de calidad
			metros: Metros cuadrados
			
		Returns:
			dict: Comparativa con precios y ahorro
		"""
		# Calcular precio partidas sueltas (con markup)
		total_partidas = 0.0
		for cat, part, cant in partidas:
			precio = self.obtener_precio_partida(cat, part, calidad)
			precio_con_markup = self.aplicar_markup(precio)
			total_partidas += precio_con_markup * cant
		
		# Calcular precio paquete (sin markup)
		precio_paquete = self.obtener_precio_paquete(paquete, calidad, metros)
		
		# Calcular ahorro
		ahorro = total_partidas - precio_paquete
		ahorro_porcentaje = (ahorro / total_partidas * 100) if total_partidas > 0 else 0
		
		return {
			"precio_partidas_sueltas": round(total_partidas, 2),
			"precio_paquete": round(precio_paquete, 2),
			"ahorro_importe": round(ahorro, 2),
			"ahorro_porcentaje": round(ahorro_porcentaje, 1),
			"recomendacion": "paquete" if ahorro > 0 else "partidas",
		}
	
	def listar_categorias(self) -> list[dict]:
		"""
		Lista todas las categorías disponibles.
		
		Returns:
			list: Categorías con info
		"""
		return [
			{
				"valor": cat,
				"nombre": WorkCategory(cat).display_name,
				"icono": WorkCategory(cat).icono,
				"partidas": get_partidas_categoria(cat),
			}
			for cat in get_todas_categorias()
		]
	
	def listar_paquetes(self) -> list[dict]:
		"""
		Lista todos los paquetes disponibles.
		
		Returns:
			list: Paquetes con info
		"""
		return [
			{
				"valor": paq,
				"nombre": PACKAGES_DATA[paq]["nombre"],
				"descripcion": PACKAGES_DATA[paq]["descripcion"],
				"incluye": PACKAGES_DATA[paq].get("incluye", []),
			}
			for paq in get_todos_paquetes()
		]
	
	def obtener_rango_precios(
		self,
		categoria: str,
		partida: str,
	) -> dict:
		"""
		Obtiene el rango de precios de una partida (básico a premium).
		
		Args:
			categoria: Categoría
			partida: Partida
			
		Returns:
			dict: Precios por calidad
		"""
		info = self.obtener_info_partida(categoria, partida)
		if not info:
			return {}
		
		return {
			"basico": info.get("basico", 0),
			"estandar": info.get("estandar", 0),
			"premium": info.get("premium", 0),
			"unidad": info.get("unidad", "ud"),
		}


# Instancia singleton
_pricing_service: Optional[PricingService] = None


def get_pricing_service() -> PricingService:
	"""
	Obtiene la instancia del servicio de precios (singleton).
	
	Returns:
		PricingService: Instancia del servicio
	"""
	global _pricing_service
	if _pricing_service is None:
		_pricing_service = PricingService()
	return _pricing_service