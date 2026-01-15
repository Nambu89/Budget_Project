"""
Componente Work Selector para Streamlit.

Permite seleccionar partidas individuales o paquetes
completos para el presupuesto.
"""

import streamlit as st
from typing import Optional

from src.config.pricing_data import PRICING_DATA, PACKAGES_DATA
from src.domain.enums import WorkCategory, QualityLevel


def render_work_selector(calidad_default: QualityLevel = QualityLevel.ESTANDAR) -> dict:
    """
    Renderiza el selector de trabajos/partidas.
    
    Args:
        calidad_default: Calidad por defecto del proyecto
        
    Returns:
        dict: Partidas y paquetes seleccionados
    """
    st.markdown("###  ¿Qué trabajos necesitas?")
    
    # Tabs para elegir entre paquetes o partidas individuales
    tab_paquetes, tab_partidas = st.tabs([
        " Paquetes completos (Recomendado)",
        " Partidas individuales",
    ])
    
    # Inicializar estado
    if "partidas_seleccionadas" not in st.session_state:
        st.session_state.partidas_seleccionadas = []
    if "paquetes_seleccionados" not in st.session_state:
        st.session_state.paquetes_seleccionados = []
    
    with tab_paquetes:
        _render_paquetes_selector()
    
    with tab_partidas:
        _render_partidas_selector(calidad_default)
    
    return {
        "partidas": st.session_state.partidas_seleccionadas,
        "paquetes": st.session_state.paquetes_seleccionados,
    }


def _render_paquetes_selector() -> None:
    """Renderiza el selector de paquetes completos."""
    st.markdown("""
     **Los paquetes incluyen todos los trabajos necesarios** y son 
    más económicos que contratar las partidas por separado.
    """)
    
    # Mostrar paquetes disponibles
    for paquete_key, paquete_data in PACKAGES_DATA.items():
        with st.expander(
            f" {paquete_data['nombre']}",
            expanded=paquete_key in st.session_state.paquetes_seleccionados,
        ):
            st.markdown(f"**{paquete_data['descripcion']}**")
            
            st.markdown("**Incluye:**")
            for item in paquete_data["incluye"]:
                st.markdown(f"-  {item}")
            
            # Mostrar precios
            st.markdown("**Precios orientativos:**")
            precios = paquete_data["precios"]
            
            col, col, col = st.columns()
            
            with col:
                if "precio_m" in precios["basico"]:
                    st.metric(" Básico", f"{precios['basico']['precio_m']}€/m²")
                else:
                    st.metric(" Básico", f"desde {precios['basico']['precio_base']}€")
            
            with col:
                if "precio_m" in precios["estandar"]:
                    st.metric("⭐ Estándar", f"{precios['estandar']['precio_m']}€/m²")
                else:
                    st.metric("⭐ Estándar", f"desde {precios['estandar']['precio_base']}€")
            
            with col:
                if "precio_m" in precios["premium"]:
                    st.metric(" Premium", f"{precios['premium']['precio_m']}€/m²")
                else:
                    st.metric(" Premium", f"desde {precios['premium']['precio_base']}€")
            
            # ══════════════════════════════════════════════════════════════
            # OPCIONES ADICIONALES (ej: armario empotrado para habitación)
            # ══════════════════════════════════════════════════════════════
            if "opciones" in paquete_data:
                st.markdown("---")
                st.markdown("**Opciones adicionales:**")
                
                for opcion_key, opcion_data in paquete_data["opciones"].items():
                    # Inicializar estado de la opción si no existe
                    opcion_state_key = f"opcion_{paquete_key}_{opcion_key}"
                    if opcion_state_key not in st.session_state:
                        st.session_state[opcion_state_key] = False
                    
                    # Checkbox para la opción
                    opcion_seleccionada = st.checkbox(
                        f" {opcion_data['descripcion']}",
                        value=st.session_state[opcion_state_key],
                        key=f"chk_{opcion_state_key}",
                        help=f"Precio: +{opcion_data['precios']['estandar']}€ (calidad estándar)"
                    )
                    st.session_state[opcion_state_key] = opcion_seleccionada
                    
                    if opcion_seleccionada:
                        col_a, col_b, col_c = st.columns()
                        with col_a:
                            st.caption(f" +{opcion_data['precios']['basico']}€")
                        with col_b:
                            st.caption(f"⭐ +{opcion_data['precios']['estandar']}€")
                        with col_c:
                            st.caption(f" +{opcion_data['precios']['premium']}€")
            
            # Botón para añadir/quitar
            if paquete_key in st.session_state.paquetes_seleccionados:
                if st.button(
                    f" Quitar {paquete_data['nombre']}",
                    key=f"remove_pkg_{paquete_key}",
                    type="secondary",
                ):
                    st.session_state.paquetes_seleccionados.remove(paquete_key)
                    st.rerun()
            else:
                if st.button(
                    f" Añadir {paquete_data['nombre']}",
                    key=f"add_pkg_{paquete_key}",
                    type="primary",
                ):
                    st.session_state.paquetes_seleccionados.append(paquete_key)
                    st.rerun()
    
    # Resumen de paquetes seleccionados
    if st.session_state.paquetes_seleccionados:
        st.divider()
        st.markdown("###  Paquetes seleccionados")
        for pkg in st.session_state.paquetes_seleccionados:
            st.success(f" {PACKAGES_DATA[pkg]['nombre']}")


def _render_partidas_selector(calidad_default: QualityLevel) -> None:
    """Renderiza el selector de partidas individuales."""
    st.markdown("""
     **Las partidas individuales tienen un incremento del %** 
    respecto a los paquetes completos.
    """)
    
    # Selector de categoría
    categorias = list(PRICING_DATA.keys())
    categoria_nombres = {
        cat: WorkCategory(cat).display_name 
        for cat in categorias
    }
    
    categoria_seleccionada = st.selectbox(
        "Selecciona una categoría",
        options=categorias,
        format_func=lambda x: f"{WorkCategory(x).icono} {categoria_nombres[x]}",
        key="categoria_select",
    )
    
    if categoria_seleccionada:
        st.markdown(f"### {WorkCategory(categoria_seleccionada).icono} {categoria_nombres[categoria_seleccionada]}")
        
        partidas = PRICING_DATA[categoria_seleccionada]
        
        for partida_key, partida_data in partidas.items():
            with st.expander(f" {partida_data['descripcion'][:0]}..."):
                st.markdown(f"**{partida_data['descripcion']}**")
                st.markdown(f"Unidad: **{partida_data['unidad']}**")
                
                # Precios
                col, col, col = st.columns()
                with col:
                    st.metric(" Básico", f"{partida_data['basico']}€/{partida_data['unidad']}")
                with col:
                    st.metric("⭐ Estándar", f"{partida_data['estandar']}€/{partida_data['unidad']}")
                with col:
                    st.metric(" Premium", f"{partida_data['premium']}€/{partida_data['unidad']}")
                
                # Formulario para añadir
                col, col, col = st.columns([, , ])
                
                with col:
                    cantidad = st.number_input(
                        f"Cantidad ({partida_data['unidad']})",
                        min_value=0.0,
                        value=0.0,
                        step=.0 if partida_data['unidad'] == 'ud' else 0.,
                        key=f"cant_{categoria_seleccionada}_{partida_key}",
                    )
                
                with col:
                    calidad_partida = st.selectbox(
                        "Calidad",
                        options=[QualityLevel.BASICO, QualityLevel.ESTANDAR, QualityLevel.PREMIUM],
                        index=,
                        format_func=lambda x: x.display_name,
                        key=f"cal_{categoria_seleccionada}_{partida_key}",
                    )
                
                with col:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if cantidad > 0:
                        if st.button(
                            " Añadir",
                            key=f"add_{categoria_seleccionada}_{partida_key}",
                            type="primary",
                        ):
                            nueva_partida = {
                                "categoria": categoria_seleccionada,
                                "partida": partida_key,
                                "cantidad": cantidad,
                                "calidad": calidad_partida.value,
                                "descripcion": partida_data["descripcion"],
                                "unidad": partida_data["unidad"],
                            }
                            st.session_state.partidas_seleccionadas.append(nueva_partida)
                            st.success(f" Añadida: {partida_data['descripcion'][:0]}...")
                            st.rerun()
    
    # Resumen de partidas seleccionadas
    if st.session_state.partidas_seleccionadas:
        st.divider()
        st.markdown("###  Partidas seleccionadas")
        
        for i, partida in enumerate(st.session_state.partidas_seleccionadas):
            col, col, col = st.columns([, , ])
            
            with col:
                st.markdown(f" {partida['descripcion'][:0]}...")
            
            with col:
                st.markdown(f"{partida['cantidad']} {partida['unidad']}")
            
            with col:
                if st.button("", key=f"del_partida_{i}"):
                    st.session_state.partidas_seleccionadas.pop(i)
                    st.rerun()


def render_work_summary() -> None:
    """Renderiza un resumen de los trabajos seleccionados."""
    partidas = st.session_state.get("partidas_seleccionadas", [])
    paquetes = st.session_state.get("paquetes_seleccionados", [])
    
    if not partidas and not paquetes:
        st.warning(" No has seleccionado ningún trabajo")
        return
    
    st.markdown("###  Resumen de trabajos")
    
    col, col = st.columns()
    
    with col:
        st.metric(" Paquetes", len(paquetes))
    
    with col:
        st.metric(" Partidas", len(partidas))
    
    if paquetes:
        st.markdown("**Paquetes:**")
        for pkg in paquetes:
            st.markdown(f"-  {PACKAGES_DATA[pkg]['nombre']}")
    
    if partidas:
        st.markdown("**Partidas individuales:**")
        for p in partidas:
            st.markdown(f"-  {p['descripcion'][:0]}... ({p['cantidad']} {p['unidad']})")


def clear_selections() -> None:
    """Limpia todas las selecciones."""
    st.session_state.partidas_seleccionadas = []
    st.session_state.paquetes_seleccionados = []