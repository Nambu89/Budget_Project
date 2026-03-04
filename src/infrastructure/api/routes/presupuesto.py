"""
Presupuesto Routes - Endpoints para cálculo, PDF, guardado y gestión de presupuestos.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from loguru import logger
from typing import Dict, Any, List

from ..dependencies import get_current_user_id

from ..schemas.request import (
    CalcularPresupuestoRequest,
    GenerarPDFRequest,
    GuardarPresupuestoRequest,
)
from ..schemas.response import (
    PresupuestoResponse,
    PartidaResponse,
    ErrorResponse,
    UserBudgetResponse,
    UserBudgetsListResponse,
    GuardarPresupuestoResponse,
)
from ....application.crews.budget_crew import get_budget_crew
from ....application.services import get_budget_service, get_user_budget_service
from ....domain.models import Customer
from ....domain.enums import PropertyType, QualityLevel, WorkCategory

router = APIRouter()


def _preparar_datos_formulario(request: CalcularPresupuestoRequest) -> dict:
    """
    Convierte un request de cálculo al formato esperado por BudgetCrew.

    Args:
        request: Request con datos de proyecto y trabajos

    Returns:
        dict: Datos en formato BudgetCrew
    """
    return {
        "tipo_inmueble": request.proyecto.tipo_inmueble,
        "metros_cuadrados": request.proyecto.metros_cuadrados,
        "estado_actual": request.proyecto.estado_actual,
        "es_vivienda_habitual": request.proyecto.es_vivienda_habitual,
        "calidad_general": request.proyecto.calidad_general,
        "paquetes_seleccionados": [
            {
                "id": p.id,
                "cantidad": p.cantidad,
                "metros": p.metros,
            }
            for p in request.trabajos.paquetes
        ],
        "partidas_seleccionadas": [
            {
                "categoria": p.categoria,
                "partida": p.partida,
                "cantidad": p.cantidad,
                "calidad": p.calidad,
            }
            for p in request.trabajos.partidas
        ],
        "modo_usuario": request.modo,
        "pais": request.pais,
    }


def _calcular_con_crew(datos_formulario: dict, generar_pdf: bool = False) -> Any:
    """
    Ejecuta el cálculo con BudgetCrew y devuelve el presupuesto.

    Args:
        datos_formulario: Datos en formato BudgetCrew
        generar_pdf: Si generar PDF durante el cálculo

    Returns:
        Budget: Objeto presupuesto calculado

    Raises:
        HTTPException: Si el cálculo falla
    """
    crew = get_budget_crew()
    resultado = crew.procesar_presupuesto(
        datos_formulario=datos_formulario,
        generar_pdf=generar_pdf,
    )

    if not resultado["exito"]:
        logger.error(f"Error en cálculo: {resultado['errores']}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Error al calcular presupuesto",
                "errores": resultado["errores"],
                "warnings": resultado.get("warnings", []),
            },
        )

    return resultado["presupuesto"]


def _presupuesto_to_response(presupuesto: Any) -> PresupuestoResponse:
    """
    Convierte un Budget domain object a PresupuestoResponse.

    Args:
        presupuesto: Objeto Budget del dominio

    Returns:
        PresupuestoResponse: Response serializable
    """
    partidas_response = [
        PartidaResponse(
            descripcion=p.descripcion,
            categoria=p.categoria,
            cantidad=p.cantidad,
            unidad=p.unidad,
            precio_unitario=p.precio_unitario,
            subtotal=p.subtotal,
            es_paquete=p.es_paquete,
            calidad=p.calidad.value if hasattr(p.calidad, "value") else str(p.calidad),
        )
        for p in presupuesto.partidas
    ]

    return PresupuestoResponse(
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
        dias_validez=presupuesto.dias_validez,
    )


# ==========================================
# Cálculo
# ==========================================


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
        logger.info("Calculando presupuesto via API...")
        logger.info(f"Proyecto: {request.proyecto.tipo_inmueble}, {request.proyecto.metros_cuadrados}m2")
        logger.info(f"Modo: {request.modo}, Pais: {request.pais}")

        datos_formulario = _preparar_datos_formulario(request)
        presupuesto = _calcular_con_crew(datos_formulario)
        response = _presupuesto_to_response(presupuesto)

        logger.info(f"Presupuesto calculado: {presupuesto.numero_presupuesto}")
        logger.info(f"  Total: {presupuesto.total:,.2f}EUR")
        logger.info("=" * 50)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error inesperado calculando presupuesto: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error interno del servidor", "detail": str(e)},
        )


# ==========================================
# Generación de PDF
# ==========================================


@router.post("/pdf")
async def generar_pdf(request: GenerarPDFRequest):
    """
    Genera un PDF del presupuesto.

    Recalcula el presupuesto, asigna datos del cliente y genera el PDF.

    Args:
        request: Datos del cliente, proyecto y trabajos

    Returns:
        Response: PDF en bytes con content-type application/pdf
    """
    try:
        logger.info(f"Generando PDF para cliente: {request.cliente.nombre}")

        # Recalcular presupuesto
        calc_request = CalcularPresupuestoRequest(
            proyecto=request.proyecto,
            trabajos=request.trabajos,
            modo=request.modo,
            pais=request.pais,
        )
        datos_formulario = _preparar_datos_formulario(calc_request)
        presupuesto = _calcular_con_crew(datos_formulario)

        # Asignar cliente al presupuesto
        presupuesto.cliente = Customer(
            nombre=request.cliente.nombre,
            email=request.cliente.email,
            telefono=request.cliente.telefono,
            direccion_obra=request.cliente.direccion_obra,
        )

        # Generar PDF
        budget_service = get_budget_service()
        pdf_bytes = budget_service.generar_pdf(presupuesto)

        logger.info(f"PDF generado: {len(pdf_bytes)} bytes para {presupuesto.numero_presupuesto}")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="presupuesto_{presupuesto.numero_presupuesto}.pdf"',
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generando PDF: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error al generar PDF", "detail": str(e)},
        )


# ==========================================
# Guardar presupuesto
# ==========================================


@router.post("/guardar", response_model=GuardarPresupuestoResponse)
async def guardar_presupuesto(
    request: GuardarPresupuestoRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Guarda un presupuesto en la base de datos asociado al usuario autenticado.

    Args:
        request: Datos del presupuesto y cliente
        user_id: ID del usuario extraído del JWT

    Returns:
        GuardarPresupuestoResponse: Confirmación con ID y número
    """
    try:
        logger.info(f"Guardando presupuesto para usuario: {user_id}")

        # Recalcular presupuesto
        calc_request = CalcularPresupuestoRequest(
            proyecto=request.proyecto,
            trabajos=request.trabajos,
            modo=request.modo,
            pais=request.pais,
        )
        datos_formulario = _preparar_datos_formulario(calc_request)
        presupuesto = _calcular_con_crew(datos_formulario)

        # Asignar cliente
        presupuesto.cliente = Customer(
            nombre=request.cliente.nombre,
            email=request.cliente.email,
            telefono=request.cliente.telefono,
            direccion_obra=request.cliente.direccion_obra,
        )

        # Guardar en BD
        budget_service = get_budget_service()
        resultado = budget_service.guardar_presupuesto(
            user_id=user_id,
            presupuesto=presupuesto,
        )

        logger.info(f"Presupuesto guardado: {resultado['numero_presupuesto']}")

        return GuardarPresupuestoResponse(
            id=resultado["id"],
            numero_presupuesto=resultado["numero_presupuesto"],
            total=resultado["total"],
            guardado=resultado["guardado"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error guardando presupuesto: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error al guardar presupuesto", "detail": str(e)},
        )


# ==========================================
# Presupuestos del usuario
# ==========================================


@router.get("/mis-presupuestos", response_model=UserBudgetsListResponse)
async def listar_presupuestos_usuario(user_id: str = Depends(get_current_user_id)):
    """
    Lista los presupuestos guardados del usuario autenticado.

    Args:
        user_id: ID del usuario extraído del JWT

    Returns:
        UserBudgetsListResponse: Lista de presupuestos
    """
    try:
        logger.info(f"Listando presupuestos para usuario: {user_id}")

        user_budget_service = get_user_budget_service()
        budgets = user_budget_service.get_user_budgets(user_id=user_id)

        presupuestos = [
            UserBudgetResponse(
                id=b["id"],
                numero_presupuesto=b["numero_presupuesto"],
                datos_proyecto=b["datos_proyecto"],
                partidas=b["partidas"],
                cliente_nombre=b.get("cliente_nombre"),
                cliente_email=b.get("cliente_email"),
                total_sin_iva=b["total_sin_iva"],
                total_con_iva=b["total_con_iva"],
                iva_aplicado=b["iva_aplicado"],
                fecha_creacion=b.get("fecha_creacion"),
                fecha_validez=b.get("fecha_validez"),
            )
            for b in budgets
        ]

        return UserBudgetsListResponse(
            presupuestos=presupuestos,
            total=len(presupuestos),
        )

    except Exception as e:
        logger.exception(f"Error listando presupuestos: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error al listar presupuestos", "detail": str(e)},
        )


@router.delete("/{budget_id}")
async def eliminar_presupuesto(budget_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Elimina (soft delete) un presupuesto del usuario autenticado.

    Args:
        budget_id: ID del presupuesto
        user_id: ID del usuario extraído del JWT

    Returns:
        dict: Confirmación de eliminación
    """
    try:
        logger.info(f"Eliminando presupuesto {budget_id} del usuario {user_id}")

        user_budget_service = get_user_budget_service()
        eliminado = user_budget_service.delete_budget(
            budget_id=budget_id,
            user_id=user_id,
        )

        if not eliminado:
            raise HTTPException(
                status_code=404,
                detail="Presupuesto no encontrado",
            )

        return {"message": "Presupuesto eliminado correctamente", "id": budget_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error eliminando presupuesto: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Error al eliminar presupuesto", "detail": str(e)},
        )


# ==========================================
# Explicación IA (pendiente de implementación)
# ==========================================


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
        logger.info("Generando explicacion con IA...")

        raise HTTPException(
            status_code=501,
            detail="Explicacion con IA no implementada aun",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generando explicacion: {e}")
        raise HTTPException(status_code=500, detail=str(e))
