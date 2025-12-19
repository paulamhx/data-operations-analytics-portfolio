"""
Automatización de cálculo de renovaciones y amparos para pólizas GMM y Tradicional.

Este script procesa información de pólizas desde Excel, calcula fechas de renovación
según la forma de pago (mensual, bimestral, trimestral, semestral o anual) y genera
fechas de amparo basadas en reglas de negocio, reduciendo la intervención manual
en procesos operativos.

GMM and Traditional policy renewal automation.

This script processes policy data from Excel, calculates renewal dates based on
payment frequency and generates grace period dates, automating complex operational
workflows.
"""

import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pathlib import Path


# ---------------------
# CONFIGURACIÓN GENERAL
# ---------------------
START_YEAR = 2025
END_YEAR = 2026

START_DATE = datetime(START_YEAR, 1, 1)
END_DATE = datetime(END_YEAR, 12, 31)


# ---------------------
# FUNCIONES AUXILIARES
# ---------------------
def parse_issue_date(value: str) -> datetime:
    """
    Convierte valores de Fecha Emisión a datetime soportando múltiples formatos.
    """
    value = str(value).strip()
    if not value:
        raise ValueError("Fecha Emisión vacía")

    formats = ["%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return pd.to_datetime(value, dayfirst=True, errors="raise").to_pydatetime()


def adjust_day(year: int, month: int, day: int) -> datetime:
    """
    Ajusta el día al último día del mes si el día solicitado no existe.
    """
    base = datetime(year, month, 1)
    last_day = (base + relativedelta(day=31)).day
    return base.replace(day=min(day, last_day))


def get_payment_day(issue_date: datetime, payment_day) -> int:
    """
    Regla de negocio:
    - Si hay Día de Cobro, se utiliza.
    - Si no, se toma el día de la Fecha Emisión.
    """
    try:
        payment_day = int(payment_day)
        return payment_day if payment_day > 0 else issue_date.day
    except Exception:
        return issue_date.day


def generate_dates(issue_date: datetime, payment_day: int, step: int) -> list:
    """
    Genera fechas de renovación con un intervalo en meses.
    """
    dates = []
    year = START_YEAR
    month = issue_date.month
    current = adjust_day(year, month, payment_day)

    while current < START_DATE:
        month += step
        if month > 12:
            month -= 12
            year += 1
        current = adjust_day(year, month, payment_day)

    while current <= END_DATE:
        dates.append(current)
        month += step
        if month > 12:
            month -= 12
            year += 1
        current = adjust_day(year, month, payment_day)

    return dates


def generate_annual_dates(issue_date: datetime, payment_day: int) -> list:
    dates = []
    for year in [START_YEAR, END_YEAR]:
        date = adjust_day(year, issue_date.month, payment_day)
        if START_DATE <= date <= END_DATE:
            dates.append(date)
    return dates


def generate_grace_periods(renewal_date: datetime) -> tuple:
    """
    Calcula amparos de 30 y 45 días desde la fecha de renovación.
    """
    return (
        renewal_date + timedelta(days=30),
        renewal_date + timedelta(days=45),
    )


# ---------------------
# PROCESO PRINCIPAL
# ---------------------
def process_file(input_path: Path, output_path: Path) -> None:
    df = pd.read_excel(input_path, dtype={"Fecha Emisión": str})

    issue_dates = df["Fecha Emisión"].astype(str).apply(parse_issue_date)

    payment_columns = {
        "mensual": (24, 1),
        "bimestral": (12, 2),
        "trimestral": (8, 3),
        "semestral": (4, 6),
        "anual": (2, 12),
    }

    for freq, (count, _) in payment_columns.items():
        for i in range(count):
            df[f"{freq.capitalize()}_{i+1}"] = ""

    df["Fecha Renovación"] = ""
    df["Amparo_30_días"] = ""
    df["Amparo_15_días"] = ""

    for idx, row in df.iterrows():
        issue_date = issue_dates.iloc[idx]
        payment_day = get_payment_day(issue_date, row["Día de Cobro"])
        frequency = str(row["Forma de Pago"]).strip().lower()

        if frequency not in payment_columns:
            raise ValueError(f"Forma de Pago desconocida en fila {idx + 1}")

        count, step = payment_columns[frequency]

        dates = (
            generate_annual_dates(issue_date, payment_day)
            if frequency == "anual"
            else generate_dates(issue_date, payment_day, step)
        )

        if not dates:
            raise ValueError(f"No se generaron fechas en la fila {idx + 1}")

        renewal_date = dates[0]
        df.at[idx, "Fecha Renovación"] = renewal_date.strftime("%d/%m/%Y")

        g30, g15 = generate_grace_periods(renewal_date)
        df.at[idx, "Amparo_30_días"] = g30.strftime("%d/%m/%Y")
        df.at[idx, "Amparo_15_días"] = g15.strftime("%d/%m/%Y")

        for i, date in enumerate(dates[:count]):
            df.at[idx, f"{frequency.capitalize()}_{i+1}"] = date.strftime("%d/%m/%Y")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)

    print(f"✅ Archivo generado exitosamente: {output_path}")


def main():
    input_file = Path("data/raw/Renovaciones_GMM_Tradicional.xlsx")
    output_file = Path("data/processed/Renovaciones_GMM_Tradicional_processed.xlsx")

    process_file(input_file, output_file)


if __name__ == "__main__":
    main()
