"""
Servicio de cálculo de precios y aplicación de reglas de negocio.

ACTUALIZADO:
- Línea 162-189: Método crear_partidas_paquete() con items_incluidos completos
- Añadidos items detallados para baño_completo, cocina_completa, reforma_integral
"""

from typing import Optional
from loguru import logger
import math

from ...domain.models.budget import Budget
from ...domain.models.budget_item import BudgetItem
from ...domain.models.project import Project
from ...domain.enums.quality_level import QualityLevel
from ...domain.enums.work_category import WorkCategory
from ...config.pricing_data import (
	PRICING_DATA,
	PACKAGES_DATA,
	get_precio_partida,
	get_precio_paquete,
)
from ...config.settings import Settings


class PricingService:
	"""
	Servicio centralizado para cálculos de precios.
	
	Aplica reglas de negocio, markups, y gestiona
	la lógica de pricing del sistema.
	"""
	
	def __init__(self, settings: Optional[Settings] = None):
		"""
		Inicializa el servicio de pricing.
		
		Args:
			settings: Configuración global del sistema (opcional)
		"""
		self.settings = settings or Settings()
		self.pricing_data = PRICING_DATA
		self.packages_data = PACKAGES_DATA
	
	def calcular_precio_unitario(
		self,
		codigo_partida: str,
		calidad: QualityLevel
	) -> float:
		"""
		Calcula el precio unitario de una partida según calidad.
		
		Args:
			codigo_partida: Código único de la partida
			calidad: Nivel de calidad solicitado
			
		Returns:
			float: Precio unitario
			
		Raises:
			ValueError: Si el código de partida no existe
		"""
		if codigo_partida not in self.pricing_data:
			raise ValueError(f"Partida '{codigo_partida}' no encontrada")
		
		partida_data = self.pricing_data[codigo_partida]
		precios = partida_data.get("precios", {})
		
		# Obtener precio según calidad
		precio = precios.get(calidad.value, precios.get("estandar", 0.0))
		
		logger.debug(
			f"Precio unitario calculado: {codigo_partida} "
			f"({calidad.value}) = {precio} €"
		)
		
		return precio
	
	def crear_partida(
		self,
		categoria: WorkCategory,
		partida: str,
		cantidad: float,
		calidad: QualityLevel,
		aplicar_markup: bool = True,
	) -> Optional[BudgetItem]:
		"""
		Crea una partida presupuestaria con todos sus datos.
		
		Args:
			categoria: Categoría de trabajo
			partida: Nombre de la partida
			cantidad: Cantidad (m2, uds, ml, etc.)
			calidad: Nivel de calidad
			aplicar_markup: Si aplica markup del 15%
			
		Returns:
			BudgetItem o None si no existe la partida
		"""
		# Buscar partida en pricing_data
		categoria_key = categoria.value
		
		if categoria_key not in PRICING_DATA:
			logger.warning(f"Categoría '{categoria_key}' no encontrada")
			return None
		
		partidas_categoria = PRICING_DATA[categoria_key]
		
		if partida not in partidas_categoria:
			logger.warning(f"Partida '{partida}' no encontrada en '{categoria_key}'")
			return None
		
		partida_data = partidas_categoria[partida]
		
		# Obtener precio según calidad
		precio_base = partida_data.get(calidad.value, partida_data.get("estandar", 0.0))
		
		# Aplicar markup si corresponde
		precio_final = precio_base * (1.15 if aplicar_markup else 1.0)
		
		# Crear BudgetItem
		budget_item = BudgetItem(
			codigo=f"{categoria_key.upper()[:3]}-{partida.upper()[:6]}",
			descripcion=partida_data.get("descripcion", partida.replace("_", " ").title()),
			cantidad=cantidad,
			unidad=partida_data.get("unidad", "ud"),
			precio_unitario=round(precio_final, 2),
			categoria=categoria,
			calidad=calidad,
			es_paquete=False,
		)
		
		logger.debug(f"Partida creada: {budget_item.descripcion} x {cantidad}")
		
		return budget_item
	
	def crear_partidas_paquete(
		self,
		paquete: str,
		calidad: QualityLevel,
		metros: float,
	) -> list[BudgetItem]:
		"""
		Crea todas las partidas de un paquete completo CON items_incluidos.
		
		Los paquetes NO tienen markup (incentivo comercial).
		
		ACTUALIZADO: Ahora incluye la lista completa de items_incluidos
		para que se muestre el desglose en el PDF.
		
		Args:
			paquete: Nombre del paquete (bano_completo, cocina_completa, etc.)
			calidad: Nivel de calidad
			metros: Metros cuadrados del espacio
			
		Returns:
			list[BudgetItem]: Lista de partidas del paquete
		"""
		if paquete not in PACKAGES_DATA:
			logger.warning(f"Paquete '{paquete}' no encontrado")
			return []
		
		paquete_data = PACKAGES_DATA[paquete]
		
		# Calcular precio total del paquete
		precio_total = get_precio_paquete(paquete, calidad.value, metros)
		
		# Obtener lista completa de items incluidos según el paquete
		items_incluidos = self._obtener_items_paquete(paquete, calidad)
		
		# Crear item único del paquete CON items_incluidos
		budget_item = BudgetItem(
			codigo=f"PKG-{paquete.upper()[:8]}",
			descripcion=paquete_data.get("nombre", paquete.replace("_", " ").title()),
			cantidad=1,
			unidad="conjunto",
			precio_unitario=round(precio_total, 2),
			categoria=WorkCategory.PAQUETE,
			calidad=calidad,
			es_paquete=True,
			items_incluidos=items_incluidos,  # ← AÑADIDO: Lista completa de items
			nombre_paquete=paquete_data.get("nombre", paquete.replace("_", " ").title()),
			notas=f"Paquete completo de {metros:.0f}m² - Calidad {calidad.display_name}",
		)
		
		logger.info(
			f"Paquete '{paquete}' creado: {precio_total:.2f}€ "
			f"({calidad.value}, {metros}m²) con {len(items_incluidos)} items incluidos"
		)
		
		return [budget_item]
	
	def _obtener_items_paquete(self, paquete: str, calidad: QualityLevel) -> list[str]:
		"""
		Obtiene la lista completa de items incluidos en un paquete.
		
		Args:
			paquete: Nombre del paquete
			calidad: Nivel de calidad
			
		Returns:
			list[str]: Lista de conceptos incluidos
		"""
		# Mapeo de items según tipo de paquete y calidad
		items_por_paquete = {
			"bano_completo": {
				"basica": [
					"Demolición y retirada de sanitarios antiguos",
					"Alicatado de paredes con azulejo cerámico estándar",
					"Solado con gres porcelánico básico",
					"Inodoro con cisterna de doble descarga",
					"Lavabo de cerámica con mueble básico",
					"Plato de ducha acrílico con mampara básica",
					"Grifería cromada estándar",
					"Instalación de fontanería completa",
					"Instalación eléctrica con punto de luz y enchufe",
					"Extractor de aire básico",
					"Accesorios básicos (toallero, portarrollos)",
				],
				"estandar": [
					"Demolición y retirada de sanitarios antiguos",
					"Alicatado de paredes con azulejo de calidad media",
					"Solado con gres porcelánico de calidad media",
					"Inodoro suspendido con cisterna empotrada",
					"Lavabo de cerámica con mueble de melamina",
					"Plato de ducha de resina con mampara de vidrio templado",
					"Grifería cromada monomando de calidad media",
					"Instalación de fontanería completa con válvulas de corte",
					"Instalación eléctrica con focos LED empotrables",
					"Extractor de aire con higrostato",
					"Accesorios de baño cromados (toallero, portarrollos, jabonera)",
					"Espejo con luz LED integrada",
				],
				"premium": [
					"Demolición y retirada de sanitarios antiguos",
					"Alicatado de paredes con azulejo porcelánico de diseño",
					"Solado con gres porcelánico rectificado gran formato",
					"Inodoro suspendido con función de bidet integrado",
					"Lavabo de diseño con encimera y mueble lacado",
					"Plato de ducha extraplano de carga mineral con mampara de vidrio antical",
					"Grifería termostática de marcas premium",
					"Sistema de hidromasaje en ducha",
					"Instalación de fontanería completa con válvulas empotradas",
					"Instalación eléctrica con iluminación LED regulable",
					"Extractor de aire con sensor de humedad y temporizador",
					"Accesorios de baño de diseño (toallero térmico, portarrollos)",
					"Espejo retroiluminado con sistema antivaho",
					"Suelo radiante eléctrico",
				],
			},
			"cocina_completa": {
				"basica": [
					"Demolición y retirada de muebles antiguos",
					"Muebles de cocina en melamina blanca",
					"Encimera laminada de 28mm",
					"Fregadero de acero inoxidable con grifo monomando",
					"Placa vitrocerámica de 4 fuegos",
					"Horno eléctrico multifunción básico",
					"Campana extractora convencional",
					"Alicatado de frente de cocina con azulejo básico",
					"Instalación eléctrica con tomas de corriente",
					"Instalación de fontanería completa",
					"Iluminación con fluorescente",
				],
				"estandar": [
					"Demolición y retirada de muebles antiguos",
					"Muebles de cocina en melamina con tiradores de aluminio",
					"Encimera de cuarzo de 20mm",
					"Fregadero de acero inoxidable bajo encimera con grifo extraíble",
					"Placa de inducción de 4 zonas",
					"Horno eléctrico multifunción con limpieza pirolítica",
					"Campana extractora decorativa de 60cm",
					"Microondas integrable",
					"Lavavajillas integrable de 12 cubiertos",
					"Frigorífico combi independiente",
					"Alicatado de frente de cocina con azulejo porcelánico",
					"Instalación eléctrica completa con circuito independiente",
					"Instalación de fontanería con tomas de agua individuales",
					"Iluminación LED bajo muebles altos",
					"Zócalo rodapié impermeable",
				],
				"premium": [
					"Demolición y retirada de muebles antiguos",
					"Muebles de cocina lacados con sistema push-pull sin tiradores",
					"Encimera de cuarzo Silestone o similar de 30mm",
					"Fregadero bajo encimera con grifo profesional con caño alto",
					"Placa de inducción con extracción integrada",
					"Horno eléctrico multifunción con vapor integrado",
					"Campana extractora de techo o integrada en encimera",
					"Microondas integrable con grill",
					"Lavavajillas totalmente integrable de alta gama con sistema silencioso",
					"Frigorífico combi integrable de clase A+++",
					"Cajonera con sistema de cierre amortiguado",
					"Columna de electrodomésticos integrada",
					"Alicatado de frente con porcelánico gran formato o cristal templado",
					"Instalación eléctrica domótica con enchufes USB",
					"Instalación de fontanería con sistema anti-inundación",
					"Iluminación LED regulable bajo muebles y en interior de cajones",
					"Sistema de organización interior de cajones",
					"Isla central o península con desayunador (si espacio lo permite)",
				],
			},
			"reforma_integral": {
				"basica": [
					"Demoliciones necesarias y retirada de escombros",
					"Reforma completa de instalaciones eléctricas",
					"Reforma completa de instalaciones de fontanería",
					"Solado de toda la vivienda con gres porcelánico básico",
					"Alicatado de baño y cocina con azulejo cerámico",
					"Pintura lisa en toda la vivienda con plástica mate",
					"Puertas de paso lacadas blancas con premarco",
					"Rodapié de DM lacado blanco",
					"Baño completo de calidad básica",
					"Cocina completa de calidad básica",
					"Mecanismos eléctricos blancos",
					"Luminarias básicas en todas las estancias",
				],
				"estandar": [
					"Demoliciones necesarias y gestión de escombros con contenedor",
					"Reforma completa de instalación eléctrica con nuevos circuitos",
					"Reforma completa de instalación de fontanería con tuberías multicapa",
					"Reforma de instalación de gas con llave de corte individual",
					"Solado de toda la vivienda con gres porcelánico de calidad media",
					"Alicatado de baño y cocina con azulejo porcelánico",
					"Techos con moldura de escayola",
					"Pintura lisa en toda la vivienda con plástica premium",
					"Puertas de paso lacadas con sistema de cierre amortiguado",
					"Armarios empotrados con puertas correderas",
					"Rodapié de DM lacado blanco de 10cm",
					"Baño completo de calidad estándar",
					"Cocina completa de calidad estándar con electrodomésticos",
					"Climatización con splits en salón y habitaciones",
					"Mecanismos eléctricos táctiles con marco cromado",
					"Luminarias LED en todas las estancias",
					"Video portero con monitor",
					"Sistema de domótica básica (persianas motorizadas)",
				],
				"premium": [
					"Proyecto técnico y dirección de obra",
					"Demoliciones necesarias con protección de elementos a conservar",
					"Gestión integral de licencias y permisos",
					"Reforma completa de instalación eléctrica con sistema domótico avanzado",
					"Reforma completa de fontanería con sistema anti-inundación",
					"Sistema de aerotermia para calefacción y ACS",
					"Suelo radiante en toda la vivienda",
					"Solado con porcelánico rectificado gran formato",
					"Alicatado con materiales premium (piedra natural, porcelánico de diseño)",
					"Falso techo continuo con iluminación LED perimetral",
					"Pintura con revestimientos texturizados en zonas destacadas",
					"Puertas correderas empotradas con herrajes ocultos",
					"Armarios empotrados a medida con interior organizado",
					"Baño principal completo de calidad premium con hidromasaje",
					"Baño secundario de calidad estándar",
					"Cocina premium con isla central y electrodomésticos de alta gama",
					"Sistema de climatización por conductos con zonas independientes",
					"Sistema domótico completo (luces, persianas, climatización, seguridad)",
					"Instalación de videoportero IP con control remoto",
					"Sistema de audio ambiental",
					"Cargador para vehículo eléctrico (si garaje disponible)",
					"Revestimientos especiales en salón (madera, piedra, etc.)",
					"Iluminación LED regulable en todas las estancias",
					"Sistema de purificación de aire",
				],
			},
		}
		
		# Obtener items del paquete y calidad específicos
		items = items_por_paquete.get(paquete, {}).get(calidad.value, [])
		
		if not items:
			# Fallback: usar items genéricos del paquete en PACKAGES_DATA
			paquete_data = PACKAGES_DATA.get(paquete, {})
			items = paquete_data.get("incluye", [
				"Incluye todos los materiales y mano de obra necesarios",
				"Transporte de materiales",
				"Limpieza final de la obra",
			])
		
		return items
	
	def obtener_precio_paquete(
		self,
		paquete: str,
		calidad: QualityLevel,
		metros: float,
	) -> float:
		"""
		Obtiene el precio de un paquete sin crear las partidas.
		
		Args:
			paquete: Nombre del paquete
			calidad: Nivel de calidad
			metros: Metros cuadrados
			
		Returns:
			float: Precio total del paquete
		"""
		return get_precio_paquete(paquete, calidad.value, metros)
	
	def aplicar_markup_partida(
		self,
		partida: BudgetItem,
		porcentaje: float
	) -> BudgetItem:
		"""
		Aplica markup a una partida individual.
		
		Args:
			partida: Partida original
			porcentaje: Porcentaje de markup (ej: 15 para 15%)
			
		Returns:
			BudgetItem: Nueva partida con markup aplicado
		"""
		nuevo_precio = partida.precio_unitario * (1 + porcentaje / 100)
		
		return BudgetItem(
			codigo=partida.codigo,
			descripcion=partida.descripcion,
			cantidad=partida.cantidad,
			unidad=partida.unidad,
			precio_unitario=round(nuevo_precio, 2),
			categoria=partida.categoria,
			calidad=partida.calidad,
			notas=partida.notas,
		)
	
	def calcular_iva(self, base_imponible: float, proyecto: Project) -> dict:
		"""
		Calcula el IVA aplicable según el proyecto.
		
		FASE 1: Siempre aplica IVA general del 21%.
		
		Args:
			base_imponible: Base sobre la que calcular el IVA
			proyecto: Datos del proyecto
			
		Returns:
			dict: {
				'porcentaje': int,
				'importe': float,
				'tipo': str
			}
		"""
		# FASE 1: IVA fijo al 21%
		porcentaje = self.settings.iva_general
		importe = round(base_imponible * (porcentaje / 100), 2)
		
		logger.info(
			f"IVA calculado: {porcentaje}% sobre {base_imponible:.2f} € "
			f"= {importe:.2f} €"
		)
		
		return {
			'porcentaje': porcentaje,
			'importe': importe,
			'tipo': 'general'
		}
	
	def aplicar_descuento(
		self,
		presupuesto: Budget,
		porcentaje: float,
		motivo: Optional[str] = None
	) -> Budget:
		"""
		Aplica un descuento global al presupuesto.
		
		Args:
			presupuesto: Presupuesto original
			porcentaje: Porcentaje de descuento (0-100)
			motivo: Razón del descuento (opcional)
			
		Returns:
			Budget: Presupuesto con descuento aplicado
		"""
		if not 0 <= porcentaje <= 100:
			raise ValueError("El porcentaje debe estar entre 0 y 100")
		
		presupuesto.descuento_porcentaje = porcentaje
		
		if motivo:
			nota_actual = presupuesto.notas_internas or ""
			presupuesto.notas_internas = f"{nota_actual}\nDescuento: {motivo}".strip()
		
		logger.info(
			f"Descuento aplicado: {porcentaje}% "
			f"({presupuesto.importe_descuento:.2f} €)"
		)
		
		return presupuesto
	
	def aplicar_factor_estado(
		self,
		partidas: list[BudgetItem],
		proyecto: Project
	) -> list[BudgetItem]:
		"""
		Aplica factor multiplicador según estado del inmueble.
		
		Args:
			partidas: Lista de partidas originales
			proyecto: Datos del proyecto con estado
			
		Returns:
			list[BudgetItem]: Partidas con factor aplicado
		"""
		factor = proyecto.factor_estado
		
		if factor == 1.0:
			return partidas
		
		partidas_ajustadas = []
		for partida in partidas:
			nuevo_precio = partida.precio_unitario * factor
			partida_ajustada = BudgetItem(
				codigo=partida.codigo,
				descripcion=partida.descripcion,
				cantidad=partida.cantidad,
				unidad=partida.unidad,
				precio_unitario=round(nuevo_precio, 2),
				categoria=partida.categoria,
				calidad=partida.calidad,
				notas=partida.notas,
			)
			partidas_ajustadas.append(partida_ajustada)
		
		logger.info(
			f"Factor de estado aplicado: {factor} "
			f"(estado: {proyecto.estado_actual})"
		)
		
		return partidas_ajustadas
	
	def calcular_estimaciones_heuristicas(self, proyecto: Project) -> dict:
		"""
		Calcula estimaciones usando fórmulas heurísticas simples.
		
		Fórmulas basadas en experiencia del sector:
		- Paredes: ~2.5x los m² totales (altura promedio 2.5m)
		- Rodapiés: ~perímetro = √(m² totales) * 4
		- Puertas: 1 cada 15-20 m²
		
		Args:
			proyecto: Datos del proyecto
			
		Returns:
			dict: Estimaciones básicas
		"""
		m2_totales = proyecto.metros_cuadrados
		
		# Estimar m² de paredes (ancho × alto)
		# Asumiendo altura promedio de 2.5m
		perimetro_aprox = math.sqrt(m2_totales) * 4
		m2_paredes = round(perimetro_aprox * 2.5, 2)
		
		# Metros lineales de rodapiés (perímetro)
		ml_rodapies = round(perimetro_aprox, 2)
		
		# Número de puertas (1 cada 15-20 m²)
		num_puertas = max(1, round(m2_totales / 17))
		
		resultado = {
			"metodo": "heuristico",
			"m2_paredes_estimado": m2_paredes,
			"ml_rodapies_estimado": ml_rodapies,
			"num_puertas_estimado": num_puertas,
			"confianza": "baja",
			"mensaje": "Estimación básica. Para mayor precisión, añade el número de habitaciones.",
		}
		
		logger.info(f"Estimaciones heurísticas: {resultado}")
		return resultado
	
	def calcular_total_con_iva(
		self,
		base_imponible: float,
		es_vivienda_habitual: bool = False,
	) -> dict:
		"""
		Calcula el total aplicando redondeo del 5% e IVA.
		
		Args:
			base_imponible: Base sin IVA ni redondeo
			es_vivienda_habitual: Flag para IVA (no usado en Fase 1)
			
		Returns:
			dict: Desglose completo de totales
		"""
		# Aplicar redondeo del 5%
		base_con_redondeo = round(base_imponible * 1.05, 2)
		importe_redondeo = round(base_con_redondeo - base_imponible, 2)
		
		# Calcular IVA sobre base con redondeo
		porcentaje_iva = self.settings.iva_general
		importe_iva = round(base_con_redondeo * (porcentaje_iva / 100), 2)
		
		# Total final
		total = round(base_con_redondeo + importe_iva, 2)
		
		return {
			'subtotal': base_imponible,
			'base_sin_redondeo': base_imponible,
			'base_con_redondeo': base_con_redondeo,
			'importe_redondeo': importe_redondeo,
			'redondeo_porcentaje': 5,
			'iva_porcentaje': porcentaje_iva,
			'iva_importe': importe_iva,
			'total': total,
		}
	
	def validar_presupuesto(self, presupuesto: Budget) -> dict:
		"""
		Valida que un presupuesto cumpla las reglas de negocio.
		
		Args:
			presupuesto: Presupuesto a validar
			
		Returns:
			dict: {
				'valido': bool,
				'errores': list[str],
				'advertencias': list[str]
			}
		"""
		errores = []
		advertencias = []
		
		# Validar que tenga partidas
		if not presupuesto.partidas:
			errores.append("El presupuesto no tiene partidas")
		
		# Validar totales mínimos
		if presupuesto.total < self.settings.presupuesto_minimo:
			advertencias.append(
				f"El presupuesto está por debajo del mínimo recomendado "
				f"({self.settings.presupuesto_minimo} €)"
			)
		
		# Validar que tenga cliente
		if not presupuesto.tiene_cliente:
			advertencias.append("El presupuesto no tiene datos de cliente")
		
		# Validar markup aplicado
		if hasattr(self.settings, 'markup_minimo'):
			# Calcular markup efectivo
			markup_efectivo = (
				(presupuesto.total / presupuesto.subtotal - 1) * 100
				if presupuesto.subtotal > 0 else 0
			)
			
			if markup_efectivo < self.settings.markup_minimo:
				advertencias.append(
					f"Markup efectivo ({markup_efectivo:.1f}%) está por debajo "
					f"del mínimo recomendado ({self.settings.markup_minimo}%)"
				)
		
		logger.info(
			f"Validación presupuesto: "
			f"{len(errores)} errores, {len(advertencias)} advertencias"
		)
		
		return {
			'valido': len(errores) == 0,
			'errores': errores,
			'advertencias': advertencias,
		}
	
	def calcular_totales_con_redondeo(self, presupuesto: Budget) -> dict:
		"""
		Calcula todos los totales aplicando el redondeo del 5%.
		
		Args:
			presupuesto: Presupuesto a calcular
			
		Returns:
			dict: Todos los totales calculados
		"""
		subtotal = presupuesto.subtotal
		descuento = presupuesto.importe_descuento
		base_sin_redondeo = presupuesto.base_imponible
		
		# Aplicar redondeo del 5%
		base_con_redondeo = round(base_sin_redondeo * 1.05, 2)
		importe_redondeo = round(base_con_redondeo - base_sin_redondeo, 2)
		
		# Calcular IVA sobre base con redondeo
		iva_data = self.calcular_iva(base_con_redondeo, presupuesto.proyecto)
		
		total = round(base_con_redondeo + iva_data['importe'], 2)
		
		return {
			'subtotal': subtotal,
			'descuento': descuento,
			'base_sin_redondeo': base_sin_redondeo,
			'base_con_redondeo': base_con_redondeo,
			'importe_redondeo': importe_redondeo,
			'redondeo_porcentaje': 5,
			'iva_porcentaje': iva_data['porcentaje'],
			'iva_importe': iva_data['importe'],
			'total': total,
		}
	
	def obtener_desglose_completo(self, presupuesto: Budget) -> dict:
		"""
		Obtiene desglose completo del presupuesto.
		
		Args:
			presupuesto: Presupuesto
			
		Returns:
			dict: Desglose completo
		"""
		return {
			"partidas": [
				{
					"codigo": p.codigo,
					"descripcion": p.descripcion,
					"cantidad": p.cantidad,
					"unidad": p.unidad,
					"precio_unitario": p.precio_unitario,
					"subtotal": p.subtotal,
					"categoria": p.categoria.value,
					"calidad": p.calidad.value,
					"es_paquete": p.es_paquete,
				}
				for p in presupuesto.partidas
			],
			"totales": self.calcular_totales_con_redondeo(presupuesto),
		}
	
	def obtener_info_partida(self, codigo_partida: str) -> Optional[dict]:
		"""
		Obtiene información completa de una partida.
		
		Args:
			codigo_partida: Código de la partida
			
		Returns:
			dict con info completa o None si no existe
		"""
		return self.pricing_data.get(codigo_partida)
	
	def listar_partidas_disponibles(self) -> list[dict]:
		"""
		Lista todas las partidas disponibles en el sistema.
		
		Returns:
			list[dict]: Lista de partidas con su info básica
		"""
		partidas = []
		for categoria, partidas_cat in self.pricing_data.items():
			for partida_key, data in partidas_cat.items():
				partidas.append({
					'codigo': partida_key,
					'nombre': partida_key.replace("_", " ").title(),
					'descripcion': data.get('descripcion', ''),
					'categoria': categoria,
					'unidad': data.get('unidad', ''),
				})
		return partidas


# ============================================================================
# FUNCIÓN FACTORY (SINGLETON)
# ============================================================================

_pricing_service: Optional[PricingService] = None


def get_pricing_service() -> PricingService:
	"""
	Obtiene la instancia singleton del servicio de pricing.
	
	Returns:
		PricingService: Instancia del servicio
	"""
	global _pricing_service
	
	if _pricing_service is None:
		_pricing_service = PricingService()
		logger.info("✅ PricingService inicializado")
	
	return _pricing_service