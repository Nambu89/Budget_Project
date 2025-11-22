"""
Componente Customer Form para Streamlit.

Formulario para capturar los datos del cliente
al final del proceso de presupuesto.
"""

import streamlit as st
from typing import Optional
import re


def render_customer_form() -> Optional[dict]:
    """
    Renderiza el formulario de datos del cliente.
    
    Returns:
        dict: Datos del cliente o None si no está completo
    """
    st.markdown("### 👤 Tus datos de contacto")
    
    st.info("""
        📋 **¿Por qué pedimos tus datos?**
        
        Para enviarte el presupuesto completo en PDF y poder 
        contactarte para concertar una visita técnica si lo deseas.
    """)
    
    # Formulario
    with st.form("customer_form"):
        # Nombre
        nombre = st.text_input(
            "Nombre completo *",
            placeholder="Ej: Juan García López",
            help="Tu nombre completo para el presupuesto",
        )
        
        # Email
        email = st.text_input(
            "Email *",
            placeholder="Ej: juan@email.com",
            help="Te enviaremos el presupuesto a este email",
        )
        
        # Teléfono
        telefono = st.text_input(
            "Teléfono *",
            placeholder="Ej: 612 345 678",
            help="Para contactarte sobre el presupuesto",
        )
        
        st.divider()
        
        # Dirección de la obra (opcional)
        direccion = st.text_input(
            "Dirección de la obra (opcional)",
            placeholder="Ej: Calle Mayor 123, Madrid",
            help="Donde se realizará la reforma",
        )
        
        # Notas adicionales
        notas = st.text_area(
            "Notas adicionales (opcional)",
            placeholder="Ej: Preferiblemente contactar por las tardes...",
            help="Cualquier información adicional que quieras añadir",
            max_chars=500,
        )
        
        st.divider()
        
        # Aceptación RGPD
        acepta_rgpd = st.checkbox(
            "Acepto el tratamiento de mis datos según la política de privacidad *",
            help="Requerido para procesar tu solicitud",
        )
        
        # Logo del cliente (monetización)
        st.markdown("#### 💼 ¿Quieres tu logo en el presupuesto?")
        
        logo_file = st.file_uploader(
            "Sube tu logo (opcional - característica premium)",
            type=["png", "jpg", "jpeg"],
            help="Añade tu logo corporativo al presupuesto",
        )
        
        # Botón submit
        submitted = st.form_submit_button(
            "✅ Generar presupuesto",
            type="primary",
            use_container_width=True,
        )
        
        if submitted:
            # Validaciones
            errores = []
            
            if not nombre or len(nombre.strip()) < 2:
                errores.append("El nombre es obligatorio")
            
            if not email or not _validar_email(email):
                errores.append("Email no válido")
            
            if not telefono or not _validar_telefono(telefono):
                errores.append("Teléfono no válido (formato español)")
            
            if not acepta_rgpd:
                errores.append("Debes aceptar la política de privacidad")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
                return None
            
            # Procesar logo si existe
            logo_path = None
            if logo_file:
                # En producción guardaríamos el archivo
                # Por ahora solo indicamos que existe
                logo_path = f"uploads/{logo_file.name}"
                st.info(f"Logo recibido: {logo_file.name}")
            
            return {
                "nombre": nombre.strip(),
                "email": email.strip().lower(),
                "telefono": _normalizar_telefono(telefono),
                "direccion_obra": direccion.strip() if direccion else None,
                "notas": notas.strip() if notas else None,
                "logo_path": logo_path,
            }
    
    return None


def render_customer_summary(datos: dict) -> None:
    """
    Renderiza un resumen de los datos del cliente.
    
    Args:
        datos: Datos del cliente
    """
    st.markdown("### 👤 Datos del cliente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Nombre:** {datos['nombre']}")
        st.markdown(f"**Email:** {datos['email']}")
        st.markdown(f"**Teléfono:** {datos['telefono']}")
    
    with col2:
        if datos.get('direccion_obra'):
            st.markdown(f"**Dirección:** {datos['direccion_obra']}")
        if datos.get('notas'):
            st.markdown(f"**Notas:** {datos['notas'][:50]}...")


def render_quick_customer_form() -> Optional[dict]:
    """
    Renderiza un formulario rápido de cliente (inline).
    
    Returns:
        dict: Datos del cliente o None
    """
    st.markdown("### 📝 Datos para el presupuesto")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nombre = st.text_input(
            "Nombre *",
            key="quick_nombre",
            placeholder="Tu nombre",
        )
    
    with col2:
        email = st.text_input(
            "Email *",
            key="quick_email",
            placeholder="tu@email.com",
        )
    
    with col3:
        telefono = st.text_input(
            "Teléfono *",
            key="quick_telefono",
            placeholder="612345678",
        )
    
    # Validación inline
    if nombre and email and telefono:
        if _validar_email(email) and _validar_telefono(telefono):
            return {
                "nombre": nombre.strip(),
                "email": email.strip().lower(),
                "telefono": _normalizar_telefono(telefono),
            }
        else:
            st.warning("⚠️ Revisa el email y teléfono")
    
    return None


def _validar_email(email: str) -> bool:
    """Valida formato de email."""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, email))


def _validar_telefono(telefono: str) -> bool:
    """Valida formato de teléfono español."""
    # Limpiar
    telefono_limpio = re.sub(r'[\s\-\.\(\)]', '', telefono)
    
    # Quitar prefijo si existe
    if telefono_limpio.startswith('+34'):
        telefono_limpio = telefono_limpio[3:]
    elif telefono_limpio.startswith('0034'):
        telefono_limpio = telefono_limpio[4:]
    
    # Validar 9 dígitos empezando por 6, 7, 8 o 9
    patron = r'^[6789]\d{8}$'
    return bool(re.match(patron, telefono_limpio))


def _normalizar_telefono(telefono: str) -> str:
    """Normaliza el teléfono al formato estándar."""
    telefono_limpio = re.sub(r'[\s\-\.\(\)]', '', telefono)
    
    if telefono_limpio.startswith('+34'):
        return telefono_limpio
    elif telefono_limpio.startswith('0034'):
        return '+34' + telefono_limpio[4:]
    else:
        return '+34' + telefono_limpio