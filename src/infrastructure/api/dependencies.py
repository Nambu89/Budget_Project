"""
Dependencias de FastAPI — autenticación JWT.
"""

from fastapi import Header, HTTPException, status
import jwt
from loguru import logger

from ...config.settings import settings

ALGORITHM = "HS256"


def create_jwt_token(user_id: str, email: str) -> str:
    """
    Genera un JWT firmado con la secret_key del proyecto.

    Args:
        user_id: ID del usuario
        email: Email del usuario

    Returns:
        str: Token JWT codificado
    """
    from datetime import datetime, timedelta, timezone

    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def get_current_user_id(authorization: str = Header(..., description="Bearer <token>")) -> str:
    """
    FastAPI dependency que extrae y valida el JWT del header Authorization.

    Args:
        authorization: Header con formato 'Bearer <token>'

    Returns:
        str: user_id extraído del token

    Raises:
        HTTPException 401: Si el token es inválido, expirado o ausente
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de autorización inválido. Use: Bearer <token>",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: falta user_id",
            )
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token JWT inválido: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
