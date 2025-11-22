"""
Budget Calculator - Entry Point.

Punto de entrada principal para la aplicación de
calculadora de presupuestos de reforma.

Uso:
    streamlit run main.py
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from loguru import logger

import streamlit as st

from src.config.settings import settings
from src.application.presentation.streamlit_app import main


def configure_logging() -> None:
    """Configura el sistema de logging."""
    # Remover handler por defecto
    logger.remove()
    
    # Formato del log
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Añadir handler de consola
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if settings.debug else "INFO",
        colorize=True,
    )
    
    # Añadir handler de archivo en producción
    if settings.environment == "production":
        logger.add(
            "logs/budget_calculator.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            retention="7 days",
            compression="gz",
        )
    
    logger.info(f"Logging configurado - Nivel: {'DEBUG' if settings.debug else 'INFO'}")


def check_configuration() -> bool:
    """
    Verifica que la configuración sea correcta.
    
    Returns:
        bool: True si la configuración es válida
    """
    errores = []
    
    # Verificar proveedor LLM
    if settings.llm_provider == "azure":
        if not settings.is_azure_configured():
            errores.append(
                "Azure OpenAI seleccionado pero faltan variables: "
                "AZURE_OPENAI_ENDPOINT y/o AZURE_OPENAI_API_KEY"
            )
    elif settings.llm_provider == "openai":
        if not settings.is_openai_configured():
            errores.append(
                "OpenAI seleccionado pero falta: OPENAI_API_KEY"
            )
    
    # Mostrar errores si existen
    if errores:
        logger.error("❌ Errores de configuración:")
        for error in errores:
            logger.error(f"  - {error}")
        logger.error("Revisa tu archivo .env")
        return False
    
    # Mostrar configuración activa
    logger.info("✓ Configuración válida")
    logger.info(f"  - Entorno: {settings.environment}")
    logger.info(f"  - LLM Provider: {settings.llm_provider}")
    logger.info(f"  - Debug: {settings.debug}")
    logger.info(f"  - IVA General: {settings.iva_general}%")
    logger.info(f"  - IVA Reducido: {settings.iva_reducido}%")
    logger.info(f"  - Markup partidas: {settings.markup_partidas_individuales}%")
    logger.info(f"  - Redondeo: {settings.redondeo_alza}%")
    
    return True


def run() -> None:
    """Ejecuta la aplicación."""
    # Configurar logging solo una vez por sesión
    if "logging_configured" not in st.session_state:
        configure_logging()
        st.session_state.logging_configured = True
        
        logger.info("=" * 50)
        logger.info("🏗️ Budget Calculator - Iniciando...")
        logger.info("=" * 50)
        
        # Verificar configuración
        if not check_configuration():
            logger.warning("⚠️ La aplicación se ejecutará pero algunas funciones pueden fallar")
    
    # Ejecutar aplicación Streamlit
    try:
        main()
    except Exception as e:
        logger.exception(f"Error fatal: {e}")
        raise


# Entry point
if __name__ == "__main__":
    run()