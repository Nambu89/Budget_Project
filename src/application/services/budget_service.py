"""
Servicio principal de presupuestos.

Orquesta la creación completa de presupuestos,
coordinando el pricing service, los modelos y la generación de PDF.
"""

from typing import Optional
from datetime import datetime
from loguru import logger

from ...config.settings import settings
from ...domain.enums import PropertyType, QualityLevel, WorkCategory
from ...domain.models import Budget, BudgetItem, Project, Customer
from ...infrastructure.pdf import generar_pdf_presupuesto
from .pricing_service import PricingService, get_pricing_service


class BudgetService:
    """
    Servicio principal para gestión de presupuestos.
    
    Coordina:
    - Creación de presupuestos
    - Agregación de partidas y paquetes
    - Aplicación de reglas de negocio
    - Generación de PDF
    """
    
    def __init__(self, pricing_service: Optional[PricingService] = None):
        """
        Inicializa el servicio de presupuestos.
        
        Args:
            pricing_service: Servicio de precios (opcional, usa singleton)
        """
        self.pricing = pricing_service or get_pricing_service()
        logger.info("✓ BudgetService inicializado")
    
    # ==========================================
    # Creación de presupuestos
    # ==========================================
    
    def crear_presupuesto(
        self,
        tipo_inmueble: PropertyType,
        metros_cuadrados: float,
        calidad: QualityLevel = QualityLevel.ESTANDAR,
        es_vivienda_habitual: bool = False,
        estado_actual: str = "normal",
        ubicacion: Optional[str] = None,
        descripcion: Optional[str] = None,
    ) -> Budget:
        """
        Crea un nuevo presupuesto vacío.
        
        Args:
            tipo_inmueble: Tipo de propiedad
            metros_cuadrados: Superficie en m²
            calidad: Nivel de calidad por defecto
            es_vivienda_habitual: Si aplica IVA reducido
            estado_actual: Estado del inmueble
            ubicacion: Ciudad/zona
            descripcion: Descripción adicional
            
        Returns:
            Budget: Presupuesto creado (sin partidas)
        """
        proyecto = Project(
            tipo_inmueble=tipo_inmueble,
            metros_cuadrados=metros_cuadrados,
            calidad_general=calidad,
            es_vivienda_habitual=es_vivienda_habitual,
            estado_actual=estado_actual,
            ubicacion=ubicacion,
            descripcion=descripcion,
        )
        
        presupuesto = Budget(
            proyecto=proyecto,
            dias_validez=settings.validez_presupuesto_dias,
        )
        
        logger.info(f"Presupuesto creado: {presupuesto.numero_presupuesto}")
        return presupuesto
    
    def crear_presupuesto_rapido(
        self,
        tipo_inmueble: PropertyType,
        metros_cuadrados: float,
        paquete: str,
        calidad: QualityLevel = QualityLevel.ESTANDAR,
        es_vivienda_habitual: bool = False,
    ) -> Budget:
        """
        Crea un presupuesto rápido con un paquete predefinido.
        
        Args:
            tipo_inmueble: Tipo de propiedad
            metros_cuadrados: Superficie en m²
            paquete: Nombre del paquete a aplicar
            calidad: Nivel de calidad
            es_vivienda_habitual: Si aplica IVA reducido
            
        Returns:
            Budget: Presupuesto con paquete incluido
        """
        presupuesto = self.crear_presupuesto(
            tipo_inmueble=tipo_inmueble,
            metros_cuadrados=metros_cuadrados,
            calidad=calidad,
            es_vivienda_habitual=es_vivienda_habitual,
        )
        
        # Agregar paquete
        self.agregar_paquete(presupuesto, paquete, calidad, metros_cuadrados)
        
        return presupuesto
    
    # ==========================================
    # Gestión de partidas
    # ==========================================
    
    def agregar_partida(
        self,
        presupuesto: Budget,
        categoria: WorkCategory,
        partida: str,
        cantidad: float,
        calidad: Optional[QualityLevel] = None,
    ) -> bool:
        """
        Agrega una partida individual al presupuesto.
        
        Aplica automáticamente el markup de partida individual.
        
        Args:
            presupuesto: Presupuesto destino
            categoria: Categoría de trabajo
            partida: Nombre de la partida
            cantidad: Cantidad (m2, uds, etc.)
            calidad: Nivel de calidad (usa el del proyecto si no se especifica)
            
        Returns:
            bool: True si se agregó correctamente
        """
        calidad_usar = calidad or presupuesto.proyecto.calidad_general
        
        budget_item = self.pricing.crear_partida(
            categoria=categoria,
            partida=partida,
            cantidad=cantidad,
            calidad=calidad_usar,
            aplicar_markup=True,  # Partidas individuales tienen markup
        )
        
        if budget_item:
            presupuesto.agregar_partida(budget_item)
            logger.debug(f"Partida agregada: {partida} x {cantidad}")
            return True
        
        return False
    
    def agregar_partidas_multiples(
        self,
        presupuesto: Budget,
        partidas: list[dict],
    ) -> int:
        """
        Agrega múltiples partidas de una vez.
        
        Args:
            presupuesto: Presupuesto destino
            partidas: Lista de dicts con {categoria, partida, cantidad, calidad?}
            
        Returns:
            int: Número de partidas agregadas correctamente
        """
        agregadas = 0
        
        for p in partidas:
            categoria = p.get("categoria")
            if isinstance(categoria, str):
                categoria = WorkCategory(categoria)
            
            calidad = p.get("calidad")
            if isinstance(calidad, str):
                calidad = QualityLevel(calidad)
            
            exito = self.agregar_partida(
                presupuesto=presupuesto,
                categoria=categoria,
                partida=p["partida"],
                cantidad=p["cantidad"],
                calidad=calidad,
            )
            
            if exito:
                agregadas += 1
        
        logger.info(f"Agregadas {agregadas}/{len(partidas)} partidas")
        return agregadas
    
    def agregar_paquete(
        self,
        presupuesto: Budget,
        paquete: str,
        calidad: Optional[QualityLevel] = None,
        metros: Optional[float] = None,
    ) -> bool:
        """
        Agrega un paquete completo al presupuesto.
        
        Los paquetes NO tienen markup (incentivo comercial).
        
        Args:
            presupuesto: Presupuesto destino
            paquete: Nombre del paquete
            calidad: Nivel de calidad
            metros: Metros cuadrados (para reformas integrales)
            
        Returns:
            bool: True si se agregó correctamente
        """
        calidad_usar = calidad or presupuesto.proyecto.calidad_general
        metros_usar = metros or presupuesto.proyecto.metros_cuadrados
        
        partidas = self.pricing.crear_partidas_paquete(
            paquete=paquete,
            calidad=calidad_usar,
            metros=metros_usar,
        )
        
        if partidas:
            presupuesto.agregar_partidas(partidas)
            logger.info(f"Paquete agregado: {paquete}")
            return True
        
        return False
    
    def eliminar_partida(
        self,
        presupuesto: Budget,
        indice: int,
    ) -> bool:
        """
        Elimina una partida del presupuesto.
        
        Args:
            presupuesto: Presupuesto
            indice: Índice de la partida a eliminar
            
        Returns:
            bool: True si se eliminó
        """
        eliminada = presupuesto.eliminar_partida(indice)
        if eliminada:
            logger.debug(f"Partida eliminada: {eliminada.descripcion}")
            return True
        return False
    
    def limpiar_partidas(self, presupuesto: Budget) -> None:
        """Elimina todas las partidas del presupuesto."""
        presupuesto.limpiar_partidas()
        logger.info("Todas las partidas eliminadas")
    
    # ==========================================
    # Gestión de cliente
    # ==========================================
    
    def asignar_cliente(
        self,
        presupuesto: Budget,
        nombre: str,
        email: str,
        telefono: str,
        direccion_obra: Optional[str] = None,
        es_vivienda_habitual: Optional[bool] = None,
        logo_path: Optional[str] = None,
        notas: Optional[str] = None,
    ) -> Customer:
        """
        Asigna datos del cliente al presupuesto.
        
        Args:
            presupuesto: Presupuesto
            nombre: Nombre del cliente
            email: Email
            telefono: Teléfono
            direccion_obra: Dirección de la obra
            es_vivienda_habitual: Override del flag de vivienda habitual
            logo_path: Ruta al logo del cliente
            notas: Notas adicionales
            
        Returns:
            Customer: Cliente creado
        """
        # Si se especifica es_vivienda_habitual, actualizar también el proyecto
        if es_vivienda_habitual is not None:
            presupuesto.proyecto.es_vivienda_habitual = es_vivienda_habitual
        
        cliente = Customer(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion_obra=direccion_obra,
            es_vivienda_habitual=presupuesto.proyecto.es_vivienda_habitual,
            logo_path=logo_path,
            notas=notas,
        )
        
        presupuesto.cliente = cliente
        logger.info(f"Cliente asignado: {cliente.nombre}")
        
        return cliente
    
    # ==========================================
    # Cálculos y totales
    # ==========================================
    
    def calcular_totales(self, presupuesto: Budget) -> dict:
        """
        Calcula todos los totales del presupuesto.
        
        Aplica redondeo al alza y calcula IVA.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            dict: Desglose completo de totales
        """
        return self.pricing.calcular_total_con_iva(
            base_imponible=presupuesto.subtotal,
            es_vivienda_habitual=presupuesto.proyecto.puede_iva_reducido,
        )
    
    def obtener_total_con_redondeo(self, presupuesto: Budget) -> float:
        """
        Obtiene el total final con redondeo al alza aplicado.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            float: Total final
        """
        totales = self.calcular_totales(presupuesto)
        return totales["total"]
    
    def aplicar_descuento(
        self,
        presupuesto: Budget,
        porcentaje: float,
    ) -> None:
        """
        Aplica un descuento al presupuesto.
        
        Args:
            presupuesto: Presupuesto
            porcentaje: Porcentaje de descuento (0-100)
        """
        presupuesto.descuento_porcentaje = min(max(porcentaje, 0), 100)
        logger.info(f"Descuento aplicado: {presupuesto.descuento_porcentaje}%")
    
    # ==========================================
    # Comparativas
    # ==========================================
    
    def comparar_con_paquete(
        self,
        presupuesto: Budget,
        paquete: str,
    ) -> dict:
        """
        Compara el precio actual del presupuesto con un paquete equivalente.
        
        Args:
            presupuesto: Presupuesto actual
            paquete: Paquete a comparar
            
        Returns:
            dict: Comparativa con ahorro potencial
        """
        precio_actual = presupuesto.subtotal
        precio_paquete = self.pricing.obtener_precio_paquete(
            paquete=paquete,
            calidad=presupuesto.proyecto.calidad_general,
            metros=presupuesto.proyecto.metros_cuadrados,
        )
        
        ahorro = precio_actual - precio_paquete
        
        return {
            "precio_actual": precio_actual,
            "precio_paquete": precio_paquete,
            "ahorro": ahorro,
            "ahorro_porcentaje": round(ahorro / precio_actual * 100, 1) if precio_actual > 0 else 0,
            "recomendacion": "paquete" if ahorro > 0 else "mantener_actual",
        }
    
    # ==========================================
    # Generación de documentos
    # ==========================================
    
    def generar_pdf(
        self,
        presupuesto: Budget,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Genera el PDF del presupuesto.
        
        Args:
            presupuesto: Presupuesto
            output_path: Ruta de salida (opcional)
            
        Returns:
            bytes: Contenido del PDF
        """
        logo_path = None
        if presupuesto.cliente and presupuesto.cliente.logo_path:
            logo_path = presupuesto.cliente.logo_path
        
        pdf_bytes = generar_pdf_presupuesto(
            budget=presupuesto,
            logo_path=logo_path,
            output_path=output_path,
        )
        
        logger.info(f"PDF generado: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    def generar_resumen_texto(self, presupuesto: Budget) -> str:
        """
        Genera un resumen en texto del presupuesto.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            str: Resumen legible
        """
        return presupuesto.resumen_texto()
    
    # ==========================================
    # Utilidades
    # ==========================================
    
    def validar_presupuesto(self, presupuesto: Budget) -> dict:
        """
        Valida que el presupuesto esté completo.
        
        Args:
            presupuesto: Presupuesto a validar
            
        Returns:
            dict: Resultado de validación con errores/warnings
        """
        errores = []
        warnings = []
        
        # Validar proyecto
        if presupuesto.proyecto.metros_cuadrados <= 0:
            errores.append("Los metros cuadrados deben ser mayores a 0")
        
        # Validar partidas
        if not presupuesto.partidas:
            warnings.append("El presupuesto no tiene partidas")
        
        # Validar cliente (warning, no error)
        if not presupuesto.tiene_cliente:
            warnings.append("No se han asignado datos del cliente")
        
        # Validar totales
        if presupuesto.subtotal <= 0:
            warnings.append("El subtotal es 0")
        
        return {
            "valido": len(errores) == 0,
            "errores": errores,
            "warnings": warnings,
            "completo": len(errores) == 0 and len(warnings) == 0,
        }
    
    def duplicar_presupuesto(self, presupuesto: Budget) -> Budget:
        """
        Crea una copia del presupuesto con nuevo ID y fecha.
        
        Args:
            presupuesto: Presupuesto original
            
        Returns:
            Budget: Copia del presupuesto
        """
        nuevo = presupuesto.model_copy(deep=True)
        cliente = Customer(
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion_obra=direccion_obra,
            es_vivienda_habitual=presupuesto.proyecto.es_vivienda_habitual,
            logo_path=logo_path,
            notas=notas,
        )
        
        presupuesto.cliente = cliente
        logger.info(f"Cliente asignado: {cliente.nombre}")
        
        return cliente
    
    # ==========================================
    # Cálculos y totales
    # ==========================================
    
    def calcular_totales(self, presupuesto: Budget) -> dict:
        """
        Calcula todos los totales del presupuesto.
        
        Aplica redondeo al alza y calcula IVA.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            dict: Desglose completo de totales
        """
        return self.pricing.calcular_total_con_iva(
            base_imponible=presupuesto.subtotal,
            es_vivienda_habitual=presupuesto.proyecto.puede_iva_reducido,
        )
    
    def obtener_total_con_redondeo(self, presupuesto: Budget) -> float:
        """
        Obtiene el total final con redondeo al alza aplicado.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            float: Total final
        """
        totales = self.calcular_totales(presupuesto)
        return totales["total"]
    
    def aplicar_descuento(
        self,
        presupuesto: Budget,
        porcentaje: float,
    ) -> None:
        """
        Aplica un descuento al presupuesto.
        
        Args:
            presupuesto: Presupuesto
            porcentaje: Porcentaje de descuento (0-100)
        """
        presupuesto.descuento_porcentaje = min(max(porcentaje, 0), 100)
        logger.info(f"Descuento aplicado: {presupuesto.descuento_porcentaje}%")
    
    # ==========================================
    # Comparativas
    # ==========================================
    
    def comparar_con_paquete(
        self,
        presupuesto: Budget,
        paquete: str,
    ) -> dict:
        """
        Compara el precio actual del presupuesto con un paquete equivalente.
        
        Args:
            presupuesto: Presupuesto actual
            paquete: Paquete a comparar
            
        Returns:
            dict: Comparativa con ahorro potencial
        """
        precio_actual = presupuesto.subtotal
        precio_paquete = self.pricing.obtener_precio_paquete(
            paquete=paquete,
            calidad=presupuesto.proyecto.calidad_general,
            metros=presupuesto.proyecto.metros_cuadrados,
        )
        
        ahorro = precio_actual - precio_paquete
        
        return {
            "precio_actual": precio_actual,
            "precio_paquete": precio_paquete,
            "ahorro": ahorro,
            "ahorro_porcentaje": round(ahorro / precio_actual * 100, 1) if precio_actual > 0 else 0,
            "recomendacion": "paquete" if ahorro > 0 else "mantener_actual",
        }
    
    # ==========================================
    # Generación de documentos
    # ==========================================
    
    def generar_pdf(
        self,
        presupuesto: Budget,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Genera el PDF del presupuesto.
        
        Args:
            presupuesto: Presupuesto
            output_path: Ruta de salida (opcional)
            
        Returns:
            bytes: Contenido del PDF
        """
        logo_path = None
        if presupuesto.cliente and presupuesto.cliente.logo_path:
            logo_path = presupuesto.cliente.logo_path
        
        pdf_bytes = generar_pdf_presupuesto(
            budget=presupuesto,
            logo_path=logo_path,
            output_path=output_path,
        )
        
        logger.info(f"PDF generado: {len(pdf_bytes)} bytes")
        return pdf_bytes
    
    def generar_resumen_texto(self, presupuesto: Budget) -> str:
        """
        Genera un resumen en texto del presupuesto.
        
        Args:
            presupuesto: Presupuesto
            
        Returns:
            str: Resumen legible
        """
        return presupuesto.resumen_texto()
    
    # ==========================================
    # Utilidades
    # ==========================================
    
    def validar_presupuesto(self, presupuesto: Budget) -> dict:
        """
        Valida que el presupuesto esté completo.
        
        Args:
            presupuesto: Presupuesto a validar
            
        Returns:
            dict: Resultado de validación con errores/warnings
        """
        errores = []
        warnings = []
        
        # Validar proyecto
        if presupuesto.proyecto.metros_cuadrados <= 0:
            errores.append("Los metros cuadrados deben ser mayores a 0")
        
        # Validar partidas
        if not presupuesto.partidas:
            warnings.append("El presupuesto no tiene partidas")
        
        # Validar cliente (warning, no error)
        if not presupuesto.tiene_cliente:
            warnings.append("No se han asignado datos del cliente")
        
        # Validar totales
        if presupuesto.subtotal <= 0:
            warnings.append("El subtotal es 0")
        
        return {
            "valido": len(errores) == 0,
            "errores": errores,
            "warnings": warnings,
            "completo": len(errores) == 0 and len(warnings) == 0,
        }
    
    def duplicar_presupuesto(self, presupuesto: Budget) -> Budget:
        """
        Crea una copia del presupuesto con nuevo ID y fecha.
        
        Args:
            presupuesto: Presupuesto original
            
        Returns:
            Budget: Copia del presupuesto
        """
        nuevo = presupuesto.model_copy(deep=True)
        nuevo.id = None  # Se generará nuevo
        nuevo.numero_presupuesto = None  # Se generará nuevo
        nuevo.fecha_emision = datetime.now()
        
        # Forzar regeneración de campos
        nuevo = Budget(**nuevo.model_dump(exclude={"id", "numero_presupuesto"}))
        
        logger.info(f"Presupuesto duplicado: {nuevo.numero_presupuesto}")
        return nuevo
    
    # ==========================================
    # Guardado en Base de Datos
    # ==========================================
    
    def guardar_presupuesto(self, user_id: str, presupuesto: Budget) -> dict:
        """
        Guarda el presupuesto en la base de datos asociado al usuario.
        
        Args:
            user_id: ID del usuario
            presupuesto: Presupuesto a guardar
            
        Returns:
            dict: Información del presupuesto guardado
        """
        import json
        from ...infrastructure.database import get_db_session
        from ...infrastructure.database.models import Budget as BudgetModel, User
        
        try:
            with get_db_session() as session:
                # Preparar datos para guardar
                budget_db = BudgetModel(
                    user_id=user_id,
                    numero_presupuesto=presupuesto.numero_presupuesto,
                    datos_proyecto=json.dumps({
                        "tipo_inmueble": presupuesto.proyecto.tipo_inmueble.value,
                        "metros_cuadrados": presupuesto.proyecto.metros_cuadrados,
                        "calidad": presupuesto.proyecto.calidad_general.value,
                        "es_vivienda_habitual": presupuesto.proyecto.es_vivienda_habitual,
                        "estado_actual": presupuesto.proyecto.estado_actual,
                    }),
                    partidas=json.dumps([
                        {
                            "codigo": p.codigo,
                            "descripcion": p.descripcion,
                            "cantidad": p.cantidad,
                            "unidad": p.unidad,
                            "precio_unitario": p.precio_unitario,
                            "subtotal": p.subtotal,
                            "es_paquete": p.es_paquete,
                        }
                        for p in presupuesto.partidas
                    ]),
                    paquetes=json.dumps([
                        {
                            "codigo": p.codigo,
                            "nombre": p.nombre if hasattr(p, 'nombre') else p.descripcion,
                        }
                        for p in presupuesto.partidas if p.es_paquete
                    ]),
                    # Datos del cliente
                    cliente_nombre=presupuesto.cliente.nombre if presupuesto.cliente else None,
                    cliente_email=presupuesto.cliente.email if presupuesto.cliente else None,
                    cliente_telefono=presupuesto.cliente.telefono if presupuesto.cliente else None,
                    cliente_direccion=presupuesto.cliente.direccion_obra if presupuesto.cliente else None,
                    # Totales
                    total_sin_iva=presupuesto.subtotal,
                    total_con_iva=presupuesto.total,
                    iva_aplicado=presupuesto.iva_porcentaje,
                    fecha_validez=presupuesto.fecha_validez,
                )
                
                session.add(budget_db)
                
                # Actualizar contador del usuario
                user = session.query(User).filter_by(id=user_id).first()
                if user:
                    user.num_presupuestos += 1
                
                session.commit()
                
                logger.info(f"✓ Presupuesto guardado en BD: {presupuesto.numero_presupuesto} (user: {user_id})")
                
                return {
                    "id": budget_db.id,
                    "numero_presupuesto": budget_db.numero_presupuesto,
                    "total": budget_db.total_con_iva,
                    "guardado": True,
                }
                
        except Exception as e:
            logger.error(f"Error guardando presupuesto en BD: {e}")
            return {
                "guardado": False,
                "error": str(e),
            }


# Instancia singleton
_budget_service: Optional[BudgetService] = None


def get_budget_service() -> BudgetService:
    """
    Obtiene la instancia del servicio de presupuestos (singleton).
    
    Returns:
        BudgetService: Instancia del servicio
    """
    global _budget_service
    if _budget_service is None:
        _budget_service = BudgetService()
    return _budget_service