"""
Limpieza y normalización de nombres de clientes.

Este script automatiza la estandarización de campos de nombres,
eliminando caracteres no deseados, texto posterior a puntos y
espacios innecesarios, dejando la información lista para análisis
o carga en bases de datos.

Client name cleaning and normalization.

This script automates the standardization of name fields by removing
unwanted characters, text after dots and extra spaces, preparing
the data for analytical or database usage.
"""

import pandas as pd
import re
from pathlib import Path


def limpiar_nombre(nombre: str) -> str:
    """
    Limpia y normaliza un nombre eliminando caracteres no deseados,
    texto posterior a puntos y espacios extra.
    """
    if pd.isna(nombre):
        return ""

    nombre = str(nombre)

    # Eliminar todo lo que esté después de un punto
    nombre = re.sub(r"\..*", "", nombre)

    # Eliminar letras minúsculas y números
    nombre = re.sub(r"[a-z0-9]", "", nombre)

    # Normalizar espacios
    nombre = re.sub(r"\s+", " ", nombre).strip()

    return nombre


def clean_names_file(input_path: Path, output_path: Path, column_name: str) -> None:
    """
    Carga un archivo Excel, limpia la columna de nombres
    y guarda el resultado en un nuevo archivo.
    """
    df = pd.read_excel(input_path)

    if column_name not in df.columns:
        raise ValueError(f"La columna '{column_name}' no existe en el archivo.")

    df[column_name] = df[column_name].apply(limpiar_nombre)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)


def main():
    input_file = Path("data/raw/Limpiezanombres.xlsx")
    output_file = Path("data/processed/Limpiezanombres_clean.xlsx")
    column_name = "NOMBRES"

    clean_names_file(input_file, output_file, column_name)

    print("✅ Limpieza de nombres completada correctamente.")
    print(f"📄 Archivo generado: {output_file}")


if __name__ == "__main__":
    main()
