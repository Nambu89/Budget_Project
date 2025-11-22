"""
Componente Results Display para Streamlit.

Muestra los resultados del presupuesto calculado
con desglose, totales y opciones de descarga.
"""

import streamlit as st
from typing import Optional
import base64

from ...domain.models import Budget


def render_results(
    presupuesto: Budget,
    desglose: dict,
    sugerencias: list = None,
) -> None:
    """
    Renderiza los resultados del presupuesto.
    
    Args:
        presupuesto: Presupuesto calculado
        desglose: Desglose detallado
        sugerencias: Lista de sugerencias de optimización
    """
    st.markdown("## 📊 Resultados del Presupuesto")
    
    # Número y fecha
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📋 Nº Presupuesto", presupuesto.numero_presupuesto)
    
    with col2:
        st.metric("📅 Fecha", presupuesto.fecha_emision_str)
    
    with col3:
        st.metric("⏰ Válido hasta", presupuesto.fecha_validez_str)
    
    st.divider()
    
    # Total destacado
    st.markdown(f"""
        <div class="total-display">
            💰 TOTAL: {presupuesto.total:,.2f} €
            <br>
            <span style="font-size: 0.9rem; font-weight: normal;">
                (IVA {presupuesto.iva_porcentaje}% incluido)
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Desglose en columnas
    col1, col2 = st.columns(2)
    
    with col1:
        _render_desglose_partidas(presupuesto)
    
    with col2:
        _render_desglose_totales(presupuesto, desglose)
    
    # Sugerencias de optimización
    if sugerencias:
        st.divider()
        _render_sugerencias(sugerencias)
    
    # Reglas aplicadas
    st.divider()
    _render_reglas_aplicadas(desglose)


def _render_desglose_partidas(presupuesto: Budget) -> None:
    """Renderiza el desglose de partidas."""
    st.markdown("### 📋 Desglose de partidas")
    
    if not presupuesto.partidas:
        st.info("No hay partidas en este presupuesto")
        return
    
    # Tabla de partidas
    for i, partida in enumerate(presupuesto.partidas, 1):
        tipo_badge = "📦" if partida.es_paquete else "🔧"
        
        with st.expander(
            f"{tipo_badge} {partida.descripcion[:40]}... - **{partida.subtotal:,.2f}€**",
            expanded=False,
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Descripción:** {partida.descripcion}")
                st.markdown(f"**Categoría:** {partida.categoria_nombre}")
                st.markdown(f"**Calidad:** {partida.calidad_nombre}")
            
            with col2:
                st.markdown(f"**Cantidad:** {partida.cantidad} {partida.unidad}")
                st.markdown(f"**Precio unitario:** {partida.precio_unitario:,.2f}€/{partida.unidad}")
                st.markdown(f"**Subtotal:** {partida.subtotal:,.2f}€")
            
            if partida.es_paquete:
                st.info("📦 Este es un paquete completo (sin markup)")
            else:
                st.warning("🔧 Partida individual (+15% markup aplicado)")
    
    # Resumen por categorías
    st.markdown("#### 📈 Por categoría")
    
    resumen = presupuesto.resumen_por_categorias()
    
    for categoria, importe in resumen.items():
        porcentaje = (importe / presupuesto.subtotal * 100) if presupuesto.subtotal > 0 else 0
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**{categoria}**")
        
        with col2:
            st.markdown(f"{importe:,.2f}€")
        
        with col3:
            st.progress(porcentaje / 100)


def _render_desglose_totales(presupuesto: Budget, desglose: dict) -> None:
    """Renderiza el desglose de totales."""
    st.markdown("### 💰 Desglose económico")
    
    # Tabla de totales
    datos_totales = [
        ("Subtotal (sin IVA)", presupuesto.subtotal),
    ]
    
    if presupuesto.descuento_porcentaje > 0:
        datos_totales.append((
            f"Descuento ({presupuesto.descuento_porcentaje:.1f}%)",
            -presupuesto.importe_descuento,
        ))
    
    datos_totales.append(("Base imponible", presupuesto.base_imponible))
    
    # Redondeo al alza
    if "redondeo_importe" in desglose and desglose["redondeo_importe"] > 0:
        datos_totales.append((
            f"Redondeo al alza ({desglose['redondeo_porcentaje']}%)",
            desglose["redondeo_importe"],
        ))
        datos_totales.append(("Base con redondeo", desglose["base_imponible"]))
    
    datos_totales.append((
        f"IVA ({presupuesto.iva_porcentaje}%)",
        desglose.get("iva_importe", presupuesto.importe_iva),
    ))
    
    # Mostrar tabla
    for concepto, importe in datos_totales:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(concepto)
        
        with col2:
            if importe < 0:
                st.markdown(f"<span style='color: #ef4444;'>-{abs(importe):,.2f}€</span>", 
                           unsafe_allow_html=True)
            else:
                st.markdown(f"{importe:,.2f}€")
    
    st.divider()
    
    # Total final
    total_final = desglose.get("total", presupuesto.total)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### **TOTAL**")
    
    with col2:
        st.markdown(f"### **{total_final:,.2f}€**")
    
    # Info IVA
    if presupuesto.proyecto.es_vivienda_habitual:
        st.success("✅ Se ha aplicado IVA reducido del 10% por ser vivienda habitual")
    else:
        st.info("ℹ️ Se ha aplicado IVA general del 21%")


def _render_sugerencias(sugerencias: list) -> None:
    """Renderiza las sugerencias de optimización."""
    st.markdown("### 💡 Sugerencias de ahorro")
    
    for sug in sugerencias:
        if sug.get("tipo") == "paquete":
            st.success(f"""
                **¿Sabías que puedes ahorrar {sug['ahorro']:,.2f}€?**
                
                {sug['mensaje']}
            """)
        elif sug.get("tipo") == "iva":
            st.info(sug["mensaje"])
        else:
            st.info(sug["mensaje"])


def _render_reglas_aplicadas(desglose: dict) -> None:
    """Renderiza las reglas de negocio aplicadas."""
    with st.expander("ℹ️ Reglas aplicadas a este presupuesto"):
        reglas = desglose.get("reglas_aplicadas", {})
        
        st.markdown(f"""
        - **Markup partidas individuales:** {reglas.get('markup_partidas', '15%')}
        - **Redondeo al alza:** {reglas.get('redondeo_alza', '5%')}
        - **IVA aplicado:** {reglas.get('iva', '21%')}
        
        *Los paquetes completos NO tienen markup, por eso son más económicos.*
        """)


def render_download_section(
    presupuesto: Budget,
    pdf_bytes: Optional[bytes] = None,
    resumen_texto: Optional[str] = None,
) -> None:
    """
    Renderiza la sección de descargas.
    
    Args:
        presupuesto: Presupuesto
        pdf_bytes: PDF en bytes (opcional)
        resumen_texto: Resumen en texto (opcional)
    """
    st.markdown("### 📥 Descargar presupuesto")
    
    if pdf_bytes:
        st.download_button(
            label="📄 Descargar PDF",
            data=pdf_bytes,
            file_name=f"presupuesto_{presupuesto.numero_presupuesto}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
    else:
        st.button(
            "📄 Generar PDF",
            disabled=True,
            use_container_width=True,
        )


def render_empty_results() -> None:
    """Renderiza mensaje cuando no hay resultados."""
    st.info("""
        ### 📋 Aquí aparecerá tu presupuesto
        
        Completa los pasos anteriores para generar tu presupuesto:
        
        1. ✅ Selecciona el tipo de inmueble
        2. ✅ Indica la superficie
        3. ✅ Elige los trabajos a realizar
        4. ⏳ ¡Genera tu presupuesto!
    """)


def render_comparison(comparativa: dict) -> None:
    """
    Renderiza una comparativa entre opciones.
    
    Args:
        comparativa: Datos de la comparativa
    """
    st.markdown("### ⚖️ Comparativa de opciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 Partidas individuales")
        st.metric(
            "Total",
            f"{comparativa['total_partidas']:,.2f}€",
        )
    
    with col2:
        st.markdown("#### 📦 Paquete completo")
        st.metric(
            "Total",
            f"{comparativa['total_paquete']:,.2f}€",
            delta=f"-{comparativa['ahorro']:,.2f}€" if comparativa['ahorro'] > 0 else None,
            delta_color="inverse",
        )
    
    if comparativa["ahorro"] > 0:
        st.success(f"""
            💡 **{comparativa['mensaje_recomendacion']}**
        """)
    else:
        st.info(comparativa["mensaje_recomendacion"])