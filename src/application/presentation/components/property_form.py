"""
Componente Property Form para Streamlit.

Formulario para seleccionar el tipo de inmueble
y configurar los datos básicos del proyecto.
"""

import streamlit as st
from typing import Optional

from src.domain.enums import PropertyType, QualityLevel


def render_property_form() -> Optional[dict]:
    """
    Renderiza el formulario de tipo de inmueble.
    
    Returns:
        dict: Datos del proyecto o None si no está completo
    """
    st.markdown("### 🏠 ¿Qué quieres reformar?")
    
    # Tipo de inmueble con cards visuales
    col1, col2, col3, col4 = st.columns(4)
    
    tipos = [
        (PropertyType.PISO, "🏢", "Piso", col1),
        (PropertyType.VIVIENDA, "🏠", "Vivienda", col2),
        (PropertyType.OFICINA, "🏢", "Oficina", col3),
        (PropertyType.LOCAL, "🏪", "Local", col4),
    ]
    
    # Inicializar estado si no existe
    if "tipo_inmueble" not in st.session_state:
        st.session_state.tipo_inmueble = None
    
    for tipo, icon, label, col in tipos:
        with col:
            selected = st.session_state.tipo_inmueble == tipo
            button_type = "primary" if selected else "secondary"
            
            if st.button(
                f"{icon}\n\n**{label}**",
                key=f"btn_{tipo.value}",
                use_container_width=True,
                type=button_type,
            ):
                st.session_state.tipo_inmueble = tipo
    
    # Mostrar selección actual
    if st.session_state.tipo_inmueble:
        tipo = st.session_state.tipo_inmueble
        st.success(f"Seleccionado: {tipo.icono} {tipo.display_name}")
    
    st.divider()
    
    # Metros cuadrados
    st.markdown("### 📐 ¿Cuántos metros cuadrados?")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        metros = st.number_input(
            "Superficie en m²",
            min_value=1.0,
            max_value=10000.0,
            value=st.session_state.get("metros_cuadrados", 80.0),
            step=5.0,
            help="Introduce la superficie total a reformar",
            key="metros_input",
        )
        st.session_state.metros_cuadrados = metros
    
    with col2:
        st.metric("Superficie", f"{metros:.0f} m²")
    
    # Slider alternativo para selección rápida
    metros_slider = st.slider(
        "O selecciona con el slider",
        min_value=10,
        max_value=500,
        value=int(metros),
        step=10,
        key="metros_slider",
    )
    
    if metros_slider != int(metros):
        st.session_state.metros_cuadrados = float(metros_slider)
    
    st.divider()
    
    # Nivel de calidad
    st.markdown("### 💎 ¿Qué nivel de calidad prefieres?")
    
    calidad_options = {
        "⚡ Básico - Económico": QualityLevel.BASICO,
        "⭐ Estándar - Recomendado": QualityLevel.ESTANDAR,
        "💎 Premium - Alta gama": QualityLevel.PREMIUM,
    }
    
    calidad_seleccionada = st.radio(
        "Selecciona el nivel de calidad",
        options=list(calidad_options.keys()),
        index=1,  # Estándar por defecto
        horizontal=True,
        key="calidad_radio",
    )
    
    calidad = calidad_options[calidad_seleccionada]
    st.session_state.calidad = calidad
    
    # Descripción de la calidad seleccionada
    st.info(calidad.descripcion)
    
    st.divider()
    
    # Estado del inmueble
    st.markdown("### 🔧 ¿En qué estado está el inmueble?")
    
    estado_options = {
        "🆕 Nuevo / Buen estado": "nuevo",
        "🏠 Normal / Uso habitual": "normal",
        "🏚️ Antiguo / Necesita actualización": "antiguo",
        "💥 Ruina / Reforma total necesaria": "ruina",
    }
    
    estado_seleccionado = st.select_slider(
        "Estado actual",
        options=list(estado_options.keys()),
        value="🏠 Normal / Uso habitual",
        key="estado_slider",
    )
    
    estado = estado_options[estado_seleccionado]
    st.session_state.estado_actual = estado
    
    st.divider()
    
    # Vivienda habitual (solo si es piso/vivienda)
    if st.session_state.tipo_inmueble in [PropertyType.PISO, PropertyType.VIVIENDA]:
        st.markdown("### 🏡 ¿Es tu vivienda habitual?")
        
        es_vivienda_habitual = st.checkbox(
            "Sí, es mi vivienda habitual (IVA reducido 10%)",
            value=st.session_state.get("es_vivienda_habitual", False),
            help="Si es tu vivienda habitual, aplica IVA reducido del 10% en lugar del 21%",
            key="vivienda_habitual_check",
        )
        st.session_state.es_vivienda_habitual = es_vivienda_habitual
        
        if es_vivienda_habitual:
            st.success("✅ Se aplicará IVA reducido del 10%")
        else:
            st.info("Se aplicará IVA general del 21%")
    else:
        st.session_state.es_vivienda_habitual = False
        st.info("💼 Para locales y oficinas se aplica IVA general del 21%")
    
    st.divider()
    
    # Ubicación (opcional)
    st.markdown("### 📍 Ubicación (opcional)")
    
    ubicacion = st.text_input(
        "Ciudad o zona",
        value=st.session_state.get("ubicacion", ""),
        placeholder="Ej: Madrid, Barcelona, Valencia...",
        key="ubicacion_input",
    )
    st.session_state.ubicacion = ubicacion if ubicacion else None
    
    # Validar si está completo
    if st.session_state.tipo_inmueble and st.session_state.metros_cuadrados > 0:
        return {
            "tipo_inmueble": st.session_state.tipo_inmueble,
            "metros_cuadrados": st.session_state.metros_cuadrados,
            "calidad": st.session_state.calidad,
            "estado_actual": st.session_state.estado_actual,
            "es_vivienda_habitual": st.session_state.es_vivienda_habitual,
            "ubicacion": st.session_state.ubicacion,
        }
    
    return None


def render_property_summary(datos: dict) -> None:
    """
    Renderiza un resumen del proyecto seleccionado.
    
    Args:
        datos: Datos del proyecto
    """
    tipo = datos["tipo_inmueble"]
    
    st.markdown("### 📋 Resumen del proyecto")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Tipo",
            f"{tipo.icono} {tipo.display_name}",
        )
    
    with col2:
        st.metric(
            "Superficie",
            f"{datos['metros_cuadrados']:.0f} m²",
        )
    
    with col3:
        calidad = datos["calidad"]
        st.metric(
            "Calidad",
            f"{calidad.icono} {calidad.display_name}",
        )
    
    # Info adicional
    col1, col2 = st.columns(2)
    
    with col1:
        iva = 10 if datos["es_vivienda_habitual"] else 21
        st.info(f"💰 IVA aplicable: **{iva}%**")
    
    with col2:
        st.info(f"🔧 Estado: **{datos['estado_actual'].capitalize()}**")