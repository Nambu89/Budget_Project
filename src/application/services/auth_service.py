"""
Servicio de autenticación con medidas de seguridad mejoradas.
"""

import hashlib
import re
from datetime import datetime, timedelta
from typing import Optional, Dict
from collections import defaultdict
from loguru import logger

from src.infrastructure.database import get_db_session
from src.infrastructure.database.models import User as UserModel
from src.infrastructure.logging.metrics import metrics


class AuthService:
    """
    Servicio de autenticación usando SQLite con seguridad mejorada.
    
    Implementa:
    - Rate limiting en login
    - Validación de email
    - Hashing seguro de contraseñas
    - Logging sin datos sensibles
    - Métricas de negocio
    """
    
    def __init__(self):
        """Inicializa el servicio de autenticación."""
        # Rate limiting
        self.login_attempts = defaultdict(list)
        self.MAX_ATTEMPTS = 5
        self.LOCKOUT_MINUTES = 15
        
        logger.info("AuthService inicializado con SQLite")
    
    def _hash_password(self, password: str) -> str:
        """
        Hash de contraseña con SHA-256.
        
        NOTA: En producción considerar bcrypt o argon2.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return self._hash_password(password) == password_hash
    
    def _validate_email(self, email: str) -> bool:
        """
        Valida formato de email.
        
        Args:
            email: Email a validar
            
        Returns:
            bool: True si el formato es válido
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _check_rate_limit(self, email: str) -> bool:
        """
        Verifica rate limiting para prevenir fuerza bruta.
        
        Args:
            email: Email del usuario
            
        Returns:
            bool: True si puede intentar login
        """
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.LOCKOUT_MINUTES)
        
        # Limpiar intentos antiguos
        self.login_attempts[email] = [
            t for t in self.login_attempts[email] if t > cutoff
        ]
        
        # Verificar límite
        if len(self.login_attempts[email]) >= self.MAX_ATTEMPTS:
            logger.warning(f"Rate limit excedido para: {email}")
            
            # Métrica de seguridad
            metrics.log_event(
                "RATE_LIMIT_EXCEEDED",
                email=email,
                attempts=len(self.login_attempts[email])
            )
            
            return False
        
        return True
    
    def _sanitize_input(self, text: str) -> str:
        """
        Sanitiza inputs de usuario para prevenir XSS.
        
        Args:
            text: Texto a sanitizar
            
        Returns:
            str: Texto sanitizado
        """
        import html
        return html.escape(text.strip()) if text else ""
    
    def register(
        self,
        email: str,
        password: str,
        nombre: str,
        telefono: Optional[str] = None,
        empresa: Optional[str] = None
    ) -> Dict:
        """
        Registra un nuevo usuario con validaciones de seguridad.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            nombre: Nombre completo
            telefono: Teléfono opcional
            empresa: Empresa opcional
            
        Returns:
            dict: Datos del usuario creado
            
        Raises:
            ValueError: Si hay errores de validación
        """
        # Validar email
        if not self._validate_email(email):
            raise ValueError("Formato de email inválido")
        
        # Validar contraseña
        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        # Sanitizar inputs
        email = email.lower().strip()
        nombre = self._sanitize_input(nombre)
        empresa = self._sanitize_input(empresa) if empresa else None
        
        with get_db_session() as session:
            # Verificar si ya existe
            existing = session.query(UserModel).filter_by(email=email).first()
            
            if existing:
                raise ValueError(f"El email {email} ya está registrado")
            
            # Crear usuario
            user = UserModel(
                email=email,
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
            
            # Métrica de negocio
            metrics.log_event(
                "USER_REGISTERED",
                user_id=user.id,
                email=email,
                nombre=nombre,
                empresa=empresa or "N/A"
            )
            
            # SEGURIDAD: No loguear datos sensibles
            logger.info(f"Usuario registrado: {email}")
            return user.to_dict()
    
    def login(self, email: str, password: str) -> Dict:
        """
        Autentica un usuario con rate limiting.
        
        Args:
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            dict: Datos del usuario autenticado
            
        Raises:
            ValueError: Si las credenciales son inválidas o rate limit excedido
        """
        email = email.lower().strip()
        
        # SEGURIDAD: Rate limiting
        if not self._check_rate_limit(email):
            raise ValueError(
                f"Demasiados intentos fallidos. "
                f"Intenta de nuevo en {self.LOCKOUT_MINUTES} minutos"
            )
        
        # Registrar intento
        self.login_attempts[email].append(datetime.now())
        
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(email=email).first()
            
            if not user:
                # Métrica de fallo de login
                metrics.log_event(
                    "LOGIN_FAILED",
                    email=email,
                    reason="user_not_found"
                )
                
                # SEGURIDAD: Mensaje genérico para no revelar si el email existe
                raise ValueError("Credenciales inválidas")
            
            if not self._verify_password(password, user.password_hash):
                # Métrica de fallo de login
                metrics.log_event(
                    "LOGIN_FAILED",
                    user_id=user.id,
                    email=email,
                    reason="wrong_password"
                )
                
                raise ValueError("Credenciales inválidas")
            
            if not user.activo:
                # Métrica de fallo de login
                metrics.log_event(
                    "LOGIN_FAILED",
                    user_id=user.id,
                    email=email,
                    reason="user_inactive"
                )
                
                raise ValueError("Usuario inactivo")
            
            # Limpiar intentos fallidos después de login exitoso
            self.login_attempts[email] = []
            
            # Actualizar último acceso
            user.ultimo_acceso = datetime.utcnow()
            session.commit()
            
            # Métrica de login exitoso
            metrics.log_event(
                "USER_LOGIN",
                user_id=user.id,
                email=email,
                num_presupuestos=user.num_presupuestos
            )
            
            # SEGURIDAD: No loguear datos sensibles
            logger.info(f"Login correcto: {email}")
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
        
        Args:
            user_id: ID del usuario
            
        Returns:
            dict: Datos actualizados del usuario
        """
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
        # Validar nueva contraseña
        if len(new_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
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
            
            # Métrica de cambio de contraseña
            metrics.log_event(
                "PASSWORD_CHANGED",
                user_id=user.id,
                email=email
            )
            
            logger.info(f"Contraseña cambiada: {email}")
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
        
        Args:
            email: Email del usuario
            
        Returns:
            str: Token generado si el usuario existe, None si no
        """
        from src.infrastructure.database.models import PasswordResetToken
        
        with get_db_session() as session:
            user = session.query(UserModel).filter_by(
                email=email.lower()
            ).first()
            
            if not user:
                # SEGURIDAD: No revelar si el email existe
                logger.warning(f"Intento de reset para email no existente: {email}")
                
                # Métrica de seguridad
                metrics.log_event(
                    "PASSWORD_RESET_REQUEST_FAILED",
                    email=email,
                    reason="user_not_found"
                )
                
                return None
            
            # Invalidar tokens anteriores
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
            
            # Métrica de solicitud de reset
            metrics.log_event(
                "PASSWORD_RESET_REQUESTED",
                user_id=user.id,
                email=email
            )
            
            logger.info(f"Token de reset creado para: {email}")
            return reset_token.token
    
    def verify_reset_token(self, token: str) -> Optional[Dict]:
        """Verifica si un token de reset es válido."""
        from src.infrastructure.database.models import PasswordResetToken
        
        with get_db_session() as session:
            reset_token = session.query(PasswordResetToken).filter_by(
                token=token
            ).first()
            
            if not reset_token or not reset_token.is_valid():
                return None
            
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
        """Resetea la contraseña usando un token válido."""
        from src.infrastructure.database.models import PasswordResetToken
        
        # Validar nueva contraseña
        if len(new_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        with get_db_session() as session:
            reset_token = session.query(PasswordResetToken).filter_by(
                token=token
            ).first()
            
            if not reset_token:
                raise ValueError("Token inválido")
            
            if not reset_token.is_valid():
                raise ValueError("Token expirado o ya usado")
            
            user = session.query(UserModel).filter_by(
                id=reset_token.user_id
            ).first()
            
            if not user:
                raise ValueError("Usuario no encontrado")
            
            user.password_hash = self._hash_password(new_password)
            reset_token.mark_as_used()
            session.commit()
            
            # Métrica de reset exitoso
            metrics.log_event(
                "PASSWORD_RESET_COMPLETED",
                user_id=user.id,
                email=user.email
            )
            
            logger.info(f"Contraseña reseteada para: {user.email}")
            return True


# Singleton
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Obtiene instancia singleton del servicio de autenticación."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service