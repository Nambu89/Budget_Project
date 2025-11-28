"""
User Budget Service - Servicio para gestión de presupuestos de usuario.
"""

from typing import List, Optional, Dict
from loguru import logger
import json

from ...infrastructure.database import get_db_session
from ...infrastructure.database.models import Budget as BudgetModel
from ...domain.models import Budget, Project, BudgetItem, Customer
from ...domain.enums import PropertyType, QualityLevel, WorkCategory


class UserBudgetService:
    """
    Servicio para gestionar presupuestos de un usuario.
    
    Permite listar, obtener y gestionar los presupuestos guardados.
    """
    
    def __init__(self):
        """Inicializa el servicio."""
        logger.info("✓ UserBudgetService inicializado")
    
    def get_user_budgets(
        self, 
        user_id: str, 
        limit: int = 50,
        offset: int = 0,
        only_active: bool = True
    ) -> List[Dict]:
        """
        Obtiene los presupuestos de un usuario.
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de resultados
            offset: Offset para paginación
            only_active: Si solo mostrar presupuestos activos
            
        Returns:
            List[Dict]: Lista de presupuestos
        """
        with get_db_session() as session:
            query = session.query(BudgetModel).filter_by(user_id=user_id)
            
            if only_active:
                query = query.filter_by(activo=True)
            
            # Ordenar por fecha de creación (más recientes primero)
            query = query.order_by(BudgetModel.fecha_creacion.desc())
            
            # Aplicar paginación
            budgets = query.limit(limit).offset(offset).all()
            
            return [budget.to_dict() for budget in budgets]
    
    def get_budget_by_id(self, budget_id: str, user_id: str) -> Optional[Dict]:
        """
        Obtiene un presupuesto específico por ID.
        
        Args:
            budget_id: ID del presupuesto
            user_id: ID del usuario (validación de pertenencia)
            
        Returns:
            Dict: Presupuesto o None
        """
        with get_db_session() as session:
            budget = session.query(BudgetModel).filter_by(
                id=budget_id,
                user_id=user_id
            ).first()
            
            return budget.to_dict() if budget else None
    
    def reconstruct_budget_object(self, budget_data: Dict) -> Budget:
        """
        Reconstruye un objeto Budget desde los datos de BD.
        
        Args:
            budget_data: Datos del presupuesto de BD
            
        Returns:
            Budget: Objeto Budget reconstruido
        """
        # Parsear JSON
        datos_proyecto = json.loads(budget_data['datos_proyecto']) if isinstance(budget_data['datos_proyecto'], str) else budget_data['datos_proyecto']
        partidas_json = json.loads(budget_data['partidas']) if isinstance(budget_data['partidas'], str) else budget_data['partidas']
        
        # Reconstruir Project
        proyecto = Project(
            tipo_inmueble=PropertyType(datos_proyecto['tipo_inmueble']),
            metros_cuadrados=datos_proyecto['metros_cuadrados'],
            calidad_general=QualityLevel(datos_proyecto['calidad']),
            es_vivienda_habitual=datos_proyecto['es_vivienda_habitual'],
            estado_actual=datos_proyecto['estado_actual']
        )
        
        # Reconstruir Budget con fecha original
        budget = Budget(
            proyecto=proyecto,
            fecha_creacion=budget_data['fecha_creacion']
        )
        
        # Reconstruir cliente si existe
        if budget_data.get('cliente_nombre'):
            budget.cliente = Customer(
                nombre=budget_data['cliente_nombre'],
                email=budget_data.get('cliente_email', ''),
                telefono=budget_data.get('cliente_telefono', ''),
                direccion=budget_data.get('cliente_direccion', '')
            )
        
        # Reconstruir partidas
        for p_data in partidas_json:
            # Inferir categoría desde el código de partida
            categoria = WorkCategory.ALBANILERIA  # Default
            
            partida = BudgetItem(
                categoria=categoria,
                codigo=p_data['codigo'],
                descripcion=p_data['descripcion'],
                unidad=p_data['unidad'],
                cantidad=p_data['cantidad'],
                precio_unitario=p_data['precio_unitario'],
                es_paquete=p_data.get('es_paquete', False)
            )
            budget.agregar_partida(partida)
        
        return budget
    
    def count_user_budgets(self, user_id: str, only_active: bool = True) -> int:
        """
        Cuenta los presupuestos de un usuario.
        
        Args:
            user_id: ID del usuario
            only_active: Si solo contar activos
            
        Returns:
            int: Número de presupuestos
        """
        with get_db_session() as session:
            query = session.query(BudgetModel).filter_by(user_id=user_id)
            
            if only_active:
                query = query.filter_by(activo=True)
            
            return query.count()
    
    def delete_budget(self, budget_id: str, user_id: str) -> bool:
        """
        Marca un presupuesto como inactivo (soft delete).
        
        Args:
            budget_id: ID del presupuesto
            user_id: ID del usuario (validación)
            
        Returns:
            bool: True si se eliminó
        """
        with get_db_session() as session:
            budget = session.query(BudgetModel).filter_by(
                id=budget_id,
                user_id=user_id
            ).first()
            
            if budget:
                budget.activo = False
                session.commit()
                logger.info(f"Presupuesto {budget_id} marcado como inactivo")
                return True
            
            return False


# Singleton
_user_budget_service: Optional[UserBudgetService] = None


def get_user_budget_service() -> UserBudgetService:
    """
    Obtiene instancia singleton del servicio.
    
    Returns:
        UserBudgetService: Instancia única
    """
    global _user_budget_service
    if _user_budget_service is None:
        _user_budget_service = UserBudgetService()
    return _user_budget_service