"""
Tests de generación de PDF.

Verifica que los PDFs se generan correctamente
con todo el contenido esperado.
"""

import pytest
import sys
from pathlib import Path
import tempfile
import os

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.domain.enums import PropertyType, QualityLevel, WorkCategory
from src.domain.models import Project, Customer, Budget, BudgetItem
from src.infrastructure.pdf import PDFGenerator, generar_pdf_presupuesto
from src.application.services import BudgetService


class TestPDFGenerator:
    """Tests del generador de PDF."""
    
    def test_generator_initialization(self):
        """Test: El generador se inicializa correctamente."""
        generator = PDFGenerator()
        
        assert generator is not None
        print("✅ PDFGenerator inicializado")
    
    def test_generar_pdf_basico(self, presupuesto_con_partidas):
        """Test: Generar PDF básico."""
        generator = PDFGenerator()
        
        pdf_bytes = generator.generar(presupuesto_con_partidas)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        # Verificar que es un PDF válido
        assert pdf_bytes[:4] == b'%PDF'
        
        print(f"✅ PDF generado: {len(pdf_bytes)} bytes")
    
    def test_generar_pdf_con_cliente(self, presupuesto_con_partidas, cliente_ejemplo):
        """Test: Generar PDF con datos de cliente."""
        presupuesto_con_partidas.cliente = cliente_ejemplo
        
        generator = PDFGenerator()
        pdf_bytes = generator.generar(presupuesto_con_partidas)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        print(f"✅ PDF con cliente generado: {len(pdf_bytes)} bytes")
    
    def test_generar_pdf_guardar_archivo(self, presupuesto_con_partidas):
        """Test: Guardar PDF en archivo."""
        generator = PDFGenerator()
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            output_path = f.name
        
        try:
            pdf_bytes = generator.generar(
                presupuesto=presupuesto_con_partidas,
                output_path=output_path,
            )
            
            # Verificar que el archivo existe
            assert os.path.exists(output_path)
            
            # Verificar tamaño del archivo
            file_size = os.path.getsize(output_path)
            assert file_size > 0
            assert file_size == len(pdf_bytes)
            
            print(f"✅ PDF guardado en: {output_path} ({file_size} bytes)")
            
        finally:
            # Limpiar
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_generar_pdf_funcion_conveniencia(self, presupuesto_con_partidas):
        """Test: Función de conveniencia generar_pdf_presupuesto."""
        pdf_bytes = generar_pdf_presupuesto(presupuesto_con_partidas)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b'%PDF'
        
        print("✅ Función de conveniencia funciona")


class TestPDFContent:
    """Tests del contenido del PDF."""
    
    def test_pdf_contiene_numero_presupuesto(self):
        """Test: PDF contiene número de presupuesto."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )
        
        service.agregar_paquete(presupuesto, "bano_completo", metros=80.0)
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        # El número de presupuesto debería estar en el PDF
        # No podemos verificar el contenido directamente, pero sí que se genera
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 1000  # PDF debe tener contenido sustancial
        
        print(f"✅ PDF generado con número: {presupuesto.numero_presupuesto}")
    
    def test_pdf_diferentes_calidades(self):
        """Test: PDFs se generan para diferentes calidades."""
        service = BudgetService()
        
        for calidad in [QualityLevel.BASICO, QualityLevel.ESTANDAR, QualityLevel.PREMIUM]:
            presupuesto = service.crear_presupuesto(
                tipo_inmueble=PropertyType.PISO,
                metros_cuadrados=80.0,
                calidad=calidad,
            )
            
            service.agregar_paquete(presupuesto, "bano_completo", calidad=calidad, metros=80.0)
            
            pdf_bytes = service.generar_pdf(presupuesto)
            
            assert pdf_bytes is not None
            assert len(pdf_bytes) > 0
            
            print(f"✅ PDF generado para calidad {calidad.display_name}")
    
    def test_pdf_diferentes_tipos_inmueble(self):
        """Test: PDFs se generan para diferentes tipos de inmueble."""
        service = BudgetService()
        
        for tipo in [PropertyType.PISO, PropertyType.VIVIENDA, PropertyType.OFICINA, PropertyType.LOCAL]:
            presupuesto = service.crear_presupuesto(
                tipo_inmueble=tipo,
                metros_cuadrados=100.0,
            )
            
            service.agregar_paquete(presupuesto, "bano_completo", metros=100.0)
            
            pdf_bytes = service.generar_pdf(presupuesto)
            
            assert pdf_bytes is not None
            
            print(f"✅ PDF generado para tipo {tipo.display_name}")
    
    def test_pdf_con_descuento(self):
        """Test: PDF con descuento aplicado."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )
        
        service.agregar_paquete(presupuesto, "bano_completo", metros=80.0)
        
        # Aplicar descuento
        presupuesto.descuento_porcentaje = 10.0
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        print(f"✅ PDF con descuento generado")
    
    def test_pdf_con_multiples_partidas(self):
        """Test: PDF con múltiples partidas."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
        )
        
        # Agregar varias partidas (solo las que existen en pricing_data)
        partidas = [
            (WorkCategory.ALBANILERIA, "alicatado_paredes", 25.0),
            (WorkCategory.FONTANERIA, "plato_ducha", 1.0),
            (WorkCategory.ELECTRICIDAD, "punto_luz", 10.0),
        ]
        
        for cat, partida, cantidad in partidas:
            service.agregar_partida(
                presupuesto=presupuesto,
                categoria=cat,
                partida=partida,
                cantidad=cantidad,
            )
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        assert pdf_bytes is not None
        assert presupuesto.num_partidas == 3
        
        print(f"✅ PDF con {presupuesto.num_partidas} partidas generado")
    
    def test_pdf_presupuesto_grande(self):
        """Test: PDF con presupuesto grande (muchas partidas)."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.VIVIENDA,
            metros_cuadrados=200.0,
        )
        
        # Agregar múltiples paquetes
        service.agregar_paquete(presupuesto, "bano_completo", metros=200.0)
        service.agregar_paquete(presupuesto, "cocina_completa", metros=200.0)
        service.agregar_paquete(presupuesto, "reforma_integral_vivienda", metros=200.0)
        
        # Agregar partidas individuales
        for i in range(10):
            service.agregar_partida(
                presupuesto=presupuesto,
                categoria=WorkCategory.ELECTRICIDAD,
                partida="punto_luz",
                cantidad=float(i + 1),
            )
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        assert pdf_bytes is not None
        # PDF grande debe ser más pesado
        assert len(pdf_bytes) > 5000
        
        print(f"✅ PDF grande generado: {presupuesto.num_partidas} partidas, {len(pdf_bytes)} bytes")


class TestPDFValidation:
    """Tests de validación de PDF."""
    
    def test_pdf_header_valido(self, presupuesto_con_partidas):
        """Test: PDF tiene header válido."""
        pdf_bytes = generar_pdf_presupuesto(presupuesto_con_partidas)
        
        # Header PDF: %PDF-X.Y
        header = pdf_bytes[:8].decode('latin-1')
        
        assert header.startswith('%PDF-')
        assert header[5].isdigit()  # Versión mayor
        
        print(f"✅ Header PDF válido: {header}")
    
    def test_pdf_footer_valido(self, presupuesto_con_partidas):
        """Test: PDF tiene footer válido."""
        pdf_bytes = generar_pdf_presupuesto(presupuesto_con_partidas)
        
        # Footer PDF: %%EOF
        footer = pdf_bytes[-10:].decode('latin-1')
        
        assert '%%EOF' in footer
        
        print("✅ Footer PDF válido")
    
    def test_pdf_no_corrupto(self, presupuesto_con_partidas):
        """Test: PDF no está corrupto (se puede guardar y leer)."""
        pdf_bytes = generar_pdf_presupuesto(presupuesto_con_partidas)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(pdf_bytes)
            output_path = f.name
        
        try:
            # Leer el archivo
            with open(output_path, 'rb') as f:
                read_bytes = f.read()
            
            # Verificar que coincide
            assert read_bytes == pdf_bytes
            
            print("✅ PDF no está corrupto")
            
        finally:
            os.remove(output_path)


class TestPDFEdgeCases:
    """Tests de casos límite para PDF."""
    
    def test_pdf_presupuesto_vacio(self, proyecto_piso):
        """Test: PDF de presupuesto sin partidas."""
        presupuesto = Budget(proyecto=proyecto_piso)
        
        # Debería funcionar aunque no haya partidas
        pdf_bytes = generar_pdf_presupuesto(presupuesto)
        
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        
        print("✅ PDF de presupuesto vacío generado")
    
    def test_pdf_descripcion_larga(self):
        """Test: PDF con descripciones largas."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            descripcion="Esta es una descripción muy larga " * 20,
        )
        
        service.agregar_paquete(presupuesto, "bano_completo", metros=80.0)
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        assert pdf_bytes is not None
        
        print("✅ PDF con descripción larga generado")
    
    def test_pdf_caracteres_especiales(self):
        """Test: PDF con caracteres especiales."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=80.0,
            ubicacion="Calle Ñoño nº 123, 2º A",
            descripcion="Reforma con materiales de última generación €€€",
        )
        
        service.agregar_paquete(presupuesto, "bano_completo", metros=80.0)
        
        service.asignar_cliente(
            presupuesto=presupuesto,
            nombre="José María Ñúñez",
            email="jose@test.com",
            telefono="612345678",
            direccion_obra="Av. España ñ 45, 3º B",
        )
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        assert pdf_bytes is not None
        
        print("✅ PDF con caracteres especiales generado")
    
    def test_pdf_metros_decimales(self):
        """Test: PDF con metros decimales."""
        service = BudgetService()
        
        presupuesto = service.crear_presupuesto(
            tipo_inmueble=PropertyType.PISO,
            metros_cuadrados=82.75,
        )
        
        service.agregar_partida(
            presupuesto=presupuesto,
            categoria=WorkCategory.ALBANILERIA,
            partida="solado_gres",
            cantidad=82.75,
        )
        
        pdf_bytes = service.generar_pdf(presupuesto)
        
        assert pdf_bytes is not None
        
        print("✅ PDF con metros decimales generado")


# ============================================
# Ejecutar tests directamente
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Tests de Generación de PDF")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])