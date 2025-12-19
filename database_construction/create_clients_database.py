"""
Construcción de base de datos de pólizas desde archivos HTML.

Este script extrae información estructurada de pólizas desde archivos HTML
y construye una base de datos consolidada en formato Excel, reduciendo
la captura manual y estandarizando la información operativa.

Policy database construction from HTML files.

This script extracts structured policy data from HTML files and builds
a consolidated database in Excel format, enabling operational analysis
and data integration.
"""

import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path


# ---------------------
# FUNCIONES AUXILIARES
# ---------------------
def read_html(file_path: Path) -> BeautifulSoup:
    """
    Lee un archivo HTML y devuelve el objeto BeautifulSoup.
    """
    return BeautifulSoup(file_path.read_text(encoding="utf-8"), "html.parser")


def find_field(soup: BeautifulSoup, label: str) -> str:
    """
    Busca un campo por etiqueta textual y devuelve el valor asociado limpio.
    """
    element = soup.find(string=lambda x: x and label in x)
    if element:
        next_element = element.find_next(["td", "div", "span"])
        if next_element:
            return next_element.get_text(strip=True)
    return ""


def extract_plan(soup: BeautifulSoup) -> str:
    """
    Extrae el plan asegurador priorizando selectores específicos
    y usando búsqueda por texto como respaldo.
    """
    plan_tag = soup.find(id="ctl00_ContentPlaceHolder1_lbDescL")
    if plan_tag and plan_tag.get_text(strip=True):
        return plan_tag.get_text(strip=True)

    plan_text = soup.find(string=lambda x: x and "Plan" in x)
    if plan_text:
        next_element = plan_text.find_next(["td", "div", "span"])
        if next_element:
            value = next_element.get_text(strip=True)
            if value.lower() not in ["planes tradicionales", "plan", "planes"]:
                return value

    return ""


def extract_policy_data(html_file: Path) -> dict:
    """
    Extrae los datos principales de una póliza desde un archivo HTML.
    """
    soup = read_html(html_file)

    return {
        "Archivo": html_file.name,
        "Número de Póliza": find_field(soup, "Póliza"),
        "Tipo de Seguro": find_field(soup, "Tipo de seguro"),
        "Plan": extract_plan(soup),
        "Estatus": find_field(soup, "Estatus"),
        "Suma Asegurada": find_field(soup, "Suma Asegurada"),
        "Moneda": find_field(soup, "Moneda"),
        "Fecha Emisión": find_field(soup, "Fecha Emisión"),
        "Forma de Pago": find_field(soup, "Forma de pago"),
        "Medio de Cobro": find_field(soup, "Medio de cobro"),
        "Banco": find_field(soup, "Banco"),
        "Cuenta / CLABE": find_field(soup, "Número de token/Cuenta CLABE"),
        "Día de Cobro": find_field(soup, "Día de cobro"),
        "Agente": find_field(soup, "Agente"),
        "Correo Agente": find_field(soup, "E-mail"),
        "Teléfono Agente": find_field(soup, "Teléfono"),
        "Contratante": find_field(soup, "Contratante"),
        "Asegurado Principal": find_field(soup, "Asegurado Principal"),
        "Fecha de Nacimiento": find_field(soup, "Fecha de Nacimiento"),
        "Calle y Número": find_field(soup, "Calle y número"),
        "Colonia": find_field(soup, "Colonia"),
        "Ciudad o Municipio": find_field(soup, "Ciudad o Municipio"),
        "Estado": find_field(soup, "Estado"),
        "Código Postal": find_field(soup, "Código postal"),
        "País": find_field(soup, "País"),
        "Correo Electrónico": find_field(soup, "Correo electrónico"),
        "Teléfono Particular": find_field(soup, "Teléfono particular"),
        "Teléfono Oficina": find_field(soup, "Teléfono oficina"),
    }


# ---------------------
# PROCESO PRINCIPAL
# ---------------------
def build_policy_database(input_folder: Path, output_file: Path) -> None:
    records = []

    for html_file in input_folder.glob("*.html"):
        try:
            print(f"🔍 Procesando: {html_file.name}")
            records.append(extract_policy_data(html_file))
        except Exception as error:
            print(f"⚠️ Error procesando {html_file.name}: {error}")

    df = pd.DataFrame(records)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_file, index=False)

    print(f"✅ Base de datos generada: {output_file}")
    print(f"📄 Total de pólizas procesadas: {len(df)}")


def main():
    input_folder = Path("data/raw/html_clientes")
    output_file = Path("data/processed/base_polizas.xlsx")

    build_policy_database(input_folder, output_file)


if __name__ == "__main__":
    main()
