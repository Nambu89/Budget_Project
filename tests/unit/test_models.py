"""
Tests unitarios para modelos de dominio.

Verifica que los modelos de datos funcionan correctamente
con validaciones, cálculos y serialización.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.domain.enums import PropertyType, QualityLevel, WorkCategory
from src.domain.models import Project, Customer, BudgetItem, Budget


class TestPropertyType:
    """Tests del enum PropertyType."""
    
    def test_property_type_values(self):
        """Test: Valores del enum son correctos."""
        assert PropertyType.PISO.value == "piso"
        assert PropertyType.VIVIENDA.value == "vivienda"
        assert PropertyType.OFICINA.value == "oficina"
        assert PropertyType.LOCAL.value == "local"
    
    def test_property_type_display_name(self):
        """Test: Display names son correctos."""
        assert PropertyType.PISO.display_name == "Piso"
        assert PropertyType.VIVIENDA.display_name == "Vivienda independiente"
        assert PropertyType.OFICINA.display_name == "Oficina"
        assert PropertyType.LOCAL.display_name == "Local comercial"
    
    def test_property_type_iva(self):
        """Test: IVA se asigna correctamente."""
        assert PropertyType.PISO.iva_aplicable == 10  # Vivienda habitual
        assert PropertyType.VIVIENDA.iva_aplicable == 10
        assert PropertyType.OFICINA.iva_aplicable == 21  # General
        assert PropertyType.LOCAL.iva_aplicable == 21
    
    def test_property_type_es_vivienda_habitual(self):
        """Test: Identificación de vivienda habitual."""
        assert PropertyType.PISO.es_vivienda_habitual is True
        assert PropertyType.VIVIENDA.es_vivienda_habitual is True
        assert PropertyType.OFICINA.es_vivienda_habitual is False
        assert PropertyType.LOCAL.es_vivienda_habitual is False


class TestQualityLevel:
    """Tests del enum QualityLevel."""
    
    def test_quality_level_values(self):
        """Test: Valores del enum son correctos."""
        assert QualityLevel.BASICO.value == "basico"
        assert QualityLevel.ESTANDAR.value == "estandar"
        assert QualityLevel.PREMIUM.value == "premium"
    
    def test_quality_level_multiplicador(self):
        """Test: Multiplicadores son correctos."""
        assert QualityLevel.BASICO.multiplicador == 0.8
        assert QualityLevel.ESTANDAR.multiplicador == 1.0
        assert QualityLevel.PREMIUM.multiplicador == 1.5
    
    def test_quality_level_descripcion(self):
        """Test: Descripciones existen."""
        assert len(QualityLevel.BASICO.descripcion) > 0
        assert len(QualityLevel.ESTANDAR.descripcion) > 0
        assert len(QualityLevel.PREMIUM.descripcion) > 0


class TestWorkCategory:
    """Tests del enum WorkCategory."""
    
    def test_work_category_values(self):
        """Test: Valores del enum son correctos."""
        assert WorkCategory.ALBANILERIA.value == "albanileria"
        assert WorkCategory.FONTANERIA.value == "fontaneria"
        assert WorkCategory.ELECTRICIDAD.value == "electricidad"
        assert WorkCategory.COCINA.value == "cocina"
        assert WorkCategory.CARPINTERIA.value == "carpinteria"
    
    def test_work_category_display_name(self):
        """Test: Display names son correctos."""
        assert WorkCategory.ALBANILERIA.display_name == "Albañilería"
        assert WorkCategory.FONTANERIA.display_name == "Fontanería"
    
    def test_work_category_icono(self):
        """Test: Iconos existen."""
        for cat in WorkCategory:
            assert cat.icono is not None
            assert len(cat.icono) > 0


class TestProject:
    """Tests del modelo Project."""
    
    def test_project_creation(self):
        """Test: Crear proyecto básico."""
        proyecto = Project(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )
        
        assert proyecto.tipo_inmueble == PropertyType.PISO
        assert proyecto.metros_cuadrados == 80.0
        assert proyecto.calidad_general == QualityLevel.ESTANDAR  # Default
    
    def test_project_iva_vivienda_habitual(self):
        """Test: IVA reducido para vivienda habitual."""
        proyecto = Project(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            es_vivienda_habitual=True,
        )
        
        assert proyecto.iva_aplicable == 10
    
    def test_project_iva_no_vivienda_habitual(self):
        """Test: IVA general para no vivienda habitual."""
        proyecto = Project(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            es_vivienda_habitual=False,
        )
        
        assert proyecto.iva_aplicable == 21
    
    def test_project_iva_local(self):
        """Test: IVA general para local (siempre 21%)."""
        proyecto = Project(
            tipo_inmueble=PropertyType.LOCAL,
            metros_cuadrados=100.0,
            es_vivienda_habitual=True,  # Aunque se marque, no aplica
        )
        
        assert proyecto.iva_aplicable == 21
    
    def test_project_validacion_metros(self):
        """Test: Validación de metros cuadrados."""
        with pytest.raises(ValueError):
            Project(
                tipo_inmueble=PropertyType.PISO,
                metros_cuadrados=0,  # No válido
            )
        
        with pytest.raises(ValueError):
            Project(
                tipo_inmueble=PropertyType.PISO,
                metros_cuadrados=-10,  # No válido
            )
    
    def test_project_serialization(self):
        """Test: Serialización a dict."""
        proyecto = Project(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            calidad_general=QualityLevel.PREMIUM,
            es_vivienda_habitual=True,
            ubicacion="Madrid",
        )
        
        data = proyecto.model_dump()
        
        assert "tipo_inmueble" in data
        assert "metros_cuadrados" in data
        assert data["metros_cuadrados"] == 80.0


class TestCustomer:
    """Tests del modelo Customer."""
    
    def test_customer_creation(self):
        """Test: Crear cliente básico."""
        cliente = Customer(
            nombre="Juan García",
            email="juan@example.com",
            telefono="612345678",
        )
        
        assert cliente.nombre == "Juan García"
        assert cliente.email == "juan@example.com"
    
    def test_customer_telefono_formateado(self):
        """Test: Formato de teléfono."""
        cliente = Customer(
            nombre="Test",
            email="test@test.com",
            telefono="612345678",
        )
        
        formateado = cliente.telefono_formateado
        
        # Debe contener espacios o guiones
        assert len(formateado) >= 9
    
    def test_customer_nombre_display(self):
        """Test: Nombre para display."""
        cliente = Customer(
            nombre="  juan garcía lópez  ",
            email="test@test.com",
            telefono="612345678",
        )
        
        # Se limpia automáticamente
        assert cliente.nombre.strip() == cliente.nombre
    
    def test_customer_validacion_email(self):
        """Test: Validación de email."""
        # Email válido
        cliente = Customer(
            nombre="Test",
            email="valid@email.com",
            telefono="612345678",
        )
        assert cliente.email == "valid@email.com"


class TestBudgetItem:
    """Tests del modelo BudgetItem."""
    
    def test_budget_item_creation(self):
        """Test: Crear partida básica."""
        partida = BudgetItem(
            categoria=WorkCategory.ALBANILERIA,
            codigo="ALB-001",
            descripcion="Alicatado de paredes",
            unidad="m2",
            cantidad=25.0,
            precio_unitario=45.0,
        )
        
        assert partida.categoria == WorkCategory.ALBANILERIA
        assert partida.cantidad == 25.0
        assert partida.precio_unitario == 45.0
    
    def test_budget_item_subtotal(self):
        """Test: Cálculo de subtotal."""
        partida = BudgetItem(
            categoria=WorkCategory.ALBANILERIA,
            codigo="ALB-001",
            descripcion="Alicatado",
            unidad="m2",
            cantidad=20.0,
            precio_unitario=50.0,
        )
        
        assert partida.subtotal == 1000.0  # 20 * 50
    
    def test_budget_item_es_paquete(self):
        """Test: Identificación de paquete."""
        partida_normal = BudgetItem(
            categoria=WorkCategory.ALBANILERIA,
            codigo="ALB-001",
            descripcion="Partida normal",
            unidad="m2",
            cantidad=10.0,
            precio_unitario=50.0,
            es_paquete=False,
        )
        
        paquete = BudgetItem(
            categoria=WorkCategory.FONTANERIA,
            codigo="PKG-001",
            descripcion="Baño completo",
            unidad="ud",
            cantidad=1.0,
            precio_unitario=3500.0,
            es_paquete=True,
        )
        
        assert partida_normal.es_paquete is False
        assert paquete.es_paquete is True
    
    def test_budget_item_validacion_cantidad(self):
        """Test: Validación de cantidad."""
        with pytest.raises(ValueError):
            BudgetItem(
                categoria=WorkCategory.ALBANILERIA,
                codigo="ALB-001",
                descripcion="Test",
                unidad="m2",
                cantidad=0,  # No válido
                precio_unitario=50.0,
            )


class TestBudget:
    """Tests del modelo Budget."""
    
    def test_budget_creation(self, proyecto_piso):
        """Test: Crear presupuesto vacío."""
        presupuesto = Budget(proyecto=proyecto_piso)
        
        assert presupuesto.proyecto == proyecto_piso
        assert presupuesto.num_partidas == 0
        assert presupuesto.subtotal == 0
    
    def test_budget_numero_presupuesto(self, proyecto_piso):
        """Test: Número de presupuesto se genera automáticamente."""
        presupuesto = Budget(proyecto=proyecto_piso)
        
        assert presupuesto.numero_presupuesto is not None
        assert len(presupuesto.numero_presupuesto) > 0
        assert presupuesto.numero_presupuesto.startswith("PRES-")
    
    def test_budget_fecha_validez(self, proyecto_piso):
        """Test: Fecha de validez se calcula correctamente."""
        presupuesto = Budget(proyecto=proyecto_piso, dias_validez=30)
        
        fecha_esperada = presupuesto.fecha_emision + timedelta(days=30)
        
        assert presupuesto.fecha_validez.date() == fecha_esperada.date()
    
    def test_budget_agregar_partida(self, presupuesto_vacio, partida_albanileria):
        """Test: Agregar partida al presupuesto."""
        presupuesto_vacio.agregar_partida(partida_albanileria)
        
        assert presupuesto_vacio.num_partidas == 1
        assert presupuesto_vacio.subtotal == partida_albanileria.subtotal
    
    def test_budget_agregar_multiples_partidas(self, presupuesto_vacio, partida_albanileria, partida_fontaneria):
        """Test: Agregar múltiples partidas."""
        presupuesto_vacio.agregar_partida(partida_albanileria)
        presupuesto_vacio.agregar_partida(partida_fontaneria)
        
        assert presupuesto_vacio.num_partidas == 2
        assert presupuesto_vacio.subtotal == partida_albanileria.subtotal + partida_fontaneria.subtotal
    
    def test_budget_eliminar_partida(self, presupuesto_con_partidas):
        """Test: Eliminar partida del presupuesto."""
        num_inicial = presupuesto_con_partidas.num_partidas
        
        # Eliminar por índice (0 = primera partida)
        presupuesto_con_partidas.eliminar_partida(0)
        
        assert presupuesto_con_partidas.num_partidas == num_inicial - 1
    
    def test_budget_calcular_total_con_iva(self, presupuesto_con_partidas):
        """Test: Cálculo de total con IVA."""
        subtotal = presupuesto_con_partidas.subtotal
        iva_porcentaje = presupuesto_con_partidas.iva_porcentaje
        
        iva_esperado = subtotal * (iva_porcentaje / 100)
        total_esperado = subtotal + iva_esperado
        
        assert presupuesto_con_partidas.importe_iva == pytest.approx(iva_esperado, rel=0.01)
        assert presupuesto_con_partidas.total == pytest.approx(total_esperado, rel=0.01)
    
    def test_budget_aplicar_descuento(self, presupuesto_con_partidas):
        """Test: Aplicar descuento al presupuesto."""
        presupuesto_con_partidas.descuento_porcentaje = 10.0
        
        subtotal = sum(p.subtotal for p in presupuesto_con_partidas.partidas)
        descuento_esperado = subtotal * 0.10
        
        assert presupuesto_con_partidas.importe_descuento == pytest.approx(descuento_esperado, rel=0.01)
    
    def test_budget_resumen_por_categorias(self, presupuesto_con_partidas):
        """Test: Resumen agrupado por categorías."""
        resumen = presupuesto_con_partidas.resumen_por_categorias()
        
        assert isinstance(resumen, dict)
        assert len(resumen) > 0
        
        # Suma de categorías debe ser igual al subtotal
        total_categorias = sum(resumen.values())
        assert total_categorias == pytest.approx(presupuesto_con_partidas.subtotal, rel=0.01)
    
    def test_budget_asignar_cliente(self, presupuesto_vacio, cliente_ejemplo):
        """Test: Asignar cliente al presupuesto."""
        presupuesto_vacio.cliente = cliente_ejemplo
        
        assert presupuesto_vacio.tiene_cliente is True
        assert presupuesto_vacio.cliente.nombre == cliente_ejemplo.nombre
    
    def test_budget_serialization_json(self, presupuesto_con_partidas):
        """Test: Serialización a JSON."""
        json_str = presupuesto_con_partidas.model_dump_json()
        
        assert json_str is not None
        assert len(json_str) > 0
        assert "numero_presupuesto" in json_str
    
    def test_budget_resumen_texto(self, presupuesto_con_partidas):
        """Test: Generar resumen en texto."""
        # resumen_texto puede ser método o propiedad, intentamos ambos
        if callable(getattr(presupuesto_con_partidas, 'resumen_texto', None)):
            resumen = presupuesto_con_partidas.resumen_texto()
        else:
            resumen = presupuesto_con_partidas.resumen_texto
        
        assert resumen is not None
        assert "Presupuesto" in resumen or "PRES-" in resumen
        assert len(resumen) > 0


# ============================================
# Ejecutar tests directamente
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Tests Unitarios de Modelos de Dominio")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])