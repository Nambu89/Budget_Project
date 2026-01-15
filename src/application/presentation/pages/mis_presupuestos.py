"""
Página Mis Presupuestos - Gestión de presupuestos guardados.
"""

import streamlit as st
from loguru import logger
from datetime import datetime

from ....application.services.user_budget_service import get_user_budget_service
from ....application.crews import get_budget_crew


def render_mis_presupuestos():
    """
    Renderiza la página de gestión de presupuestos del usuario.
    """
    st.title(" Mis Presupuestos")
    
    if not st.session_state.get("authenticated"):
        st.warning("Debes iniciar sesión para ver tus presupuestos")
        return
    
    user_id = st.session_state.user["id"]
    
    # Obtener presupuestos
    budget_service = get_user_budget_service()
    presupuestos = budget_service.get_user_budgets(user_id)
    
    if not presupuestos:
        st.info(" Aún no tienes presupuestos guardados")
        st.markdown("---")
        if st.button(" Crear mi primer presupuesto", type="primary", use_container_width=True):
            st.session_state.current_page = "calculator"
            st.rerun()
        return
    
    # Mostrar estadísticas
    col, col, col = st.columns()
    
    with col:
        st.metric("Total Presupuestos", len(presupuestos))
    
    with col:
        total_facturado = sum(p['total_con_iva'] for p in presupuestos)
        st.metric("Total Facturado", f"{total_facturado:,.f} €")
    
    with col:
        iva_medio = sum(p['iva_aplicado'] for p in presupuestos) / len(presupuestos)
        st.metric("IVA Medio", f"{iva_medio:.0f}%")
    
    st.markdown("---")
    
    # Tabla de presupuestos
    st.markdown("###  Mis Presupuestos Guardados")
    
    for presupuesto in presupuestos:
        with st.expander(
            f" {presupuesto['numero_presupuesto']} - {presupuesto['total_con_iva']:,.f} €",
            expanded=False
        ):
            col, col = st.columns([, ])
            
            with col:
                # Información del presupuesto
                datos_proyecto = presupuesto['datos_proyecto']
                
                st.markdown(f"**Fecha:** {presupuesto['fecha_creacion'][:0]}")
                st.markdown(f"**Tipo:** {datos_proyecto.get('tipo_inmueble', 'N/A').capitalize()}")
                st.markdown(f"**Superficie:** {datos_proyecto.get('metros_cuadrados', 0):.0f} m²")
                st.markdown(f"**Calidad:** {datos_proyecto.get('calidad', 'N/A').capitalize()}")
                st.markdown(f"**IVA:** %")  # SIEMPRE %
                
                # Partidas
                partidas = presupuesto['partidas']
                if partidas:
                    st.markdown(f"**Partidas:** {len(partidas)}")
                    with st.expander("Ver detalle de partidas"):
                        for p in partidas:
                            tipo = " Paquete" if p.get('es_paquete') else " Individual"
                            st.markdown(f"- {tipo}: {p['descripcion'][:0]}... - {p['subtotal']:.f} €")
            
            with col:
                # Acciones
                st.markdown("**Acciones:**")
                
                # Descargar PDF
                if st.button(
                    " Descargar PDF",
                    key=f"download_{presupuesto['id']}",
                    use_container_width=True
                ):
                    try:
                        # Reconstruir objeto Budget
                        budget_obj = budget_service.reconstruct_budget_object(presupuesto)
                        
                        # Generar PDF usando el crew
                        crew = get_budget_crew()
                        pdf_bytes = crew.document_agent.generar_pdf(budget_obj)
                        
                        # Ofrecer descarga
                        st.download_button(
                            label=" Guardar PDF",
                            data=pdf_bytes,
                            file_name=f"{presupuesto['numero_presupuesto']}.pdf",
                            mime="application/pdf",
                            key=f"save_{presupuesto['id']}",
                            use_container_width=True
                        )
                        
                        st.success(" PDF generado correctamente")
                        
                    except Exception as e:
                        logger.error(f"Error generando PDF: {e}")
                        st.error(f"Error al generar PDF: {str(e)}")
                
                # Eliminar
                if st.button(
                    " Eliminar",
                    key=f"delete_{presupuesto['id']}",
                    type="secondary",
                    use_container_width=True
                ):
                    if budget_service.delete_budget(presupuesto['id'], user_id):
                        st.success(" Presupuesto eliminado")
                        st.rerun()
                    else:
                        st.error(" Error al eliminar")