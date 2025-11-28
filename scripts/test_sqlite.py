"""
Script de prueba para verificar SQLite.
"""

import sys
import os
from pathlib import Path

# Añadir directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))
os.chdir(root_dir)

from src.application.services import get_auth_service


def test_sqlite():
    """Prueba el funcionamiento de SQLite."""
    print("=" * 60)
    print("🧪 Probando SQLite")
    print("=" * 60)
    
    auth = get_auth_service()
    
    # 1. Crear usuario de prueba
    print("\n1. Creando usuario de prueba...")
    try:
        user = auth.register(
            email="test@sqlite.com",
            password="test123",
            nombre="Usuario de Prueba SQLite",
            empresa="Test Corp"
        )
        print(f"   ✓ Usuario creado: {user['email']}")
    except ValueError as e:
        print(f"   ⊘ Usuario ya existe: {e}")
    
    # 2. Login
    print("\n2. Probando login...")
    try:
        logged_user = auth.login("test@sqlite.com", "test123")
        print(f"   ✓ Login correcto: {logged_user['nombre']}")
        print(f"   - ID: {logged_user['id']}")
        print(f"   - Email: {logged_user['email']}")
        print(f"   - Empresa: {logged_user.get('empresa', 'N/A')}")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # 3. Obtener usuario
    print("\n3. Obteniendo usuario por email...")
    user = auth.get_user_by_email("test@sqlite.com")
    if user:
        print(f"   ✓ Usuario encontrado: {user['nombre']}")
    else:
        print("   ✗ Usuario no encontrado")
        return False
    
    # 4. Listar todos los usuarios
    print("\n4. Listando todos los usuarios...")
    all_users = auth.get_all_users()
    print(f"   ✓ Total de usuarios: {len(all_users)}")
    
    for u in all_users[:5]:  # Mostrar primeros 5
        print(f"   - {u['email']} ({u['nombre']})")
    
    if len(all_users) > 5:
        print(f"   ... y {len(all_users) - 5} más")
    
    # 5. Cambiar contraseña
    print("\n5. Probando cambio de contraseña...")
    try:
        auth.change_password("test@sqlite.com", "test123", "newpass123")
        print("   ✓ Contraseña cambiada")
        
        # Verificar con nueva contraseña
        auth.login("test@sqlite.com", "newpass123")
        print("   ✓ Login con nueva contraseña ")
        
        # Restaurar contraseña original
        auth.change_password("test@sqlite.com", "newpass123", "test123")
        print("   ✓ Contraseña restaurada")
        
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Todas las pruebas pasaron")
    print("=" * 60)
    print("\n💡 SQLite está funcionando correctamente!")
    print("   - Base de datos: data/budget.db")
    print(f"   - Usuarios totales: {len(all_users)}")
    print("\n✅ Listo para producción")
    
    return True


if __name__ == "__main__":
    try:
        success = test_sqlite()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error en pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
