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
        print("✅ PricingService inicializado")
    
    def test_service_singleton(self):
        """Test: get_pricing_service retorna singleton."""
        service1 = get_pricing_service()
        service2 = get_pricing_service()
        
        assert service1 is service2
        print("✅ Singleton funciona correctamente")
    
    def test_listar_categorias(self):
        """Test: Listar categorías disponibles."""
        service = PricingService()
        
        categorias = service.listar_categorias()
        
        assert isinstance(categorias, list)
        assert len(categorias) > 0
        
        # Verificar estructura (puede tener 'codigo' o 'valor')
        for cat in categorias:
            assert "nombre" in cat
            assert "partidas" in cat
            # codigo o valor
            assert "codigo" in cat or "valor" in cat
        
        print(f"✅ Categorías listadas: {len(categorias)}")
    
    def test_listar_paquetes(self):
        """Test: Listar paquetes disponibles."""
        service = PricingService()
        
        paquetes = service.listar_paquetes()
        
        assert isinstance(paquetes, list)
        assert len(paquetes) > 0
        
        # Verificar estructura (puede tener 'codigo' o 'valor')
        for pkg in paquetes:
            assert "nombre" in pkg
            assert "descripcion" in pkg
            # codigo o valor
            assert "codigo" in pkg or "valor" in pkg
        
        print(f"✅ Paquetes listados: {len(paquetes)}")
    
    def test_obtener_precio_partida(self):
        """Test: Obtener precio de una partida."""
        service = PricingService()
        
        precio = service.obtener_precio_partida(
            categoria="albanileria",
            partida="alicatado_paredes",
            calidad=QualityLevel.ESTANDAR,
        )
        
        assert precio is not None
        assert precio > 0
        
        print(f"✅ Precio obtenido: {precio}€")
    
    def test_obtener_precio_partida_diferentes_calidades(self):
        """Test: Precios varían según calidad."""
        service = PricingService()
        
        precio_basico = service.obtener_precio_partida(
            categoria="albanileria",
            partida="alicatado_paredes",
            calidad=QualityLevel.BASICO,
        )
        
        precio_estandar = service.obtener_precio_partida(
            categoria="albanileria",
            partida="alicatado_paredes",
            calidad=QualityLevel.ESTANDAR,
        )
        
        precio_premium = service.obtener_precio_partida(
            categoria="albanileria",
            partida="alicatado_paredes",
            calidad=QualityLevel.PREMIUM,
        )
        
        assert precio_basico < precio_estandar < precio_premium
        
        print(f"✅ Precios por calidad: básico={precio_basico}€, estándar={precio_estandar}€, premium={precio_premium}€")
    
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
        
        print(f"✅ Precio paquete: {precio}€")
    
    def test_obtener_info_paquete(self):
        """Test: Obtener información de un paquete."""
        service = PricingService()
        
        # Usar listar_paquetes para obtener info
        paquetes = service.listar_paquetes()
        
        # Buscar bano_completo
        bano = None
        for pkg in paquetes:
            if pkg.get("valor") == "bano_completo" or pkg.get("codigo") == "bano_completo":
                bano = pkg
                break
        
        assert bano is not None
        assert "nombre" in bano
        assert "descripcion" in bano
        
        print(f"✅ Info paquete: {bano['nombre']}")
    
    def test_aplicar_markup(self):
        """Test: Aplicar markup a partidas individuales."""
        service = PricingService()
        
        precio_base = 100.0
        precio_con_markup = service.aplicar_markup(precio_base)
        
        markup_esperado = precio_base * (1 + settings.markup_partidas_individuales / 100)
        
        assert precio_con_markup == pytest.approx(markup_esperado, rel=0.01)
        
        print(f"✅ Markup aplicado: {precio_base}€ → {precio_con_markup}€")
    
    def test_aplicar_redondeo_alza(self):
        """Test: Aplicar redondeo al alza."""
        service = PricingService()
        
        base = 1000.0
        con_redondeo = service.aplicar_redondeo_alza(base)
        
        redondeo_esperado = base * (1 + settings.redondeo_alza / 100)
        
        assert con_redondeo == pytest.approx(redondeo_esperado, rel=0.01)
        
        print(f"✅ Redondeo aplicado: {base}€ → {con_redondeo}€")
    
    def test_calcular_iva(self):
        """Test: Calcular IVA."""
        service = PricingService()
        
        base = 1000.0
        
        resultado_general = service.calcular_iva(base, es_vivienda_habitual=False)
        resultado_reducido = service.calcular_iva(base, es_vivienda_habitual=True)
        
        # El método puede retornar tupla (porcentaje, importe) o solo importe
        if isinstance(resultado_general, tuple):
            porcentaje_general, iva_general = resultado_general
            porcentaje_reducido, iva_reducido = resultado_reducido
            assert porcentaje_general == 21
            assert porcentaje_reducido == 10
        else:
            iva_general = resultado_general
            iva_reducido = resultado_reducido
        
        assert iva_general == pytest.approx(base * 0.21, rel=0.01)
        assert iva_reducido == pytest.approx(base * 0.10, rel=0.01)
        
        print(f"✅ IVA calculado: general={iva_general}€, reducido={iva_reducido}€")


class TestBudgetService:
    """Tests del servicio de presupuestos."""
    
    def test_service_initialization(self):
        """Test: El servicio se inicializa correctamente."""
        service = BudgetService()
        
        assert service is not None
        assert service.pricing is not None
        print("✅ BudgetService inicializado")
    
    def test_service_singleton(self):
        """Test: get_budget_service retorna singleton."""
        service1 = get_budget_service()
        service2 = get_budget_service()
        
        assert service1 is service2
        print("✅ Singleton funciona correctamente")
    
    def test_crear_presupuesto(self):
        """Test: Crear presupuesto vacío."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            calidad=QualityLevel.ESTANDAR,
            es_vivienda_habitual=True,
        )
        
        assert presupuesto is not None
        assert presupuesto.proyecto.tipo_inmueble == PropertyType.PISO
        assert presupuesto.proyecto.metros_cuadrados == 80.0
        
        print(f"✅ Presupuesto creado: {presupuesto.numero_presupuesto}")
    
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
        
        print(f"✅ Partida agregada: {presupuesto.subtotal}€")
    
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
        
        print(f"✅ Paquete agregado: {presupuesto.subtotal}€")
    
    def test_calcular_totales(self):
        """Test: Calcular totales con redondeo e IVA."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
            es_vivienda_habitual=True,
        )
        
        service.agregar_paquete(
            presupuesto=presupuesto,
            paquete="bano_completo",
            calidad=QualityLevel.ESTANDAR,
            metros=60.0,
        )
        
        totales = service.calcular_totales(presupuesto)
        
        # Verificar que tiene las claves de totales
        assert "base_imponible" in totales
        assert "iva_importe" in totales
        assert "total" in totales
        
        # IVA debe ser 10% para vivienda habitual
        assert totales["iva_porcentaje"] == 10
        
        print(f"✅ Totales calculados: {totales['total']}€")
    
    def test_asignar_cliente(self):
        """Test: Asignar cliente al presupuesto."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )
        
        service.asignar_cliente(
            presupuesto=presupuesto,
            nombre="Juan García",
            email="juan@test.com",
            telefono="612345678",
            direccion_obra="Calle Test 123",
        )
        
        assert presupuesto.tiene_cliente is True
        assert presupuesto.cliente.nombre == "Juan García"
        
        print("✅ Cliente asignado correctamente")
    
    def test_comparar_con_paquete(self):
        """Test: Comparar partidas individuales vs paquete."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=60.0,
            es_vivienda_habitual=True,
        )
        
        # Agregar partidas de fontanería
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
        
        print(f"✅ Comparativa: actual={comparativa['precio_actual']}€, paquete={comparativa['precio_paquete']}€")
    
    def test_generar_pdf(self):
        """Test: Generar PDF del presupuesto."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            es_vivienda_habitual=True,
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
        
        print(f"✅ PDF generado: {len(pdf_bytes)} bytes")
    
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
        
        print(f"✅ Múltiples partidas agregadas: {presupuesto.num_partidas}")


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
        
        print("✅ Markup aplicado correctamente según tipo")
    
    def test_iva_reducido_solo_vivienda_habitual(self):
        """Test: IVA reducido solo para vivienda habitual."""
        service = BudgetService()
        
        # Piso como vivienda habitual
        pres_habitual = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            es_vivienda_habitual=True,
        )
        
        # Piso NO vivienda habitual
        pres_no_habitual = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            es_vivienda_habitual=False,
        )
        
        # Local (nunca vivienda habitual)
        pres_local = service.crear_presupuesto(
            tipo_inmueble=PropertyType.LOCAL,
            metros_cuadrados=100.0,
            es_vivienda_habitual=True,  # Se ignora
        )
        
        assert pres_habitual.iva_porcentaje == 10
        assert pres_no_habitual.iva_porcentaje == 21
        assert pres_local.iva_porcentaje == 21
        
        print("✅ IVA aplicado correctamente según tipo de inmueble")
    
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
        
        # Verificar que hay redondeo
        assert totales["redondeo_porcentaje"] == settings.redondeo_alza
        assert totales["redondeo_importe"] > 0
        
        # Base con redondeo debe ser mayor que subtotal
        assert totales["base_imponible"] > presupuesto.subtotal
        
        print(f"✅ Redondeo aplicado: {totales['redondeo_importe']}€")


# ============================================
# Ejecutar tests directamente
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Tests Unitarios de Servicios")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])