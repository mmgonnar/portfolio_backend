from fpdf import FPDF  # type: ignore[import-not-found]
import os
import re


class BriefPDF(FPDF):

    def footer(self):

        self.set_y(-15)

        # 1. Configuración del Texto (CENTRADO)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        # Dibujamos la celda de la URL centrada
        self.cell(0, 10, "www.mmgonnar.com", ln=0, align="C")

        # 2. Configuración del Logo (INFERIOR DERECHA)
        root_dir = os.getcwd()
        logo_path = os.path.join(root_dir, "assets", "mmgonnar.png")

        if os.path.exists(logo_path):
            # Calculamos la posición X para que esté a la derecha
            # Ancho de página (self.w) - Margen derecho (10) - Ancho del logo (20)
            x_logo = self.w - 10 - 20
            # La Y la ajustamos un poco para que se alinee visualmente con el texto
            y_logo = self.get_y() + 1

            self.image(logo_path, x=x_logo, y=y_logo, w=20)


def generate_brief_pdf(data: dict):
    # Configuración de página tamaño Carta (Letter)
    pdf = BriefPDF(format="letter")
    pdf.set_auto_page_break(auto=True, margin=30)
    pdf.add_page()

    # --- ENCABEZADO ---
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 5, "Brief | Web Design", ln=True)

    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(33, 37, 41)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 12, f"Brief {data.get('projectName', 'General')}", ln=True)

    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y() + 2, 205, pdf.get_y() + 2)
    pdf.ln(10)

    # --- FUNCIÓN DE COLUMNAS MEJORADA ---
    def add_row(label, key):
        value = data.get(key)
        # Limpieza de Enums
        if value is not None and hasattr(value, "value"):
            value = value.value
        # Manejo de listas como 'features'
        if isinstance(value, list):
            value = ", ".join(value)
        # Manejo de booleanos
        if isinstance(value, bool):
            value = "Sí" if value else "No"

        if value is not None and str(value).strip() != "":
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(70, 8, label, ln=0)  # Columna de etiquetas fija[cite: 3]

            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(
                0, 8, f"{value}"
            )  # Columna de valores con separador[cite: 3]
            pdf.ln(1)

    # --- SECCIONES COMPLETAS (Incluyendo campos faltantes del JSON) ---
    sections = [
        (
            "INFORMACIÓN DEL CONTACTO",
            [
                ("Nombre del Contacto", "name"),
                ("Email", "email"),
                ("Teléfono", "phone"),
                ("Empresa", "company"),
            ],
        ),
        (
            "DETALLES DEL PROYECTO",
            [
                ("Tipo de Proyecto", "projectType"),
                ("Nombre del Proyecto", "projectName"),
                ("Descripción de su idea", "projectDescription"),
                ("¿Tiene sitio actual?", "hasExistingSite"),
                ("URL del sitio actual", "existingSiteUrl"),
            ],
        ),
        (
            "FUNCIONALIDADES REQUERIDAS",
            [
                ("Funciones clave", "features"),
                ("Detalle de funciones", "featuresDetail"),
            ],
        ),
        (
            "ESTILO Y AUDIENCIA",
            [
                ("Público objetivo", "targetAudience"),
                ("Competencia", "competitors"),
                ("Estilo Visual", "visualStyle"),
                ("Referencias Visuales", "visualReferences"),
                ("Colores de marca", "brandColors"),
                ("¿Assets listos?", "brandAssetsReady"),
            ],
        ),
        (
            "PRESUPUESTO Y TIEMPOS",
            [
                ("Presupuesto", "budget"),
                ("Tiempo para el proyecto", "timeline"),
                ("¿Presupuesto flexible?", "flexibleBudget"),
                ("Notas adicionales", "additionalNotes"),
            ],
        ),
        (
            "IDIOMA",
            [
                ("Idioma", "locale"),
            ],
        ),
        (
            "ARCHIVOS ADJUNTOS",
            [
                ("Archivos subidos", "files"),
            ],
        ),
    ]

    for section_name, fields in sections:
        pdf.ln(4)
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(0, 10, f"  {section_name}", ln=True, fill=True)
        pdf.ln(2)

        for label, key in fields:
            add_row(label, key)

    # --- GESTIÓN DE ARCHIVO DINÁMICO ---
    if not os.path.exists("temp_briefs"):
        os.makedirs("temp_briefs")

    # Nombre del archivo basado en Empresa -> Proyecto -> Cliente[cite: 3]
    identificador = (
        data.get("company") or data.get("projectName") or data.get("name") or "Brief"
    )
    clean_name = re.sub(r"[^a-zA-Z0-9]", "_", identificador)
    filename = f"temp_briefs/brief_{clean_name}.pdf"

    pdf.output(filename)
    return filename
