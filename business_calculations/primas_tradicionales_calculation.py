"""
Extracción de primas desde archivos HTML para productos tradicionales.

Este script automatiza la extracción de información clave (número de póliza
y prima al cobro) desde archivos HTML, transformando datos no estructurados
en información lista para análisis y procesos operativos.

Traditional products premium extraction from HTML files.

This script extracts policy numbers and premium amounts from HTML files,
converting unstructured data into structured outputs for operational
and analytical use.
"""

import os
from pathlib import Path
from bs4 import BeautifulSoup
from openpyxl import Workbook


# ---------------------
# CONFIGURACIÓN GENERAL
# ---------------------
PREMIUM_COLUMN_INDEX = 17  # Columna 18 en HTML (índice base 0)


# ---------------------
# FUNCIONES AUXILIARES
# ---------------------
def read_html_file(file_path: Path) -> str:
    """
    Lee un archivo HTML intentando distintos encodings.
    """
    try:
        return file_path.read_text(encoding="latin-1")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="utf-8")


def extract_premium_data(html_content: str, file_name: str) -> tuple | None:
    """
    Extrae número de póliza y prima al cobro desde el contenido HTML.
    Solo se toma la primera fila válida.
    """
    soup = BeautifulSoup(html_content, "lxml")
    rows = soup.find_all("tr", class_="GridRow")

    for row in rows:
        policy_link = row.find("a", id=lambda x: x and "lnkPoliza" in x)
        if not policy_link:
            continue

        policy_number = policy_link.text.strip()
        cells = row.find_all("td")

        premium = ""
        if len(cells) > PREMIUM_COLUMN_INDEX:
            premium = cells[PREMIUM_COLUMN_INDEX].get_text(strip=True)

        return file_name, policy_number, premium

    return None


# ---------------------
# PROCESO PRINCIPAL
# ---------------------
def process_html_folder(input_folder: Path, output_file: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Primas Tradicionales"
    ws.append(["Archivo", "No. Póliza", "Prima al Cobro"])

    for html_file in input_folder.iterdir():
        if html_file.suffix.lower() != ".html":
            continue

        html_content = read_html_file(html_file)
        result = extract_premium_data(html_content, html_file.name)

        if result:
            ws.append(result)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_file)

    print(f"✅ Archivo generado exitosamente: {output_file}")


def main():
    input_folder = Path("data/raw/html_tradicional")
    output_file = Path("data/processed/polizas_prima_al_cobro.xlsx")

    process_html_folder(input_folder, output_file)


if __name__ == "__main__":
    main()
