"""
FastAPI Main Application.

API REST para la calculadora de presupuestos de reformas.
Expone el motor de cálculo vía HTTP para consumo desde cualquier frontend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Crear aplicación FastAPI
app = FastAPI(
    title="API Calculadora de Presupuestos",
    description="API REST para cálculo de presupuestos de reformas de construcción",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS para permitir acceso desde web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Importar routers
from .routes import catalogos, presupuesto, auth

# Registrar routers
app.include_router(
    catalogos.router,
    prefix="/api/v1/catalogos",
    tags=["Catálogos"]
)

app.include_router(
    presupuesto.router,
    prefix="/api/v1/presupuesto",
    tags=["Presupuestos"]
)

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["Autenticación"]
)


@app.get("/", tags=["Health"])
def root():
    """Endpoint raíz - health check."""
    return {
        "status": "ok",
        "message": "API Calculadora de Presupuestos",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Event handlers
@app.on_event("startup")
async def startup_event():
    """Ejecutar al iniciar la aplicación."""
    logger.info("=" * 50)
    logger.info("🚀 API Calculadora de Presupuestos - Iniciando...")
    logger.info("=" * 50)
    logger.info("Docs disponibles en: /docs")
    logger.info("ReDoc disponibles en: /redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """Ejecutar al cerrar la aplicación."""
    logger.info("API Calculadora de Presupuestos - Cerrando...")
