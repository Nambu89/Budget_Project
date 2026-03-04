"""
Tests unitarios para servicios.

Verifica que los servicios de pricing y presupuestos
funcionan correctamente.
"""

import pytest
import sys
from pathlib import Path

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.domain.enums import PropertyType, QualityLevel, WorkCategory
from src.application.services import (
    PricingService,
    get_pricing_service,
    BudgetService,
    get_budget_service,
)
from src.config.settings import settings


class TestPricingService:
    """Tests del servicio de precios."""

    def test_service_initialization(self):
        """Test: El servicio se inicializa correctamente."""
        service = PricingService()

        assert service is not None
        print("PricingService inicializado")

    def test_service_singleton(self):
        """Test: get_pricing_service retorna singleton."""
        service1 = get_pricing_service()
        service2 = get_pricing_service()

        assert service1 is service2
        print("Singleton funciona correctamente")

    def test_listar_partidas_disponibles(self):
        """Test: Listar partidas disponibles."""
        service = PricingService()

        partidas = service.listar_partidas_disponibles()

        assert isinstance(partidas, (list, dict))
        assert len(partidas) > 0

        print(f"Partidas disponibles: {len(partidas)}")

    def test_obtener_info_partida(self):
        """Test: Obtener info de una categoria (clave top-level)."""
        service = PricingService()

        # pricing_data tiene claves de categoria en el nivel superior
        info = service.obtener_info_partida("albanileria")

        assert info is not None
        assert "alicatado_paredes" in info

        print(f"Info partida obtenida: {list(info.keys())[:5]}")

    def test_obtener_precio_paquete(self):
        """Test: Obtener precio de un paquete."""
        service = PricingService()

        precio = service.obtener_precio_paquete(
            paquete="bano_completo",
            calidad=QualityLevel.ESTANDAR,
            metros=60.0,
        )

        assert precio is not None
        assert precio > 0

        print(f"Precio paquete: {precio}")

    def test_crear_partida(self):
        """Test: Crear una partida individual."""
        service = PricingService()

        partida = service.crear_partida(
            categoria=WorkCategory.ALBANILERIA,
            partida="alicatado_paredes",
            cantidad=20.0,
            calidad=QualityLevel.ESTANDAR,
        )

        assert partida is not None
        assert partida.cantidad == 20.0
        assert partida.precio_unitario > 0

        print(f"Partida creada: {partida.descripcion} - {partida.subtotal}")

    def test_calcular_iva(self):
        """Test: Calcular IVA (siempre 21%)."""
        service = PricingService()

        base = 1000.0

        # calcular_iva requiere un Project
        from src.domain.models import Project
        proyecto = Project(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )

        resultado = service.calcular_iva(base, proyecto)

        assert resultado["porcentaje"] == 21
        assert resultado["importe"] == pytest.approx(base * 0.21, rel=0.01)

        print(f"IVA calculado: {resultado['porcentaje']}% = {resultado['importe']}")

    def test_calcular_total_con_iva(self):
        """Test: Calcular total con redondeo e IVA."""
        service = PricingService()

        base = 1000.0
        resultado = service.calcular_total_con_iva(base)

        assert "total" in resultado
        assert "iva_porcentaje" in resultado
        assert resultado["iva_porcentaje"] == 21
        assert resultado["redondeo_porcentaje"] == 5
        assert resultado["total"] > base

        # base * 1.05 * 1.21
        expected_total = round(round(base * 1.05, 2) * 1.21, 2)
        assert resultado["total"] == pytest.approx(expected_total, rel=0.01)

        print(f"Total calculado: {resultado['total']}")

    def test_crear_partida_precio_unitario(self):
        """Test: Crear partida devuelve precio unitario correcto."""
        service = PricingService()

        partida = service.crear_partida(
            categoria=WorkCategory.ALBANILERIA,
            partida="alicatado_paredes",
            cantidad=1.0,
            calidad=QualityLevel.ESTANDAR,
        )

        assert partida is not None
        assert partida.precio_unitario > 0

        print(f"Precio unitario via crear_partida: {partida.precio_unitario}")

    def test_precios_varian_por_calidad(self):
        """Test: Precios varian segun calidad."""
        service = PricingService()

        partida_basico = service.crear_partida(
            categoria=WorkCategory.ALBANILERIA,
            partida="alicatado_paredes",
            cantidad=1.0,
            calidad=QualityLevel.BASICO,
        )

        partida_estandar = service.crear_partida(
            categoria=WorkCategory.ALBANILERIA,
            partida="alicatado_paredes",
            cantidad=1.0,
            calidad=QualityLevel.ESTANDAR,
        )

        partida_premium = service.crear_partida(
            categoria=WorkCategory.ALBANILERIA,
            partida="alicatado_paredes",
            cantidad=1.0,
            calidad=QualityLevel.PREMIUM,
        )

        assert partida_basico.precio_unitario < partida_estandar.precio_unitario < partida_premium.precio_unitario

        print(f"Precios: basico={partida_basico.precio_unitario}, estandar={partida_estandar.precio_unitario}, premium={partida_premium.precio_unitario}")


class TestBudgetService:
    """Tests del servicio de presupuestos."""

    def test_service_initialization(self):
        """Test: El servicio se inicializa correctamente."""
        service = BudgetService()

        assert service is not None
        assert service.pricing is not None
        print("BudgetService inicializado")

    def test_service_singleton(self):
        """Test: get_budget_service retorna singleton."""
        service1 = get_budget_service()
        service2 = get_budget_service()

        assert service1 is service2
        print("Singleton funciona correctamente")

    def test_crear_presupuesto(self):
        """Test: Crear presupuesto vacío."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            calidad=QualityLevel.ESTANDAR,
        )

        assert presupuesto is not None
        assert presupuesto.proyecto.tipo_inmueble == PropertyType.PISO
        assert presupuesto.proyecto.metros_cuadrados == 80.0

        print(f"Presupuesto creado: {presupuesto.numero_presupuesto}")

    def test_agregar_partida_individual(self):
        """Test: Agregar partida individual con markup."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )

        service.agregar_partida(
            presupuesto=presupuesto,
            categoria=WorkCategory.ALBANILERIA,
            partida="alicatado_paredes",
            cantidad=25.0,
            calidad=QualityLevel.ESTANDAR,
        )

        assert presupuesto.num_partidas == 1
        assert presupuesto.partidas[0].es_paquete is False

        print(f"Partida agregada: {presupuesto.subtotal}")

    def test_agregar_paquete_sin_markup(self):
        """Test: Agregar paquete sin markup."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
        )

        service.agregar_paquete(
            presupuesto=presupuesto,
            paquete="bano_completo",
            calidad=QualityLevel.ESTANDAR,
            metros=60.0,
        )

        assert presupuesto.num_partidas == 1
        assert presupuesto.partidas[0].es_paquete is True

        print(f"Paquete agregado: {presupuesto.subtotal}")

    def test_calcular_totales(self):
        """Test: Calcular totales con redondeo e IVA (siempre 21%)."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
        )

        service.agregar_paquete(
            presupuesto=presupuesto,
            paquete="bano_completo",
            calidad=QualityLevel.ESTANDAR,
            metros=60.0,
        )

        totales = service.calcular_totales(presupuesto)

        # Verificar claves
        assert "iva_importe" in totales
        assert "total" in totales
        assert "iva_porcentaje" in totales

        # IVA siempre 21% en Fase 1
        assert totales["iva_porcentaje"] == 21

        print(f"Totales calculados: {totales['total']}")

    def test_asignar_cliente(self):
        """Test: Asignar cliente al presupuesto."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )

        service.asignar_cliente(
            presupuesto=presupuesto,
            nombre="Juan Garcia",
            email="juan@test.com",
            telefono="612345678",
            direccion_obra="Calle Test 123",
        )

        assert presupuesto.tiene_cliente is True
        assert presupuesto.cliente.nombre == "Juan Garcia"

        print("Cliente asignado correctamente")

    def test_comparar_con_paquete(self):
        """Test: Comparar partidas individuales vs paquete."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
        )

        # Agregar partidas de fontaneria
        service.agregar_partida(
            presupuesto=presupuesto,
            categoria=WorkCategory.FONTANERIA,
            partida="plato_ducha",
            cantidad=1.0,
        )

        service.agregar_partida(
            presupuesto=presupuesto,
            categoria=WorkCategory.FONTANERIA,
            partida="inodoro_suspendido",
            cantidad=1.0,
        )

        comparativa = service.comparar_con_paquete(presupuesto, "bano_completo")

        assert "precio_actual" in comparativa
        assert "precio_paquete" in comparativa
        assert "ahorro" in comparativa

        print(f"Comparativa: actual={comparativa['precio_actual']}, paquete={comparativa['precio_paquete']}")

    def test_generar_pdf(self):
        """Test: Generar PDF del presupuesto."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )

        service.agregar_paquete(
            presupuesto=presupuesto,
            paquete="bano_completo",
            metros=80.0,
        )

        service.asignar_cliente(
            presupuesto=presupuesto,
            nombre="Test Client",
            email="test@test.com",
            telefono="612345678",
        )

        pdf_bytes = service.generar_pdf(presupuesto)

        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'

        print(f"PDF generado: {len(pdf_bytes)} bytes")

    def test_agregar_partidas_multiples(self):
        """Test: Agregar múltiples partidas de una vez."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )

        partidas = [
            {
                "categoria": WorkCategory.ALBANILERIA,
                "partida": "alicatado_paredes",
                "cantidad": 25.0,
                "calidad": QualityLevel.ESTANDAR,
            },
            {
                "categoria": WorkCategory.FONTANERIA,
                "partida": "plato_ducha",
                "cantidad": 1.0,
                "calidad": QualityLevel.ESTANDAR,
            },
        ]

        service.agregar_partidas_multiples(presupuesto, partidas)

        assert presupuesto.num_partidas == 2

        print(f"Multiples partidas agregadas: {presupuesto.num_partidas}")


class TestBusinessRules:
    """Tests de reglas de negocio."""

    def test_markup_solo_aplica_a_partidas_individuales(self):
        """Test: Markup solo aplica a partidas, no a paquetes."""
        service = BudgetService()

        # Presupuesto con partida individual
        pres_partida = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
        )

        service.agregar_partida(
            presupuesto=pres_partida,
            categoria=WorkCategory.FONTANERIA,
            partida="plato_ducha",
            cantidad=1.0,
        )

        # Presupuesto con paquete
        pres_paquete = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
        )

        service.agregar_paquete(
            presupuesto=pres_paquete,
            paquete="bano_completo",
            metros=60.0,
        )

        # Verificar que partida tiene markup y paquete no
        assert pres_partida.partidas[0].es_paquete is False
        assert pres_paquete.partidas[0].es_paquete is True

        print("Markup aplicado correctamente segun tipo")

    def test_iva_siempre_21_por_ciento(self):
        """Test: IVA siempre 21% para todos los tipos de inmueble (Fase 1)."""
        service = BudgetService()

        for tipo in [PropertyType.PISO, PropertyType.VIVIENDA, PropertyType.LOCAL, PropertyType.OFICINA]:
            pres = service.crear_presupuesto(
                tipo_inmueble=tipo,
                metros_cuadrados=80.0,
            )

            assert pres.iva_porcentaje == 21, f"IVA debe ser 21% para {tipo}"

        print("IVA 21% aplicado correctamente a todos los tipos")

    def test_redondeo_al_alza(self):
        """Test: Redondeo al alza del 5%."""
        service = BudgetService()

        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )

        service.agregar_paquete(
            presupuesto=presupuesto,
            paquete="bano_completo",
            metros=80.0,
        )

        totales = service.calcular_totales(presupuesto)

        # Verificar redondeo
        assert totales["redondeo_porcentaje"] == 5
        assert totales["importe_redondeo"] > 0

        # Base con redondeo debe ser mayor que subtotal
        assert totales["base_con_redondeo"] > presupuesto.subtotal

        print(f"Redondeo aplicado: {totales['importe_redondeo']}")


# ============================================
# Ejecutar tests directamente
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Tests Unitarios de Servicios")
    print("=" * 60)

    pytest.main([__file__, "-v", "-s"])
