"""
Presupuesto Routes - Endpoints para cálculo y generación de presupuestos.
"""

from fastapi import APIRouter, HTTPException, Response
from loguru import logger
from typing import Dict, Any

from ..schemas.request import CalcularPresupuestoRequest, GenerarPDFRequest
from ..schemas.response import PresupuestoResponse, PartidaResponse, ErrorResponse
from ....application.crews.budget_crew import get_budget_crew
from ....domain.enums import PropertyType, QualityLevel, WorkCategory

router = APIRouter()


@router.post("/calcular", response_model=PresupuestoResponse)
async def calcular_presupuesto(request: CalcularPresupuestoRequest):
    """
    Calcula un presupuesto basado en los datos del proyecto y trabajos seleccionados.
    
    Args:
        request: Datos del proyecto y trabajos
    
    Returns:
        Presupuesto calculado con totales y desglose
    """
    try:
        logger.info("=" * 50)
        logger.info("Calculando presupuesto vía API...")
        logger.info(f"Proyecto: {request.proyecto.tipo_inmueble}, {request.proyecto.metros_cuadrados}m²")
        logger.info(f"Modo: {request.modo}, País: {request.pais}")
        
        # Preparar datos del formulario en el formato esperado por BudgetCrew
        datos_formulario = {
            "tipo_inmueble": request.proyecto.tipo_inmueble,
            "metros_cuadrados": request.proyecto.metros_cuadrados,
            "estado_actual": request.proyecto.estado_actual,
            "es_vivienda_habitual": request.proyecto.es_vivienda_habitual,
            "calidad_general": request.proyecto.calidad_general,
            "paquetes_seleccionados": [
                {
                    "id": p.id,
                    "cantidad": p.cantidad,
                    "metros": p.metros
                }
                for p in request.trabajos.paquetes
            ],
            "partidas_seleccionadas": [
                {
                    "categoria": p.categoria,
                    "partida": p.partida,
                    "cantidad": p.cantidad,
                    "calidad": p.calidad
                }
                for p in request.trabajos.partidas
            ],
            "modo_usuario": request.modo,
            "pais": request.pais,
        }
        
        # Usar BudgetCrew para procesar
        crew = get_budget_crew()
        resultado = crew.procesar_presupuesto(
            datos_formulario=datos_formulario,
            generar_pdf=False  # No generar PDF en este endpoint
        )
        
        if not resultado["exito"]:
            logger.error(f"Error en cálculo: {resultado['errores']}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Error al calcular presupuesto",
                    "errores": resultado["errores"],
                    "warnings": resultado.get("warnings", [])
                }
            )
        
        presupuesto = resultado["presupuesto"]
        
        # Convertir partidas a response schema
        partidas_response = [
            PartidaResponse(
                descripcion=p.descripcion,
                categoria=p.categoria,
                cantidad=p.cantidad,
                unidad=p.unidad,
                precio_unitario=p.precio_unitario,
                subtotal=p.subtotal,
                es_paquete=p.es_paquete,
                calidad=p.calidad.value if hasattr(p.calidad, 'value') else str(p.calidad)
            )
            for p in presupuesto.partidas
        ]
        
        # Crear response
        response = PresupuestoResponse(
            numero=presupuesto.numero_presupuesto,
            fecha_emision=presupuesto.fecha_emision_str,
            fecha_validez=presupuesto.fecha_validez_str,
            subtotal=presupuesto.subtotal,
            iva_porcentaje=presupuesto.iva_porcentaje,
            iva_importe=presupuesto.importe_iva,
            total=presupuesto.total,
            partidas=partidas_response,
            desglose_por_categoria=presupuesto.resumen_por_categorias(),
            num_partidas=presupuesto.num_partidas,
            dias_validez=presupuesto.dias_validez
        )
        
        logger.info(f"✓ Presupuesto calculado: {presupuesto.numero_presupuesto}")
        logger.info(f"  Total: {presupuesto.total:,.2f}€")
        logger.info("=" * 50)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error inesperado calculando presupuesto: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error interno del servidor", "detail": str(e)}
        )


@router.post("/pdf")
async def generar_pdf(request: GenerarPDFRequest):
    """
    Genera un PDF del presupuesto.
    
    Args:
        request: Datos del cliente y presupuesto
    
    Returns:
        PDF en bytes
    """
    try:
        logger.info(f"Generando PDF para cliente: {request.cliente.nombre}")
        
        # TODO: Implementar generación de PDF
        # Por ahora, retornar error not implemented
        raise HTTPException(
            status_code=501,
            detail="Generación de PDF no implementada aún en API"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generando PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explicar")
async def explicar_presupuesto(presupuesto_data: Dict[str, Any]):
    """
    Genera una explicación detallada del presupuesto usando IA.
    
    Args:
        presupuesto_data: Datos del presupuesto calculado
    
    Returns:
        Explicación generada por IA
    """
    try:
        logger.info("Generando explicación con IA...")
        
        # TODO: Implementar explicación con IA
        raise HTTPException(
            status_code=501,
            detail="Explicación con IA no implementada aún"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generando explicación: {e}")
        raise HTTPException(status_code=500, detail=str(e))
