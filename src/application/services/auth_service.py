"""
Servicio de autenticación actualizado para usar SQLite con SQLAlchemy.
"""

import hashlib
from datetime import datetime
from typing import Optional, Dict
from loguru import logger

from src.infrastructure.database import get_db_session
from src.infrastructure.database.models import User as UserModel


class AuthService:
    """
    Servicio de autenticación usando SQLite.
    
    Gestiona registro, login y gestión de usuarios con SQLAlchemy.
    """
    
    def __init__(self):
        """Inicializa el servicio de autenticación."""
        logger.info("✓ AuthService inicializado con SQLite")
    
    def _hash_password(self, password: str) -> str:
        """Hash de contraseña con SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return self._hash_password(password) == password_hash
    
    def register(
        self,
        email: str,
        password: str,
        nombre: str,
        telefono: Optional[str] = None,
        empresa: Optional[str] = None
    ) -> Dict:
        """
        Registra un nuevo usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            nombre: Nombre completo
            telefono: Teléfono opcional
            empresa: Empresa opcional
            
        Returns:
            dict: Datos del usuario creado
            
        Raises:
            ValueError: Si el email ya está registrado
        """
        with get_db_session() as session:
            # Verificar si ya existe
            existing = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            if existing:
                raise ValueError(f"El email {email} ya está registrado")
            
            # Crear usuario
            user = UserModel(
                email=email.lower(),
                nombre=nombre,
                password_hash=self._hash_password(password),
                telefono=telefono,
                empresa=empresa,
                fecha_registro=datetime.utcnow(),
                activo=True,
                num_presupuestos=0
            )
            
            session.add(user)
            session.commit()
            
            logger.info(f"✓ Usuario registrado: {email}")
            return user.to_dict()
    
    def login(self, email: str, password: str) -> Dict:
        """
        Autentica un usuario.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            dict: Datos del usuario autenticado
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            if not user:
                raise ValueError("Credenciales inválidas")
            
            if not self._verify_password(password, user.password_hash):
                raise ValueError("Credenciales inválidas")
            
            if not user.activo:
                raise ValueError("Usuario inactivo")
            
            # Actualizar último acceso
            user.ultimo_acceso = datetime.utcnow()
            session.commit()
            
            logger.info(f"✓ Login correcto: {email}")
            return user.to_dict()
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """
        Obtiene un usuario por email.
        
        Args:
            email: Email del usuario
            
        Returns:
            dict: Datos del usuario o None
        """
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            return user.to_dict() if user else None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """
        Obtiene un usuario por ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            dict: Datos del usuario o None
        """
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(id=user_id).first()
            return user.to_dict() if user else None

    def refresh_user_data(self, user_id: str) -> Optional[Dict]:
        """
        Refresca los datos del usuario desde la BD.
        
        Útil después de operaciones que modifican el usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            dict: Datos actualizados del usuario
        """
        logger.debug(f"Refrescando datos del usuario: {user_id}")
        return self.get_user_by_id(user_id)
    
    def change_password(
        self,
        email: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            email: Email del usuario
            old_password: Contraseña actual
            new_password: Nueva contraseña
            
        Returns:
            bool: True si se cambió correctamente
            
        Raises:
            ValueError: Si la contraseña actual es incorrecta
        """
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            if not user:
                raise ValueError("Usuario no encontrado")
            
            if not self._verify_password(old_password, user.password_hash):
                raise ValueError("Contraseña actual incorrecta")
            
            user.password_hash = self._hash_password(new_password)
            session.commit()
            
            logger.info(f"✓ Contraseña cambiada: {email}")
            return True
    
    def get_all_users(self) -> list[Dict]:
        """
        Obtiene todos los usuarios (admin).
        
        Returns:
            list: Lista de usuarios
        """
        with get_db_session() as session:
            users = session.query(UserModel).all()
            return [user.to_dict() for user in users]
    
    def increment_presupuestos(self, email: str) -> None:
        """
        Incrementa el contador de presupuestos de un usuario.
        
        Args:
            email: Email del usuario
        """
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            if user:
                user.num_presupuestos += 1
                session.commit()
    
    # ==========================================
    # Recuperación de Contraseña
    # ==========================================
    
    def request_password_reset(self, email: str) -> Optional[str]:
        """
        Solicita reset de contraseña para un usuario.
        
        1. Verifica que el usuario existe
        2. Genera token único
        3. Guarda en BD con expiración (1 hora)
        4. Retorna token para enviar por email
        
        Args:
            email: Email del usuario
            
        Returns:
            str: Token generado si el usuario existe, None si no
        """
        from src.infrastructure.database.models import PasswordResetToken
        
        with get_db_session() as session:
            # Buscar usuario
            user = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            if not user:
                # No revelar si el email existe o no (seguridad)
                logger.warning(f"Intento de reset para email no existente: {email}")
                return None
            
            # Invalidar tokens anteriores del usuario
            old_tokens = session.query(PasswordResetToken).filter_by(
                user_id=user.id,
                used=False
            ).all()
            
            for token in old_tokens:
                token.mark_as_used()
            
            # Crear nuevo token
            reset_token = PasswordResetToken.create_token(user.id)
            session.add(reset_token)
            session.commit()
            
            logger.info(f"✓ Token de reset creado para: {email}")
            return reset_token.token
    
    def verify_reset_token(self, token: str) -> Optional[Dict]:
        """
        Verifica si un token de reset es válido.
        
        Args:
            token: Token a verificar
            
        Returns:
            dict: Datos del usuario si válido, None si no
        """
        from src.infrastructure.database.models import PasswordResetToken
        
        with get_db_session() as session:
            reset_token = session.query(PasswordResetToken).filter_by(
                token=token
            ).first()
            
            if not reset_token:
                return None
            
            if not reset_token.is_valid():
                return None
            
            # Obtener usuario
            user = session.query(UserModel).filter_by(
                id=reset_token.user_id
            ).first()
            
            if not user:
                return None
            
            return {
                "user_id": user.id,
                "email": user.email,
                "nombre": user.nombre
            }
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """
        Resetea la contraseña usando un token válido.
        
        Args:
            token: Token de reset
            new_password: Nueva contraseña
            
        Returns:
            bool: True si exitoso, False si no
            
        Raises:
            ValueError: Si el token es inválido o expirado
        """
        from src.infrastructure.database.models import PasswordResetToken
        
        with get_db_session() as session:
            # Verificar token
            reset_token = session.query(PasswordResetToken).filter_by(
                token=token
            ).first()
            
            if not reset_token:
                raise ValueError("Token inválido")
            
            if not reset_token.is_valid():
                raise ValueError("Token expirado o ya usado")
            
            # Obtener usuario
            user = session.query(UserModel).filter_by(
                id=reset_token.user_id
            ).first()
            
            if not user:
                raise ValueError("Usuario no encontrado")
            
            # Cambiar contraseña
            user.password_hash = self._hash_password(new_password)
            
            # Marcar token como usado
            reset_token.mark_as_used()
            
            session.commit()
            
            logger.info(f"✓ Contraseña reseteada para: {user.email}")
            return True


# Singleton
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """
    Obtiene instancia singleton del servicio de autenticación.
    
    Returns:
        AuthService: Instancia única
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
