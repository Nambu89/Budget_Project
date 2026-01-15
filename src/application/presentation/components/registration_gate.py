"""
Registration Gate Component - Puerta de registro para ver presupuesto.

Muestra un teaser del presupuesto con rango de precios y
requiere registro/login para ver el valor exacto.
"""

import streamlit as st
from loguru import logger

from ...services.auth_service import get_auth_service


def render_registration_gate(presupuesto) -> bool:
    """
    Renderiza la puerta de registro con teaser de rango de precios.
    
    Muestra:
    - Rango de precios estimado (±15% del total real)
    - Call to action para registro
    - Formulario de login/registro inline
    
    Args:
        presupuesto: Presupuesto calculado (con el total real)
        
    Returns:
        bool: True si el usuario se autenticó, False si no
    """
    # Calcular rango de precios (±15%)
    total_real = presupuesto.total
    precio_min = total_real * 0.97
    precio_max = total_real * 1.03
    
    # Container principal con estilo
    st.markdown("""
        <style>
        .registration-gate {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            color: white;
            margin: 2rem 0;
        }
        .price-range {
            font-size: 2rem;
            font-weight: bold;
            margin: 1rem 0;
        }
        .benefits-list {
            text-align: left;
            margin: 1.5rem auto;
            max-width: 400px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Mensaje principal
    st.markdown("## Tu presupuesto está listo")
    
    st.markdown("---")
    
    # Rango de precios destacado
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            ### Tu reforma costará entre
            ## {precio_min:,.0f}€ y {precio_max:,.0f}€
        """.replace(",", "."))
    
    st.markdown("---")
    
    # Beneficios de registrarse
    st.markdown("""
        ### Regístrate **GRATIS** para:
        
        - **Ver el precio exacto** de tu reforma  
        - **Descargar PDF profesional** con desglose completo  
        - **Guardar y comparar** todos tus presupuestos  
        - **Recibir ofertas** exclusivas de proveedores  
    """)
    
    st.markdown("---")
    
    # Tabs para Login y Registro
    tab1, tab2 = st.tabs(["Registrarme", "Ya tengo cuenta"])
    
    with tab1:
        _render_inline_register_form()
    
    with tab2:
        _render_inline_login_form()
    
    # Verificar si se autenticó
    return st.session_state.get("authenticated", False)


def _render_inline_register_form():
    """Formulario de registro inline simplificado."""
    with st.form("gate_register_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(
                "Nombre *",
                placeholder="Tu nombre",
                key="gate_reg_nombre"
            )
        
        with col2:
            email = st.text_input(
                "Email *",
                placeholder="tu@email.com",
                key="gate_reg_email"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            password = st.text_input(
                "Contraseña *",
                type="password",
                placeholder="Mínimo 6 caracteres",
                key="gate_reg_password"
            )
        
        with col4:
            telefono = st.text_input(
                "Teléfono (opcional)",
                placeholder="600123456",
                key="gate_reg_telefono"
            )
        
        submitted = st.form_submit_button(
            "Registrarme y ver mi presupuesto",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not nombre or not email or not password:
                st.error("Por favor completa los campos obligatorios (*)")
                return
            
            if len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
                return
            
            try:
                auth_service = get_auth_service()
                user = auth_service.register(
                    email=email,
                    password=password,
                    nombre=nombre,
                    telefono=telefono if telefono else None,
                )
                
                if user:
                    # Auto-login tras registro
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    
                    st.success("Cuenta creada! Cargando tu presupuesto...")
                    logger.info(f"Usuario registrado desde gate: {user['email']}")
                    st.rerun()
                else:
                    st.error("No se pudo crear la cuenta")
                    
            except ValueError as e:
                st.error(f"{str(e)}")
            except Exception as e:
                logger.error(f"Error en registro gate: {e}")
                st.error("Error al crear la cuenta. Inténtalo de nuevo.")


def _render_inline_login_form():
    """Formulario de login inline simplificado."""
    with st.form("gate_login_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            email = st.text_input(
                "Email",
                placeholder="tu@email.com",
                key="gate_login_email"
            )
        
        with col2:
            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Tu contraseña",
                key="gate_login_password"
            )
        
        submitted = st.form_submit_button(
            "Entrar y ver mi presupuesto",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            if not email or not password:
                st.error("Por favor completa todos los campos")
                return
            
            try:
                auth_service = get_auth_service()
                user = auth_service.login(email, password)
                
                if user:
                    st.session_state.user = user
                    st.session_state.authenticated = True
                    
                    st.success(f"Bienvenido {user['nombre']}! Cargando tu presupuesto...")
                    logger.info(f"Usuario logueado desde gate: {user['email']}")
                    st.rerun()
                else:
                    st.error("Email o contraseña incorrectos")
                    
            except ValueError as e:
                st.error(f"{str(e)}")
            except Exception as e:
                logger.error(f"Error en login gate: {e}")
                st.error("Error al iniciar sesión. Inténtalo de nuevo.")
