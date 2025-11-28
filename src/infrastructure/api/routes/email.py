"""
Endpoint para envío de presupuestos por email.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from loguru import logger

from src.application.services import get_email_service

router = APIRouter()


class EnviarEmailRequest(BaseModel):
    """Request para enviar presupuesto por email."""
    email_destinatario: EmailStr
    pdf_bytes: bytes
    datos_presupuesto: dict
    mensaje_personalizado: str | None = None


class EnviarEmailResponse(BaseModel):
    """Response del envío de email."""
    success: bool
    message: str


@router.post("/enviar", response_model=EnviarEmailResponse)
async def enviar_presupuesto_email(request: EnviarEmailRequest):
    """
    Envía un presupuesto por email con PDF adjunto.
    
    Args:
        request: Datos del email a enviar
        
    Returns:
        EnviarEmailResponse: Resultado del envío
    """
    try:
        email_service = get_email_service()
        
        success = email_service.enviar_presupuesto(
            email_destinatario=request.email_destinatario,
            pdf_bytes=request.pdf_bytes,
            datos_presupuesto=request.datos_presupuesto,
            mensaje_personalizado=request.mensaje_personalizado
        )
        
        if success:
            return EnviarEmailResponse(
                success=True,
                message=f"Presupuesto enviado correctamente a {request.email_destinatario}"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al enviar el email"
            )
            
    except Exception as e:
        logger.error(f"Error en endpoint enviar_presupuesto_email: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al enviar email: {str(e)}"
        )
