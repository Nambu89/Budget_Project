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
from .prompts import CALCULATOR_INSTRUCTIONS, build_estimaciones_prompt

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
			instructions=CALCULATOR_INSTRUCTIONS,
		)
		
		logger.info("✓ CalculatorAgent inicializado con Microsoft Agent Framework + Ajuste Geográfico")
	
	def calcular_presupuesto(
		self,
		datos_proyecto: dict,
		partidas: list[dict],
		paquetes: Optional[list] = None,
	) -> Budget:
		"""
		Calcula el presupuesto completo.

		Args:
			datos_proyecto: Datos validados del proyecto
			partidas: Lista de partidas a incluir
			paquetes: Lista de paquetes a incluir. Cada elemento puede ser
				un str (id del paquete) o un dict {id, cantidad, metros}

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
		# El frontend envía dicts {id, cantidad, metros}; también se admite str (id)
		if paquetes:
			for paquete in paquetes:
				if isinstance(paquete, dict):
					paquete_id = paquete.get("id")
					cantidad = int(paquete.get("cantidad") or 1)
					# Sin metros explícitos, BudgetService decide el fallback
					# según el tipo de paquete (m2 del proyecto o m2_referencia)
					metros_paquete = paquete.get("metros")
				else:
					paquete_id = paquete
					cantidad = 1
					metros_paquete = None

				if not paquete_id:
					logger.warning(f"Paquete sin id, ignorado: {paquete}")
					continue

				for _ in range(max(cantidad, 1)):
					self.budget_service.agregar_paquete(
						presupuesto=presupuesto,
						paquete=paquete_id,
						calidad=datos_proyecto.get("calidad"),
						metros=metros_paquete,
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
		if not proyecto.habitaciones:
			logger.info("Sin habitaciones, usando cálculo heurístico")
			return self.budget_service.pricing.calcular_estimaciones_heuristicas(proyecto)
		
		# Preparar información de ubicación
		ubicacion_info = proyecto.ubicacion if proyecto.ubicacion else "España (precio medio)"
		
		logger.info(
			f"Calculando estimaciones con Agent Framework para {proyecto.habitaciones} habitaciones "
			f"en {ubicacion_info}"
		)
		
		try:
			prompt = build_estimaciones_prompt(proyecto, ubicacion_info)

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