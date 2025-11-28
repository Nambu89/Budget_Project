"""
Auth Routes - Endpoints de autenticación.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from loguru import logger

from ....application.services.auth_service import get_auth_service

router = APIRouter()


# Schemas de Request
class RegisterRequest(BaseModel):
    """Request para registro de usuario."""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    nombre: str = Field(..., min_length=2, description="Nombre completo")
    telefono: Optional[str] = Field(None, description="Teléfono")
    empresa: Optional[str] = Field(None, description="Empresa")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "password": "mipassword123",
                "nombre": "Juan Pérez",
                "telefono": "600123456",
                "empresa": "Reformas JP"
            }
        }


class LoginRequest(BaseModel):
    """Request para login."""
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., description="Contraseña")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "usuario@example.com",
                "password": "mipassword123"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña."""
    email: EmailStr
    old_password: str
    new_password: str = Field(..., min_length=6)


# Schemas de Response
class UserResponse(BaseModel):
    """Response con datos del usuario."""
    id: str
    email: str
    nombre: str
    telefono: Optional[str]
    empresa: Optional[str]
    fecha_registro: str
    num_presupuestos: int


class AuthResponse(BaseModel):
    """Response de autenticación correcta."""
    message: str
    user: UserResponse
    token: str  # Por ahora fake, luego JWT real


# Endpoints
@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Registra un nuevo usuario.
    
    Args:
        request: Datos del usuario a registrar
        
    Returns:
        AuthResponse: Usuario creado y token
        
    Raises:
        HTTPException: Si el email ya existe
    """
    try:
        logger.info(f"Intento de registro: {request.email}")
        
        auth_service = get_auth_service()
        user = auth_service.register(
            email=request.email,
            password=request.password,
            nombre=request.nombre,
            telefono=request.telefono,
            empresa=request.empresa
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            telefono=user.telefono,
            empresa=user.empresa,
            fecha_registro=user.fecha_registro.isoformat(),
            num_presupuestos=user.num_presupuestos
        )
        
        logger.info(f"✓ Usuario registrado correctamente: {user.email}")
        
        return AuthResponse(
            message="Usuario registrado correctamente",
            user=user_response,
            token="fake-jwt-token-" + user.id  # TODO: Implementar JWT real
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error en registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Inicia sesión de usuario.
    
    Args:
        request: Credenciales del usuario
        
    Returns:
        AuthResponse: Usuario y token
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    try:
        logger.info(f"Intento de login: {request.email}")
        
        auth_service = get_auth_service()
        user = auth_service.login(request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos"
            )
        
        # Crear response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            telefono=user.telefono,
            empresa=user.empresa,
            fecha_registro=user.fecha_registro.isoformat(),
            num_presupuestos=user.num_presupuestos
        )
        
        logger.info(f"✓ Login correcto: {user.email}")
        
        return AuthResponse(
            message="Login correcto",
            user=user_response,
            token="fake-jwt-token-" + user.id  # TODO: Implementar JWT real
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error en login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(email: str):
    """
    Obtiene datos del usuario actual.
    
    Args:
        email: Email del usuario (por ahora, luego desde JWT)
        
    Returns:
        UserResponse: Datos del usuario
    """
    try:
        auth_service = get_auth_service()
        user = auth_service.get_user(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        
        return UserResponse(
            id=user.id,
            email=user.email,
            nombre=user.nombre,
            telefono=user.telefono,
            empresa=user.empresa,
            fecha_registro=user.fecha_registro.isoformat(),
            num_presupuestos=user.num_presupuestos
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error obteniendo usuario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


@router.post("/change-password")
async def change_password(request: ChangePasswordRequest):
    """
    Cambia la contraseña del usuario.
    
    Args:
        request: Email y contraseñas
        
    Returns:
        dict: Mensaje de confirmación
    """
    try:
        auth_service = get_auth_service()
        success = auth_service.change_password(
            request.email,
            request.old_password,
            request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña actual incorrecta"
            )
        
        logger.info(f"Contraseña cambiada: {request.email}")
        return {"message": "Contraseña cambiada correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error cambiando contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )


# ==========================================
# Recuperación de Contraseña
# ==========================================

@router.post("/request-password-reset")
async def request_password_reset(request: dict):
    """
    Solicita reset de contraseña.
    
    Genera un token y envía email con link de recuperación.
    """
    try:
        from ....application.services import get_email_service
        
        auth_service = get_auth_service()
        email_service = get_email_service()
        
        email = request.get('email')
        
        # Generar token
        token = auth_service.request_password_reset(email)
        
        if token:
            # Obtener datos del usuario
            user_data = auth_service.verify_reset_token(token)
            
            if user_data:
                # Generar link de reset
                reset_link = f"http://localhost:8501?reset_token={token}"
                
                # Enviar email
                try:
                    email_service.enviar_reset_password(
                        email_destinatario=email,
                        reset_link=reset_link,
                        nombre=user_data['nombre']
                    )
                except Exception as e:
                    logger.error(f"Error enviando email: {e}")
        
        # Siempre retornar el mismo mensaje (seguridad)
        return {
            "message": "Si el email existe, recibirás un link de recuperación",
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error en request_password_reset: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error procesando solicitud"
        )


@router.get("/verify-reset-token/{token}")
async def verify_reset_token(token: str):
    """
    Verifica si un token de reset es válido.
    """
    try:
        auth_service = get_auth_service()
        user_data = auth_service.verify_reset_token(token)
        
        if user_data:
            return {
                "valid": True,
                "email": user_data['email'],
                "nombre": user_data['nombre']
            }
        else:
            return {"valid": False}
            
    except Exception as e:
        logger.error(f"Error verificando token: {e}")
        return {"valid": False}


@router.post("/reset-password")
async def reset_password(request: dict):
    """
    Resetea la contraseña usando un token válido.
    """
    try:
        auth_service = get_auth_service()
        
        token = request.get('token')
        new_password = request.get('new_password')
        
        # Resetear contraseña
        success = auth_service.reset_password(token, new_password)
        
        if success:
            return {
                "message": "Contraseña actualizada correctamente",
                "success": True
            }
        else:
            raise HTTPException(
                status_code=400,
                detail="Error al resetear contraseña"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error en reset_password: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error procesando solicitud"
        )
