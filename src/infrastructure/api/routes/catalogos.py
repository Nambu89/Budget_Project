"""
Catalogos Routes - Endpoints para obtener catálogos de paquetes y categorías.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from ..schemas.response import PaquetesResponse, CategoriasResponse, PaqueteInfo, CategoriaInfo
from ....config.pricing_data import get_todos_paquetes, get_todas_categorias, PACKAGES_DATA, PRICING_DATA

router = APIRouter()


@router.get("/paquetes", response_model=PaquetesResponse)
async def obtener_paquetes(pais: str = "ES"):
    """
    Obtiene la lista de paquetes disponibles.
    
    Args:
        pais: Código del país (ES, FR, etc.)
    
    Returns:
        Lista de paquetes con sus precios y descripciones
    """
    try:
        logger.info(f"Obteniendo paquetes para país: {pais}")
        
        # PACKAGES_DATA es un dict plano {paquete_id: datos}
        paquetes = []
        for paquete_id, datos in PACKAGES_DATA.items():
            paquete_info = PaqueteInfo(
                id=paquete_id,
                nombre=datos.get("nombre", ""),
                descripcion=datos.get("descripcion", ""),
                incluye=datos.get("incluye", []),
                precios=datos.get("precios", {})
            )
            paquetes.append(paquete_info)
        
        logger.info(f"Encontrados {len(paquetes)} paquetes")
        
        return PaquetesResponse(
            paquetes=paquetes,
            total=len(paquetes)
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo paquetes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categorias", response_model=CategoriasResponse)
async def obtener_categorias(pais: str = "ES"):
    """
    Obtiene la lista de categorías de trabajo disponibles.
    
    Args:
        pais: Código del país (ES, FR, etc.)
    
    Returns:
        Lista de categorías con sus partidas
    """
    try:
        logger.info(f"Obteniendo categorías para país: {pais}")
        
        # Obtener todas las categorías directamente del dict de precios
        categorias = []
        for cat_id, datos in PRICING_DATA.items():
            categoria_info = CategoriaInfo(
                id=cat_id,
                nombre=cat_id.replace("_", " ").title(),
                icono={"albanileria": "🧱", "fontaneria": "🚿", "electricidad": "⚡", "cocina": "🍳", "carpinteria": "🚪"}.get(cat_id, "🔧"),
                partidas=list(datos.keys())
            )
            categorias.append(categoria_info)
        
        logger.info(f"Encontradas {len(categorias)} categorías")
        
        return CategoriasResponse(
            categorias=categorias,
            total=len(categorias)
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paises")
async def obtener_paises():
    """
    Obtiene la lista de países disponibles.
    
    Returns:
        Lista de países soportados
    """
    return {
        "paises": [
            {"codigo": "ES", "nombre": "España", "disponible": True},
            {"codigo": "FR", "nombre": "Francia", "disponible": False},
        ]
    }
