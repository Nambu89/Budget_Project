"""
Generador de PDF para presupuestos.

Genera documentos PDF profesionales con el presupuesto
completo, incluyendo logo opcional, partidas y disclaimers.
"""

import io
from typing import Optional
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    Table, 
    TableStyle,
    Image,
    PageBreak,
    HRFlowable,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from loguru import logger

from src.config.settings import settings
from src.config.pricing_data import DISCLAIMERS
from src.domain.models.budget import Budget

class PDFGenerator:
    """
    Generador de PDFs para presupuestos.
    
    Crea documentos PDF profesionales con formato
    corporativo y todos los datos del presupuesto.
    """
    
    # Colores corporativos
COLOR_PRIMARIO = colors.HexColor("#F39200")      # Naranja Easy Obras
COLOR_SECUNDARIO = colors.HexColor("#999999")    # Gris
COLOR_ACENTO = colors.HexColor("#F39200")        # Naranja
COLOR_TEXTO = colors.HexColor("#000000")         # Negro
COLOR_TEXTO_CLARO = colors.HexColor("#999999")   # Gris
COLOR_FONDO = colors.HexColor("#FFFFFF")         # Blanco
COLOR_LINEA = colors.HexColor("#999999")         # Gris
    
    def __init__(self):
        """Inicializa el generador de PDF."""
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()
    
    def _crear_estilos_personalizados(self) -> None:
        """Crea estilos personalizados para el PDF."""
        # Título principal
        self.styles.add(ParagraphStyle(
            name='TituloPrincipal',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.COLOR_PRIMARIO,
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        
        # Subtítulo
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.COLOR_SECUNDARIO,
            spaceAfter=10,
            spaceBefore=15,
        ))
        
        # Sección
        self.styles.add(ParagraphStyle(
            name='Seccion',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.COLOR_PRIMARIO,
            spaceAfter=8,
            spaceBefore=12,
            borderColor=self.COLOR_PRIMARIO,
            borderWidth=0,
            borderPadding=0,
        ))
        
        # Texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLOR_TEXTO,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
        ))
        
        # Texto pequeño (disclaimers)
        self.styles.add(ParagraphStyle(
            name='TextoPequeno',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=self.COLOR_TEXTO_CLARO,
            spaceAfter=4,
            alignment=TA_JUSTIFY,
        ))
        
        # Texto derecha
        self.styles.add(ParagraphStyle(
            name='TextoDerecha',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.COLOR_TEXTO,
            alignment=TA_RIGHT,
        ))
        
        # Total grande
        self.styles.add(ParagraphStyle(
            name='TotalGrande',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=self.COLOR_PRIMARIO,
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold',
        ))
    
    def generar_pdf(
        self,
        budget: Budget,
        logo_path: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Genera el PDF del presupuesto.
        
        Args:
            budget: Presupuesto a generar
            logo_path: Ruta al logo (opcional)
            output_path: Ruta de salida (opcional, si no retorna bytes)
            
        Returns:
            bytes: Contenido del PDF si no se especifica output_path
        """
        # Buffer para el PDF
        buffer = io.BytesIO()
        
        # Crear documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm,
        )
        
        # Construir contenido
        elementos = []
        
        # Cabecera con logo
        elementos.extend(self._crear_cabecera(budget, logo_path))
        
        # Datos del proyecto
        elementos.extend(self._crear_seccion_proyecto(budget))
        
        # Datos del cliente (si existen)
        if budget.tiene_cliente:
            elementos.extend(self._crear_seccion_cliente(budget))
        
        # Tabla de partidas
        elementos.extend(self._crear_tabla_partidas(budget))
        
        # Resumen por categorías
        elementos.extend(self._crear_resumen_categorias(budget))
        
        # Totales
        elementos.extend(self._crear_totales(budget))
        
        # Disclaimers
        elementos.extend(self._crear_disclaimers(budget))
        
        # Pie de página
        elementos.extend(self._crear_pie(budget))
        
        # Generar PDF
        doc.build(elementos)
        
        # Obtener bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Guardar si se especificó ruta
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            logger.info(f"PDF guardado en: {output_path}")
        
        return pdf_bytes
    
    def _crear_cabecera(
        self, 
        budget: Budget, 
        logo_path: Optional[str]
    ) -> list:
        """Crea la cabecera del documento."""
        elementos = []
        
        # Logo (si existe)
        if logo_path and Path(logo_path).exists():
            try:
                logo = Image(logo_path, width=4*cm, height=2*cm)
                logo.hAlign = 'LEFT'
                elementos.append(logo)
                elementos.append(Spacer(1, 10))
            except Exception as e:
                logger.warning(f"No se pudo cargar el logo: {e}")
        
        # Título
        elementos.append(Paragraph(
            "PRESUPUESTO DE REFORMA",
            self.styles['TituloPrincipal']
        ))
        
        # Número y fecha
        info_presupuesto = f"""
        <b>Nº Presupuesto:</b> {budget.numero_presupuesto}<br/>
        <b>Fecha emisión:</b> {budget.fecha_emision_str}<br/>
        <b>Válido hasta:</b> {budget.fecha_validez_str}
        """
        elementos.append(Paragraph(info_presupuesto, self.styles['TextoDerecha']))
        
        # Línea separadora
        elementos.append(Spacer(1, 10))
        elementos.append(HRFlowable(
            width="100%",
            thickness=2,
            color=self.COLOR_PRIMARIO,
            spaceBefore=5,
            spaceAfter=15,
        ))
        
        return elementos
    
    def _crear_seccion_proyecto(self, budget: Budget) -> list:
        """Crea la sección de datos del proyecto."""
        elementos = []
        
        elementos.append(Paragraph("📋 DATOS DEL PROYECTO", self.styles['Seccion']))
        
        proyecto = budget.proyecto
        datos = [
            ["Tipo de inmueble:", proyecto.tipo_inmueble_nombre],
            ["Superficie:", f"{proyecto.metros_cuadrados:.2f} m²"],
            ["Nivel de calidad:", proyecto.calidad_nombre],
            ["Estado actual:", proyecto.estado_actual.capitalize()],
            ["Vivienda habitual:", "Sí" if proyecto.es_vivienda_habitual else "No"],
            ["IVA aplicable:", f"{proyecto.iva_aplicable}%"],
        ]
        
        if proyecto.ubicacion:
            datos.append(["Ubicación:", proyecto.ubicacion])
        
        tabla = Table(datos, colWidths=[5*cm, 10*cm])
        tabla.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLOR_TEXTO_CLARO),
            ('TEXTCOLOR', (1, 0), (1, -1), self.COLOR_TEXTO),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 15))
        
        return elementos
    
    def _crear_seccion_cliente(self, budget: Budget) -> list:
        """Crea la sección de datos del cliente."""
        elementos = []
        
        elementos.append(Paragraph("👤 DATOS DEL CLIENTE", self.styles['Seccion']))
        
        cliente = budget.cliente
        datos = [
            ["Nombre:", cliente.nombre],
            ["Email:", cliente.email],
            ["Teléfono:", cliente.telefono_formateado],
        ]
        
        if cliente.direccion_obra:
            datos.append(["Dirección obra:", cliente.direccion_obra])
        
        tabla = Table(datos, colWidths=[5*cm, 10*cm])
        tabla.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLOR_TEXTO_CLARO),
            ('TEXTCOLOR', (1, 0), (1, -1), self.COLOR_TEXTO),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 15))
        
        return elementos
    
    def _crear_tabla_partidas(self, budget: Budget) -> list:
        """Crea la tabla de partidas."""
        elementos = []
        
        elementos.append(Paragraph("📊 DESGLOSE DE PARTIDAS", self.styles['Seccion']))
        
        if not budget.partidas:
            elementos.append(Paragraph(
                "No hay partidas en este presupuesto.",
                self.styles['TextoNormal']
            ))
            return elementos
        
        # Cabecera de la tabla
        datos = [["Descripción", "Ud.", "Cant.", "Precio Ud.", "Subtotal"]]
        
        # Filas de partidas
        for partida in budget.partidas:
            datos.append([
                partida.descripcion[:50] + "..." if len(partida.descripcion) > 50 else partida.descripcion,
                partida.unidad,
                f"{partida.cantidad:.2f}",
                f"{partida.precio_unitario:.2f} €",
                f"{partida.subtotal:.2f} €",
            ])
        
        tabla = Table(datos, colWidths=[8*cm, 1.5*cm, 1.5*cm, 2.5*cm, 2.5*cm])
        tabla.setStyle(TableStyle([
            # Cabecera
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_PRIMARIO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Cuerpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
            
            # Bordes y colores alternos
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLOR_LINEA),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLOR_FONDO]),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 15))
        
        # Añadir desglose de paquetes si los hay
        elementos.extend(self._crear_desglose_paquetes(budget))
        
        return elementos
    
    def _crear_desglose_paquetes(self, budget: Budget) -> list:
        """Crea el desglose detallado de los paquetes incluidos."""
        elementos = []
        
        # Filtrar partidas que son paquetes y tienen items incluidos
        paquetes = [p for p in budget.partidas if p.es_paquete and p.items_incluidos]
        
        if not paquetes:
            return elementos
        
        elementos.append(Paragraph("📦 DETALLE DE PAQUETES INCLUIDOS", self.styles['Seccion']))
        
        for paquete in paquetes:
            # Nombre del paquete
            nombre_paquete = paquete.nombre_paquete or "Paquete"
            elementos.append(Paragraph(
                f"<b>{nombre_paquete}</b> - {paquete.calidad_nombre}",
                self.styles['TextoNormal']
            ))
            elementos.append(Spacer(1, 5))
            
            # Crear tabla con los items incluidos
            datos = [["Concepto incluido"]]
            for item in paquete.items_incluidos:
                datos.append([f"  ✓ {item}"])
            
            tabla = Table(datos, colWidths=[16*cm])
            tabla.setStyle(TableStyle([
                # Cabecera
                ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_SECUNDARIO),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                
                # Cuerpo
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TEXTCOLOR', (0, 1), (-1, -1), self.COLOR_TEXTO),
                
                # Bordes
                ('GRID', (0, 0), (-1, -1), 0.5, self.COLOR_LINEA),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.COLOR_FONDO]),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 1), (-1, -1), 10),
            ]))
            
            elementos.append(tabla)
            elementos.append(Spacer(1, 10))
        
        return elementos
    
    def _crear_resumen_categorias(self, budget: Budget) -> list:
        """Crea el resumen por categorías."""
        elementos = []
        
        resumen = budget.resumen_por_categorias()
        if not resumen:
            return elementos
        
        elementos.append(Paragraph("📈 RESUMEN POR CATEGORÍA", self.styles['Seccion']))
        
        datos = [["Categoría", "Importe"]]
        for categoria, importe in resumen.items():
            datos.append([categoria, f"{importe:,.2f} €"])
        
        tabla = Table(datos, colWidths=[10*cm, 5*cm])
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLOR_SECUNDARIO),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, self.COLOR_LINEA),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 15))
        
        return elementos
    
    def _crear_totales(self, budget: Budget) -> list:
        """Crea la sección de totales."""
        elementos = []
        
        elementos.append(Paragraph("💰 TOTALES", self.styles['Seccion']))
        
        datos = [
            ["Subtotal:", f"{budget.subtotal:,.2f} €"],
        ]
        
        if budget.descuento_porcentaje > 0:
            datos.append([
                f"Descuento ({budget.descuento_porcentaje:.1f}%):",
                f"-{budget.importe_descuento:,.2f} €"
            ])
        
        datos.extend([
            ["Base imponible:", f"{budget.base_imponible:,.2f} €"],
            [f"IVA ({budget.iva_porcentaje}%):", f"{budget.importe_iva:,.2f} €"],
            ["TOTAL:", f"{budget.total:,.2f} €"],
        ])
        
        tabla = Table(datos, colWidths=[10*cm, 5*cm])
        tabla.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -2), 10),
            ('FONTSIZE', (0, -1), (-1, -1), 14),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.COLOR_PRIMARIO),
            ('LINEABOVE', (0, -1), (-1, -1), 2, self.COLOR_PRIMARIO),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elementos.append(tabla)
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def _crear_disclaimers(self, budget: Budget) -> list:
        """Crea la sección de disclaimers legales."""
        elementos = []
        
        elementos.append(HRFlowable(
            width="100%",
            thickness=1,
            color=self.COLOR_LINEA,
            spaceBefore=10,
            spaceAfter=10,
        ))
        
        # Disclaimer principal
        elementos.append(Paragraph(
            DISCLAIMERS["principal"].strip(),
            self.styles['TextoPequeno']
        ))
        
        # Validez
        validez = DISCLAIMERS["validez"].format(dias_validez=budget.dias_validez)
        elementos.append(Paragraph(validez.strip(), self.styles['TextoPequeno']))
        
        # IVA
        iva = DISCLAIMERS["iva"].format(iva_porcentaje=budget.iva_porcentaje)
        elementos.append(Paragraph(iva.strip(), self.styles['TextoPequeno']))
        
        # Forma de pago
        elementos.append(Paragraph(
            DISCLAIMERS["forma_pago"].strip(),
            self.styles['TextoPequeno']
        ))
        
        # Variaciones
        elementos.append(Paragraph(
            DISCLAIMERS["variaciones"].strip(),
            self.styles['TextoPequeno']
        ))
        
        # No incluido
        elementos.append(Paragraph(
            DISCLAIMERS["no_incluido"].strip(),
            self.styles['TextoPequeno']
        ))
        
        # Garantías
        elementos.append(Paragraph(
            DISCLAIMERS["garantias"].strip(),
            self.styles['TextoPequeno']
        ))
        
        # Protección de datos
        elementos.append(Paragraph(
            DISCLAIMERS["proteccion_datos"].strip(),
            self.styles['TextoPequeno']
        ))
        
        return elementos
    
    def _crear_pie(self, budget: Budget) -> list:
        """Crea el pie del documento."""
        elementos = []
        
        elementos.append(Spacer(1, 20))
        elementos.append(HRFlowable(
            width="100%",
            thickness=2,
            color=self.COLOR_PRIMARIO,
            spaceBefore=10,
            spaceAfter=10,
        ))
        
        # Datos de la empresa
        empresa_info = f"""
        <b>{settings.empresa_nombre}</b><br/>
        📞 {settings.empresa_telefono} | 
        ✉️ {settings.empresa_email} | 
        🌐 {settings.empresa_web}
        """
        elementos.append(Paragraph(empresa_info, self.styles['TextoPequeno']))
        
        # Pie final
        elementos.append(Paragraph(
            DISCLAIMERS["pie"].strip(),
            self.styles['TextoPequeno']
        ))
        
        return elementos


def generar_pdf_presupuesto(
    budget: Budget,
    logo_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> bytes:
    """
    Función de conveniencia para generar PDF.
    
    Args:
        budget: Presupuesto a generar
        logo_path: Ruta al logo opcional
        output_path: Ruta de salida opcional
        
    Returns:
        bytes: Contenido del PDF
    """
    generator = PDFGenerator()
    return generator.generar_pdf(budget, logo_path, output_path)