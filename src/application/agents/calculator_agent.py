"""
Calculator Agent - Agente calculador de precios.

Calcula los precios de las partidas y paquetes aplicando
todas las reglas de negocio (markup, redondeo, IVA).

MIGRADO A: Microsoft Agent Framework
PROMPT ENGINEERING: Chain-of-Thought + Few-Shot + Grounding Data + Ajuste Geográfico
"""

from typing import Optional
import asyncio
import json
import re
from loguru import logger

# Microsoft Agent Framework (reemplaza CrewAI)
from agent_framework import ChatAgent

from src.config.settings import settings
from src.infrastructure.llm import get_chat_client
from src.domain.enums import PropertyType, QualityLevel, WorkCategory
from src.domain.models import Budget, Project
from ..services import BudgetService, get_budget_service

class CalculatorAgent:
	"""
	Agente para cálculo de precios usando Microsoft Agent Framework.
	
	Responsibilities:
	- Calcular precios de partidas
	- Aplicar markup a partidas individuales
	- Calcular paquetes (sin markup)
	- Aplicar redondeo al alza
	- Calcular IVA según tipo de inmueble
	- Ajustar precios según ubicación geográfica
	- Sugerir optimizaciones
	- Calcular estimaciones inteligentes con LLM
	"""
	
	def __init__(self, budget_service: Optional[BudgetService] = None):
		"""
		Inicializa el agente calculador.
		
		Args:
			budget_service: Servicio de presupuestos (opcional)
		"""
		self.budget_service = budget_service or get_budget_service()
		
		# Crear cliente usando factory (OpenAI o Azure según config)
		chat_client = get_chat_client()
		
		# Crear agente con Microsoft Agent Framework
		self.agent = ChatAgent(
			name="Especialista en Cálculo de Presupuestos",
			chat_client=chat_client,
			instructions="""
			Soy un calculista experto con más de 15 años de experiencia
			en el sector de la construcción EN ESPAÑA. Conozco todos los precios
			del mercado español y aplico las reglas comerciales para
			ofrecer presupuestos competitivos pero rentables.
			
			CONOCIMIENTO GEOGRÁFICO DE ESPAÑA:
			Tengo experiencia trabajando en TODAS las provincias españolas y conozco
			las variaciones de precios por ubicación:
			
			ZONAS MUY CARAS (+30% a +50%):
			- Madrid capital y zona norte (Pozuelo, Las Rozas, Majadahonda)
			- Barcelona capital y zona alta (Sant Cugat, Sitges)
			- San Sebastián, Bilbao zona centro
			- Palma de Mallorca, Ibiza
			- Marbella, Puerto Banús
			
			ZONAS CARAS (+15% a +30%):
			- Valencia capital, Málaga capital
			- Alicante, San Sebastián periferia
			- Pamplona, Vitoria
			- Zaragoza centro, Sevilla centro
			- Costa del Sol (Fuengirola, Torremolinos)
			
			ZONAS PRECIO MEDIO (±0%):
			- Capitales de provincia medianas
			- Ciudades entre 50.000-200.000 habitantes
			- Murcia, Córdoba, Valladolid, Granada
			
			ZONAS ECONÓMICAS (-15% a -30%):
			- Provincias del interior (Soria, Teruel, Cuenca, Ávila)
			- Zonas rurales de Castilla-La Mancha
			- Interior de Extremadura, Andalucía rural
			- Galicia interior, Asturias rural
			
			ZONAS MUY ECONÓMICAS (-30% a -40%):
			- Pueblos pequeños (<10.000 habitantes)
			- Zonas despobladas ("España vaciada")
			
			AJUSTE AUTOMÁTICO:
			Cuando recibo una ubicación, ajusto AUTOMÁTICAMENTE todos mis cálculos
			de costes (materiales, mano de obra, transporte) según mi conocimiento
			del mercado en esa zona específica.
			
			Mi trabajo es calcular precios precisos aplicando:
			- Markup del 15% a partidas individuales (no a paquetes)
			- Redondeo al alza del 5% sobre el total
			- IVA del 21% para todos los inmuebles (general único)
			- Ajuste geográfico según ubicación del proyecto
			""",
		)
		
		logger.info("✓ CalculatorAgent inicializado con Microsoft Agent Framework + Ajuste Geográfico")
	
	def calcular_presupuesto(
		self,
		datos_proyecto: dict,
		partidas: list[dict],
		paquetes: list[str] = None,
	) -> Budget:
		"""
		Calcula el presupuesto completo.
		
		Args:
			datos_proyecto: Datos validados del proyecto
			partidas: Lista de partidas a incluir
			paquetes: Lista de paquetes a incluir
			
		Returns:
			Budget: Presupuesto calculado
		"""
		logger.info("Calculando presupuesto...")
		
		# Crear presupuesto base
		presupuesto = self.budget_service.crear_presupuesto(
			tipo_inmueble=datos_proyecto["tipo_inmueble"],
			metros_cuadrados=datos_proyecto["metros_cuadrados"],
			calidad=datos_proyecto.get("calidad", QualityLevel.ESTANDAR),
			estado_actual=datos_proyecto.get("estado_actual", "normal"),
			ubicacion=datos_proyecto.get("ubicacion"),
			descripcion=datos_proyecto.get("descripcion"),
			num_habitaciones=datos_proyecto.get("num_habitaciones"),
			estado_mobiliario=datos_proyecto.get("estado_mobiliario", "vacio"),
		)
		
		# Agregar partidas individuales (con markup)
		if partidas:
			self.budget_service.agregar_partidas_multiples(presupuesto, partidas)
		
		# Agregar paquetes (sin markup)
		if paquetes:
			for paquete in paquetes:
				self.budget_service.agregar_paquete(
					presupuesto=presupuesto,
					paquete=paquete,
					calidad=datos_proyecto.get("calidad"),
					metros=datos_proyecto["metros_cuadrados"],
				)
		
		logger.info(
			f"Presupuesto calculado: {presupuesto.num_partidas} partidas, "
			f"subtotal: {presupuesto.subtotal}€"
		)
		
		return presupuesto
	
	async def calcular_estimaciones_inteligentes(self, proyecto: Project) -> dict:
		"""
		Calcula estimaciones inteligentes usando Microsoft Agent Framework.
		
		Utiliza técnicas avanzadas de prompt engineering:
		- Chain-of-Thought (CoT) para razonamiento paso a paso
		- Few-Shot learning con ejemplo concreto
		- Grounding data con contexto estructurado
		- Restricciones numéricas precisas
		- Ajuste geográfico automático según ubicación
		
		Args:
			proyecto: Datos del proyecto
			
		Returns:
			dict: Estimaciones calculadas con alta precisión
		"""
		if not proyecto.num_habitaciones:
			logger.info("Sin num_habitaciones, usando cálculo heurístico")
			return self.budget_service.pricing.calcular_estimaciones_heuristicas(proyecto)
		
		# Preparar información de ubicación
		ubicacion_info = proyecto.ubicacion if proyecto.ubicacion else "España (precio medio)"
		
		logger.info(
			f"Calculando estimaciones con Agent Framework para {proyecto.num_habitaciones} habitaciones "
			f"en {ubicacion_info}"
		)
		
		try:
			prompt = f"""Eres un calculista experto en construcción española con 15+ años de experiencia en mediciones arquitectónicas.

**CONTEXTO DEL PROYECTO:**
Tipo de inmueble: {proyecto.tipo_inmueble_nombre}
Superficie total construida: {proyecto.metros_cuadrados} m²
Número de habitaciones/espacios: {proyecto.num_habitaciones}
Estado actual: {proyecto.estado_actual}
📍 UBICACIÓN: {ubicacion_info}

**CONSIDERACIONES CRÍTICAS DE UBICACIÓN:**
La ubicación "{ubicacion_info}" es FUNDAMENTAL para los cálculos.
Debes ajustar TODOS los precios y estimaciones según tu conocimiento del mercado español:

- Si es Madrid, Barcelona, San Sebastián, o zona cara → Los costes de materiales, mano de obra 
  y transporte serán significativamente más altos (+30-50%)
  
- Si es una capital de provincia o ciudad media → Usa precios estándar españoles (base)

- Si es zona rural, pueblo pequeño, o interior → Los costes serán notablemente más bajos (-20-40%)
  debido a menor coste de vida y mano de obra más económica

**IMPACTO EN LOS CÁLCULOS:**
- m² de paredes: La mano de obra varía según zona
- ml de rodapiés: El material y su instalación varían según zona
- Número de puertas: El precio de carpintería varía según zona

NO ignores la ubicación. Es tan importante como los m² o el número de habitaciones.

**TU TAREA:**
Calcula con precisión las siguientes mediciones siguiendo el estándar español de construcción:

**METODOLOGÍA PASO A PASO:**

1. **DISTRIBUCIÓN DE ESPACIOS:**
   - Analiza la superficie total ({proyecto.metros_cuadrados} m²)
   - Distribuye en espacios típicos españoles según número de habitaciones ({proyecto.num_habitaciones})
   - Considera: dormitorios, salón-comedor, cocina, baños, pasillos, distribuidor
   - Asigna m² realistas a cada espacio según distribución típica de {proyecto.tipo_inmueble_nombre}

2. **CÁLCULO DE PAREDES (m²):**
   - Para cada espacio: perímetro = 2 × (ancho + largo)
   - Altura estándar española: 2.50 metros
   - m² paredes de cada espacio = perímetro × 2.50m
   - SUMA TOTAL de todos los espacios
   - Incluye: paredes interiores, medianeras, fachadas

3. **CÁLCULO DE RODAPIÉS (ml):**
   - Rodapiés = perímetro de CADA habitación
   - Resta los anchos de puertas (0.80m cada una)
   - SUMA TOTAL de todos los espacios

4. **NÚMERO DE PUERTAS:**
   - Cuenta SOLO puertas de paso entre habitaciones
   - NO incluyas: puertas de armario, ventanas, accesos exteriores
   - Típico: 1 puerta por dormitorio + baño + cocina + salón + extras

**RESTRICCIONES CRÍTICAS:**
- Altura de techo: exactamente 2.50m (estándar español)
- Ancho estándar puerta: 0.80m
- Considera distribuciones típicas españolas, no americanas
- Los m² de todos los espacios deben sumar aproximadamente {proyecto.metros_cuadrados} m²
- Sé conservador: mejor estimar de menos que de más
- APLICA tu conocimiento de precios en {ubicacion_info}

**FORMATO DE SALIDA OBLIGATORIO:**
Responde EXCLUSIVAMENTE con un JSON válido (sin ```json, sin markdown, sin explicaciones adicionales):

{{
	"m2_paredes_estimado": <float con 1 decimal>,
	"ml_rodapies_estimado": <float con 1 decimal>,
	"num_puertas_estimado": <int>,
	"distribucion_espacios": [
		{{"tipo": "dormitorio", "cantidad": <int>, "m2_promedio": <float>}},
		{{"tipo": "salon", "cantidad": <int>, "m2_promedio": <float>}},
		{{"tipo": "cocina", "cantidad": <int>, "m2_promedio": <float>}},
		{{"tipo": "bano", "cantidad": <int>, "m2_promedio": <float>}},
		{{"tipo": "pasillo", "cantidad": <int>, "m2_promedio": <float>}}
	],
	"razonamiento": "<Explica en 2-3 frases los cálculos clave realizados y menciona si has aplicado ajuste por ubicación>"
}}

**EJEMPLO DE RAZONAMIENTO ESPERADO:**
"Para 80m² con 2 habitaciones en {ubicacion_info}: 2 dormitorios (12m² c/u), salón (22m²), cocina (8m²), baño (5m²), pasillo (9m²). Perímetro total ~74ml → 74ml × 2.5m = 185m² paredes. Rodapiés: 74ml - (5 puertas × 0.8m) = 70ml. Total 5 puertas de paso. Costes ajustados según ubicación."

CRÍTICO: Responde SOLO con el JSON. Nada antes, nada después. Sin explicaciones adicionales."""

			# Ejecutar agente de forma asíncrona
			result = await self.agent.run(prompt)
			
			# Extraer respuesta
			response_text = result.text if result else ""
			
			# Limpiar respuesta (eliminar markdown si existe)
			response_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
			
			# Parsear JSON
			try:
				estimaciones = json.loads(response_text)
				estimaciones["metodo"] = "ia"
				estimaciones["confianza"] = "alta"
				estimaciones["ubicacion"] = ubicacion_info
				
				logger.info(f"✓ Estimaciones IA para {ubicacion_info}: {estimaciones['m2_paredes_estimado']:.1f}m² paredes, "
						   f"{estimaciones['ml_rodapies_estimado']:.1f}ml rodapiés, "
						   f"{estimaciones['num_puertas_estimado']} puertas")
				
				return estimaciones
				
			except json.JSONDecodeError as je:
				logger.error(f"Error parseando JSON: {je}")
				logger.error(f"Respuesta recibida: {response_text[:500]}")
				logger.warning("Fallback a cálculo heurístico")
				return self.budget_service.pricing.calcular_estimaciones_heuristicas(proyecto)
			
		except Exception as e:
			logger.error(f"Error en cálculo con Agent Framework: {e}")
			logger.warning("Fallback a cálculo heurístico")
			return self.budget_service.pricing.calcular_estimaciones_heuristicas(proyecto)
	
	def obtener_desglose_completo(self, presupuesto: Budget) -> dict:
		"""Obtiene desglose completo del presupuesto."""
		return self.budget_service.obtener_desglose(presupuesto)
	
	def sugerir_optimizaciones(self, presupuesto: Budget) -> list:
		"""Sugiere optimizaciones del presupuesto."""
		return self.budget_service.sugerir_optimizaciones(presupuesto)
	
	def calcular_con_comparativa(
		self,
		datos_proyecto: dict,
		partidas: list[dict],
		paquete_alternativo: str,
	) -> dict:
		"""Calcula comparativa entre partidas y paquete."""
		return self.budget_service.calcular_comparativa(
			datos_proyecto, partidas, paquete_alternativo
		)