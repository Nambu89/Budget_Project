"""
Script para ejecutar la API REST.

Uso:
    python run_api.py
"""

import uvicorn
from loguru import logger

if __name__ == "__main__":
    logger.info("Iniciando API REST...")
    logger.info("Documentación disponible en: http://localhost:8000/docs")
    logger.info("ReDoc disponible en: http://localhost:8000/redoc")
    logger.info("")
    logger.info("Presiona Ctrl+C para detener")
    logger.info("=" * 50)
    
    uvicorn.run(
        "src.infrastructure.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en desarrollo
        log_level="info"
    )
