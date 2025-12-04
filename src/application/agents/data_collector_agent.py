"""
Data Collector Agent - Agente recolector de datos.

Procesa y valida los datos del formulario del usuario,
estructurándolos para el resto del sistema.

MIGRADO A: Microsoft Agent Framework (sin CrewAI)
"""

from typing import Optional, Any
from agent_framework import ChatAgent
from agent_framework.azure import AzureOpenAIChatClient
from loguru import logger

from ...config.settings import settings
from src.domain.enums import PropertyType, QualityLevel, WorkCategory


def get_azure_chat_client() -> AzureOpenAIChatClient:
	"""Crea cliente Azure OpenAI para Agent Framework."""
	return AzureOpenAIChatClient(
		deployment_name=settings.azure_openai_deployment_name,
		api_key=settings.azure_openai_api_key,
		endpoint=settings.azure_openai_endpoint,
		api_version=settings.azure_openai_api_version,
	)


# System prompt del agente
DATA_COLLECTOR_SYSTEM_PROMPT = """
Eres un asistente experto en reformas y obras en España. Tu trabajo es:

1. VALIDAR que los datos proporcionados por el usuario sean correctos y coherentes
2. ESTRUCTURAR la información de forma clara para el siguiente paso
3. DETECTAR inconsistencias o datos faltantes
4. SUGERIR mejoras o aclaraciones si es necesario

Reglas:
- Los metros cuadrados deben ser razonables (1-10000 m²)
- El tipo de inmueble debe ser: piso, vivienda, oficina o local
- La calidad debe ser: basico, estandar o premium
- Las partidas deben corresponder a categorías válidas
- Todos los inmuebles aplican IVA general del 21%

Si detectas algún problema, indícalo claramente.
Si todo está correcto, confirma los datos estructurados.

Responde siempre en español y de forma profesional pero cercana.
"""


class DataCollectorAgent:
	"""
	Agente para recolección y validación de datos.
	
	Procesa los inputs del usuario desde el formulario
	y los estructura para su uso en el sistema.
	
	Responsibilities:
	- Validar datos de entrada
	- Estructurar información del proyecto
	- Detectar inconsistencias
	- Preparar datos para el CalculatorAgent
	"""
	
	def __init__(self):
		"""Inicializa el agente recolector."""
		# Crear agente con Microsoft Agent Framework
		chat_client = get_azure_chat_client()
		self.agent = ChatAgent(
			name="Especialista en Recolección de Datos",
			chat_client=chat_client,
			instructions="""
			Soy un experto en reformas con años de experiencia ayudando
			a clientes a definir sus proyectos. Mi trabajo es asegurarme
			de que toda la información esté completa y sea coherente
			antes de calcular el presupuesto.
			"""
		)
		
		logger.info("✓ DataCollectorAgent inicializado (Microsoft Agent Framework)")
	
	def validar_tipo_inmueble(self, tipo: str) -> tuple[bool, Optional[PropertyType], str]:
		"""
		Valida el tipo de inmueble.
		
		Args:
			tipo: Tipo de inmueble como string
			
		Returns:
			tuple: (es_valido, PropertyType o None, mensaje)
		"""
		tipo_lower = tipo.lower().strip()
		
		mapeo = {
			"piso": PropertyType.PISO,
			"vivienda": PropertyType.VIVIENDA,
			"vivienda independiente": PropertyType.VIVIENDA,
			"casa": PropertyType.VIVIENDA,
			"chalet": PropertyType.VIVIENDA,
			"adosado": PropertyType.VIVIENDA,
			"oficina": PropertyType.OFICINA,
			"despacho": PropertyType.OFICINA,
			"local": PropertyType.LOCAL,
			"local comercial": PropertyType.LOCAL,
			"comercio": PropertyType.LOCAL,
		}
		
		if tipo_lower in mapeo:
			return True, mapeo[tipo_lower], f"Tipo de inmueble válido: {mapeo[tipo_lower].value}"
		
		return False, None, f"Tipo de inmueble no reconocido: '{tipo}'. Usa: piso, vivienda, oficina o local"
	
	def validar_metros(self, metros: Any) -> tuple[bool, Optional[float], str]:
		"""
		Valida los metros cuadrados.
		
		Args:
			metros: Metros cuadrados (puede venir como string o número)
			
		Returns:
			tuple: (es_valido, metros como float o None, mensaje)
		"""
		try:
			metros_float = float(metros)
			
			if metros_float <= 0:
				return False, None, "Los metros cuadrados deben ser positivos"
			
			if metros_float > 10000:
				return False, None, "Los metros cuadrados parecen excesivos (máximo 10,000 m²)"
			
			if metros_float < 5:
				return False, None, "Los metros cuadrados son muy pequeños (mínimo 5 m²)"
			
			return True, metros_float, f"Metros cuadrados válidos: {metros_float} m²"
			
		except (ValueError, TypeError):
			return False, None, f"'{metros}' no es un número válido de metros cuadrados"
	
	def validar_calidad(self, calidad: str) -> tuple[bool, Optional[QualityLevel], str]:
		"""
		Valida el nivel de calidad.
		
		Args:
			calidad: Nivel de calidad como string
			
		Returns:
			tuple: (es_valido, QualityLevel o None, mensaje)
		"""
		calidad_lower = calidad.lower().strip()
		
		mapeo = {
			"basico": QualityLevel.BASICO,
			"básico": QualityLevel.BASICO,
			"economico": QualityLevel.BASICO,
			"económico": QualityLevel.BASICO,
			"estandar": QualityLevel.ESTANDAR,
			"estándar": QualityLevel.ESTANDAR,
			"normal": QualityLevel.ESTANDAR,
			"medio": QualityLevel.ESTANDAR,
			"premium": QualityLevel.PREMIUM,
			"alta": QualityLevel.PREMIUM,
			"lujo": QualityLevel.PREMIUM,
			"alto": QualityLevel.PREMIUM,
		}
		
		if calidad_lower in mapeo:
			return True, mapeo[calidad_lower], f"Calidad válida: {mapeo[calidad_lower].value}"
		
		return False, None, f"Calidad no reconocida: '{calidad}'. Usa: basico, estandar o premium"
	
	def validar_categoria(self, categoria: str) -> tuple[bool, Optional[WorkCategory], str]:
		"""
		Valida una categoría de trabajo.
		
		Args:
			categoria: Categoría como string
			
		Returns:
			tuple: (es_valido, WorkCategory o None, mensaje)
		"""
		categoria_lower = categoria.lower().strip()
		
		mapeo = {
			"albanileria": WorkCategory.ALBANILERIA,
			"albañileria": WorkCategory.ALBANILERIA,
			"albañilería": WorkCategory.ALBANILERIA,
			"fontaneria": WorkCategory.FONTANERIA,
			"fontanería": WorkCategory.FONTANERIA,
			"electricidad": WorkCategory.ELECTRICIDAD,
			"electrico": WorkCategory.ELECTRICIDAD,
			"eléctrico": WorkCategory.ELECTRICIDAD,
			"carpinteria": WorkCategory.CARPINTERIA,
			"carpintería": WorkCategory.CARPINTERIA,
			"cocina": WorkCategory.COCINA,
		}
		
		if categoria_lower in mapeo:
			return True, mapeo[categoria_lower], f"Categoría válida: {mapeo[categoria_lower].value}"
		
		return False, None, f"Categoría no reconocida: '{categoria}'"
	
	def procesar_formulario(self, datos: dict) -> dict:
		"""
		Procesa y valida todos los datos del formulario.
		
		Args:
			datos: Diccionario con los datos del formulario
			
		Returns:
			dict: Resultado del procesamiento con datos validados o errores
		"""
		resultado = {
			"exito": True,
			"proyecto": {},
			"partidas": [],
			"paquetes": [],
			"errores": [],
			"warnings": [],
		}
		
		# Validar tipo de inmueble (requerido)
		if "tipo_inmueble" in datos:
			valido, tipo, msg = self.validar_tipo_inmueble(datos["tipo_inmueble"])
			if valido:
				resultado["proyecto"]["tipo_inmueble"] = tipo
			else:
				resultado["exito"] = False
				resultado["errores"].append(msg)
		else:
			resultado["exito"] = False
			resultado["errores"].append("Falta el tipo de inmueble")
		
		# Validar metros cuadrados (requerido)
		if "metros_cuadrados" in datos:
			valido, metros, msg = self.validar_metros(datos["metros_cuadrados"])
			if valido:
				resultado["proyecto"]["metros_cuadrados"] = metros
			else:
				resultado["exito"] = False
				resultado["errores"].append(msg)
		else:
			resultado["exito"] = False
			resultado["errores"].append("Faltan los metros cuadrados")
		
		# Validar calidad (opcional, default: estandar)
		if "calidad" in datos:
			valido, calidad, msg = self.validar_calidad(datos["calidad"])
			if valido:
				resultado["proyecto"]["calidad"] = calidad
			else:
				resultado["warnings"].append(msg)
				resultado["proyecto"]["calidad"] = QualityLevel.ESTANDAR
		else:
			resultado["proyecto"]["calidad"] = QualityLevel.ESTANDAR
		
		# Procesar estado actual (opcional)
		if "estado_actual" in datos:
			resultado["proyecto"]["estado_actual"] = datos["estado_actual"]
		
		# Procesar descripción (opcional)
		if "descripcion" in datos:
			resultado["proyecto"]["descripcion"] = datos["descripcion"]
		
		# Procesar ubicación (opcional)
		if "ubicacion" in datos:
			resultado["proyecto"]["ubicacion"] = datos["ubicacion"]
		
		# Procesar partidas seleccionadas
		if "partidas" in datos:
			for partida in datos["partidas"]:
				if isinstance(partida, dict):
					partida_proc = {
						"categoria": partida.get("categoria"),
						"partida": partida.get("partida") or partida.get("nombre"),
						"cantidad": partida.get("cantidad", 1),
					}
					
					# Validar categoría si está presente
					if partida_proc["categoria"]:
						valido, cat, _ = self.validar_categoria(partida_proc["categoria"])
						if valido:
							partida_proc["categoria"] = cat
					
					resultado["partidas"].append(partida_proc)
		
		# Procesar paquetes seleccionados
		if "paquetes" in datos:
			resultado["paquetes"] = datos["paquetes"]
		
		return resultado
	
	def generar_resumen(self, resultado: dict) -> str:
		"""
		Genera un resumen legible de los datos procesados.
		
		Args:
			resultado: Resultado del procesamiento (con 'proyecto' y 'partidas')
			
		Returns:
			str: Resumen en texto
		"""
		lineas = ["📋 Resumen del Proyecto:", ""]
		
		proyecto = resultado.get("proyecto", {})
		
		if "tipo_inmueble" in proyecto:
			lineas.append(f"🏠 Tipo: {proyecto['tipo_inmueble'].value.title()}")
		
		if "metros_cuadrados" in proyecto:
			lineas.append(f"📐 Metros: {proyecto['metros_cuadrados']} m²")
		
		if "calidad" in proyecto:
			lineas.append(f"⭐ Calidad: {proyecto['calidad'].value.title()}")
		
		lineas.append("💶 IVA: 21%")
		
		if "ubicacion" in proyecto:
			lineas.append(f"📍 Ubicación: {proyecto['ubicacion']}")
		
		partidas = resultado.get("partidas", [])
		if partidas:
			lineas.append(f"")
			lineas.append(f"📝 Partidas seleccionadas: {len(partidas)}")
		
		paquetes = resultado.get("paquetes", [])
		if paquetes:
			lineas.append(f"📦 Paquetes seleccionados: {', '.join(paquetes)}")
		
		return "\n".join(lineas)