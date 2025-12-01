"""
Aplicación principal de Streamlit.

Orquesta todos los componentes de la UI para crear
la experiencia completa de generación de presupuestos.
"""

import streamlit as st
from loguru import logger

from src.config.settings import settings
from src.application.crews import get_budget_crew
from src.presentation.components import (
    render_header,
    render_sidebar_info,
    render_progress_steps,
    render_footer,
    render_property_form,
    render_property_summary,
    render_work_selector,
    render_work_summary,
    render_results,
    render_download_section,
    render_empty_results,
    render_customer_form,
    render_customer_summary,
    render_login,
    render_user_info,
)


def init_session_state() -> None:
    """Inicializa el estado de la sesión."""
    defaults = {
        "current_step": 1,
        "proyecto_data": None,
        "partidas_seleccionadas": [],
        "paquetes_seleccionados": [],
        "presupuesto": None,
        "desglose": None,
        "sugerencias": [],
        "pdf_bytes": None,
        "cliente_data": None,
        "proceso_completado": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def main() -> None:
    """Función principal de la aplicación."""
    # Verificar autenticación
    if not st.session_state.get("authenticated"):
        render_login()
        return
    
    # Inicializar estado
    init_session_state()
    
    # Gestión de páginas
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "calculator"
    
    # Renderizar header (configura página también) - SOLO UNA VEZ
    render_header()
    
    # Sidebar con información - SOLO UNA VEZ
    render_sidebar_info()
    
    # Renderizar según página actual
    if st.session_state.current_page == "mis_presupuestos":
        from src.presentation.pages.mis_presupuestos import render_mis_presupuestos
        render_mis_presupuestos()
        render_footer()
        return
    
    # Si no, renderizar calculadora normal
    # Progreso
    render_progress_steps(st.session_state.current_step)
    
    st.divider()
    
    # Contenido principal según el paso actual
    if st.session_state.current_step == 1:
        _render_step_1_proyecto()
    
    elif st.session_state.current_step == 2:
        _render_step_2_trabajos()
    
    elif st.session_state.current_step == 3:
        _render_step_3_calculo()
    
    elif st.session_state.current_step == 4:
        _render_step_4_cliente()
    
    elif st.session_state.current_step == 5:
        _render_step_5_final()
    
    # Footer
    render_footer()


def _render_step_1_proyecto() -> None:
    """Renderiza el paso 1: Datos del proyecto."""
    st.markdown("## Paso 1: Información del proyecto")
    
    datos_proyecto = render_property_form()
    
    st.divider()
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if datos_proyecto:
            if st.button("Siguiente →", type="primary", use_container_width=True):
                st.session_state.proyecto_data = datos_proyecto
                st.session_state.current_step = 2
                st.rerun()
        else:
            st.button(
                "Siguiente →",
                disabled=True,
                use_container_width=True,
                help="Completa la información del proyecto",
            )
    
    with col1:
        if datos_proyecto:
            st.success("✅ Proyecto configurado correctamente")
        else:
            st.warning("⚠️ Selecciona el tipo de inmueble para continuar")


def _render_step_2_trabajos() -> None:
    """Renderiza el paso 2: Selección de trabajos."""
    st.markdown("## Paso 2: Trabajos a realizar")
    
    # Resumen del proyecto
    if st.session_state.proyecto_data:
        render_property_summary(st.session_state.proyecto_data)
        st.divider()
    
    # Selector de trabajos
    calidad = st.session_state.proyecto_data.get("calidad") if st.session_state.proyecto_data else None
    trabajos = render_work_selector(calidad)
    
    st.divider()
    
    # Navegación
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("← Anterior", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    
    with col2:
        render_work_summary()
    
    with col3:
        tiene_trabajos = (
            len(st.session_state.partidas_seleccionadas) > 0 or
            len(st.session_state.paquetes_seleccionados) > 0
        )
        
        if tiene_trabajos:
            if st.button("Calcular presupuesto →", type="primary", use_container_width=True):
                st.session_state.current_step = 3
                st.rerun()
        else:
            st.button(
                "Calcular presupuesto →",
                disabled=True,
                use_container_width=True,
                help="Selecciona al menos un trabajo",
            )


def _render_step_3_calculo() -> None:
    """Renderiza el paso 3: Cálculo del presupuesto."""
    st.markdown("## Paso 3: Tu presupuesto")
    
    # Calcular si no existe
    if st.session_state.presupuesto is None:
        with st.spinner("🔄 Calculando tu presupuesto..."):
            _calcular_presupuesto()
    
    # Mostrar resultados
    if st.session_state.presupuesto:
        render_results(
            presupuesto=st.session_state.presupuesto,
            desglose=st.session_state.desglose,
            sugerencias=st.session_state.sugerencias,
        )
        
        st.divider()
        
        # Navegación
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("← Modificar trabajos", use_container_width=True):
                st.session_state.presupuesto = None
                st.session_state.current_step = 2
                st.rerun()
        
        with col2:
            if st.button("🔄 Recalcular", use_container_width=True):
                st.session_state.presupuesto = None
                st.rerun()
        
        with col3:
            if st.button("Continuar →", type="primary", use_container_width=True):
                st.session_state.current_step = 4
                st.rerun()
    else:
        render_empty_results()
        
        if st.button("← Volver", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()


def _render_step_4_cliente() -> None:
    """Renderiza el paso 4: Datos del cliente."""
    st.markdown("## Paso 4: Tus datos")
    
    # Resumen del presupuesto
    if st.session_state.presupuesto:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
                **Presupuesto:** {st.session_state.presupuesto.numero_presupuesto}  
                **Total:** {st.session_state.presupuesto.total:,.2f}€ (IVA incluido)
            """)
        
        with col2:
            if st.button("← Volver al presupuesto"):
                st.session_state.current_step = 3
                st.rerun()
    
    st.divider()
    
    # Formulario de cliente
    datos_cliente = render_customer_form()
    
    if datos_cliente:
        st.session_state.cliente_data = datos_cliente
        st.session_state.current_step = 5
        st.rerun()


def _render_step_5_final() -> None:
    """Renderiza el paso 5: Presupuesto final."""
    st.markdown("## ✅ ¡Presupuesto completado!")
    
    # Asignar cliente al presupuesto y generar PDF
    if st.session_state.pdf_bytes is None:
        with st.spinner("📄 Generando tu presupuesto en PDF..."):
            _finalizar_presupuesto()
    
    # Mostrar resumen final
    if st.session_state.presupuesto:
        presupuesto = st.session_state.presupuesto
        
        # Resumen del cliente
        if st.session_state.cliente_data:
            render_customer_summary(st.session_state.cliente_data)
        
        st.divider()
        
        # Resultados
        render_results(
            presupuesto=presupuesto,
            desglose=st.session_state.desglose,
            sugerencias=[],  # Sin sugerencias en paso final
        )
        
        st.divider()
        
        # Descargas
        render_download_section(
            presupuesto=presupuesto,
            pdf_bytes=st.session_state.pdf_bytes,
            resumen_texto=presupuesto.resumen_texto,
        )
        
        st.divider()
        
        # Acciones finales
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Nuevo presupuesto", use_container_width=True):
                _reset_session()
                st.rerun()
        
        with col2:
            st.button(
                "📧 Enviar por email",
                use_container_width=True,
                disabled=True,
                help="Próximamente",
            )
        
        with col3:
            st.button(
                "📅 Solicitar visita",
                use_container_width=True,
                disabled=True,
                help="Próximamente",
            )
        
        # Mensaje final
        st.success(f"""
            ### 🎉 ¡Gracias por usar nuestra calculadora!
            
            Tu presupuesto **{presupuesto.numero_presupuesto}** está listo.
            
            **Próximos pasos:**
            1. Descarga tu presupuesto en PDF
            2. Revísalo con calma
            3. Contáctanos para una visita técnica gratuita
            
            📞 {settings.empresa_telefono}  
            ✉️ {settings.empresa_email}
        """)


def _calcular_presupuesto() -> None:
    """Calcula el presupuesto usando el BudgetCrew."""
    try:
        crew = get_budget_crew()
        
        # Preparar datos del formulario
        datos_formulario = {
            **st.session_state.proyecto_data,
            "partidas": st.session_state.partidas_seleccionadas,
            "paquetes": st.session_state.paquetes_seleccionados,
        }
        
        # Procesar
        resultado = crew.procesar_presupuesto(
            datos_formulario=datos_formulario,
            generar_pdf=False,  # PDF lo generamos después con datos del cliente
        )
        
        if resultado["exito"]:
            st.session_state.presupuesto = resultado["presupuesto"]
            st.session_state.desglose = resultado["desglose"]
            st.session_state.sugerencias = resultado.get("sugerencias", [])
            logger.info(f"Presupuesto calculado: {resultado['presupuesto'].numero_presupuesto}")
        else:
            for error in resultado["errores"]:
                st.error(f"❌ {error}")
            for warning in resultado["warnings"]:
                st.warning(f"⚠️ {warning}")
                
    except Exception as e:
        logger.exception(f"Error calculando presupuesto: {e}")
        st.error(f"Error al calcular el presupuesto: {str(e)}")


def _finalizar_presupuesto() -> None:
    """Finaliza el presupuesto asignando cliente y generando PDF."""
    try:
        crew = get_budget_crew()
        presupuesto = st.session_state.presupuesto
        cliente_data = st.session_state.cliente_data
        
        if presupuesto and cliente_data:
            # Asignar cliente
            crew.document_agent.budget_service.asignar_cliente(
                presupuesto=presupuesto,
                **cliente_data,
            )
            
            # Generar PDF
            pdf_bytes = crew.document_agent.generar_pdf(presupuesto)
            st.session_state.pdf_bytes = pdf_bytes
            
            # Guardar en BD si el usuario está autenticado
            if st.session_state.get("authenticated"):
                user_id = st.session_state.user["id"]
                resultado = crew.document_agent.budget_service.guardar_presupuesto(
                    user_id=user_id,
                    presupuesto=presupuesto
                )
                if resultado.get("guardado"):
                    logger.info(f"✓ Presupuesto guardado para usuario {user_id}")
                    
                    # Refrescar datos del usuario
                    from src.application.services.auth_service import get_auth_service
                    auth_service = get_auth_service()
                    st.session_state.user = auth_service.refresh_user_data(user_id)
                    
                else:
                    logger.warning(f"No se pudo guardar presupuesto: {resultado.get('error')}")
            
            # Actualizar desglose
            st.session_state.desglose = crew.calculator.obtener_desglose_completo(presupuesto)
            
            logger.info(f"Presupuesto finalizado: {presupuesto.numero_presupuesto}")
            
    except Exception as e:
        logger.exception(f"Error finalizando presupuesto: {e}")
        st.error(f"Error al generar el PDF: {str(e)}")


def _reset_session() -> None:
    """Resetea la sesión para un nuevo presupuesto."""
    keys_to_reset = [
        "current_step",
        "proyecto_data",
        "partidas_seleccionadas",
        "paquetes_seleccionados",
        "presupuesto",
        "desglose",
        "sugerencias",
        "pdf_bytes",
        "cliente_data",
        "proceso_completado",
        "tipo_inmueble",
        "metros_cuadrados",
        "calidad",
        "estado_actual",
        "es_vivienda_habitual",
        "ubicacion",
    ]
    
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]
    
    init_session_state()


# Punto de entrada cuando se ejecuta directamente
if __name__ == "__main__":
    main()