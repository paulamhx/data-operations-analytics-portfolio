"""
Cálculo de primas y renovaciones para productos flexibles.

Este script implementa reglas de negocio para el cálculo de fechas de
renovación, esquemas de pago (mensual, trimestral, semestral y anual)
y periodos de amparo para productos flexibles, automatizando procesos
operativos previamente manuales.

Flexible products premium and renewal calculation.

This script applies business rules to calculate renewal dates,
payment schedules and grace periods for flexible products,
reducing manual operational effort.
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
def adjust_day(base_date: datetime, day: int) -> datetime:
    """
    Ajusta el día al último día del mes si el día solicitado no existe.
    """
    last_day = (base_date + relativedelta(day=31)).day
    return base_date.replace(day=min(day, last_day))


def generate_monthly_flex(issue_date: datetime, payment_day: int) -> list:
    """
    Genera pagos mensuales para productos flexibles.
    """
    dates = []

    renewal = datetime(START_YEAR, issue_date.month, issue_date.day)
    if START_DATE <= renewal <= END_DATE:
        dates.append(renewal)

    day_to_use = payment_day if payment_day > 0 else renewal.day

    year, month = renewal.year, renewal.month + 1
    if month > 12:
        month, year = 1, year + 1

    while True:
        current = adjust_day(datetime(year, month, 1), day_to_use)
        if current > END_DATE:
            break
        if current >= START_DATE:
            dates.append(current)

        month += 1
        if month > 12:
            month, year = 1, year + 1

    return dates


def generate_semiannual(issue_date: datetime, payment_day: int) -> list:
    """
    Genera pagos semestrales (enero y julio).
    """
    day_to_use = payment_day if payment_day > 0 else issue_date.day
    dates = []

    for year in [START_YEAR, END_YEAR]:
        for month in [1, 7]:
            date = adjust_day(datetime(year, month, 1), day_to_use)
            if START_DATE <= date <= END_DATE:
                dates.append(date)

    return dates[:2]


def generate_quarterly(issue_date: datetime, payment_day: int) -> list:
    """
    Genera pagos trimestrales (enero, abril, julio, octubre).
    """
    day_to_use = payment_day if payment_day > 0 else issue_date.day
    dates = []

    for year in [START_YEAR, END_YEAR]:
        for month in [1, 4, 7, 10]:
            date = adjust_day(datetime(year, month, 1), day_to_use)
            if START_DATE <= date <= END_DATE:
                dates.append(date)

    return dates[:4]


def generate_annual(issue_date: datetime) -> datetime | None:
    """
    Genera pago anual en la fecha de emisión.
    """
    renewal = datetime(START_YEAR, issue_date.month, issue_date.day)
    return renewal if START_DATE <= renewal <= END_DATE else None


def generate_grace_periods(renewal_date: datetime) -> tuple:
    """
    Calcula amparos de 30 y 45 días desde la renovación.
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

    issue_dates = pd.to_datetime(
        df["Fecha Emisión"].astype(str).str.strip(),
        dayfirst=True,
        errors="raise",
    )

    monthly_cols = [f"Mensual_{i+1}" for i in range(25)]
    semiannual_cols = ["Semestral_1", "Semestral_2"]
    quarterly_cols = ["Trimestral_1", "Trimestral_2", "Trimestral_3", "Trimestral_4"]
    annual_col = "Anual"
    grace_cols = ["Amparo_30_días", "Amparo_15_días"]

    df["Fecha Renovación"] = ""
    for col in monthly_cols + semiannual_cols + quarterly_cols + [annual_col] + grace_cols:
        df[col] = ""

    for idx, row in df.iterrows():
        issue_date = issue_dates.iloc[idx]

        payment_day = row.get("Día de Cobro", 0)
        payment_day = int(payment_day) if pd.notna(payment_day) else 0

        payment_type = str(row["Forma de Pago"]).strip().lower()

        renewal_date = datetime(START_YEAR, issue_date.month, issue_date.day)
        df.at[idx, "Fecha Renovación"] = renewal_date.strftime("%d-%m-%Y")

        g30, g15 = generate_grace_periods(renewal_date)
        df.at[idx, "Amparo_30_días"] = g30.strftime("%d-%m-%Y")
        df.at[idx, "Amparo_15_días"] = g15.strftime("%d-%m-%Y")

        if payment_type == "mensual":
            dates = generate_monthly_flex(issue_date, payment_day)
            for i, d in enumerate(dates[: len(monthly_cols)]):
                df.at[idx, monthly_cols[i]] = d.strftime("%d-%m-%Y")

        elif payment_type == "semestral":
            for i, d in enumerate(generate_semiannual(issue_date, payment_day)):
                df.at[idx, semiannual_cols[i]] = d.strftime("%d-%m-%Y")

        elif payment_type == "trimestral":
            for i, d in enumerate(generate_quarterly(issue_date, payment_day)):
                df.at[idx, quarterly_cols[i]] = d.strftime("%d-%m-%Y")

        elif payment_type == "anual":
            annual_date = generate_annual(issue_date)
            if annual_date:
                df.at[idx, annual_col] = annual_date.strftime("%d-%m-%Y")

        else:
            raise ValueError(f"Forma de pago no soportada en fila {idx + 1}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False)

    print(f"✅ Archivo generado exitosamente: {output_path}")


def main():
    input_file = Path("data/raw/Renovaciones_Flexibles.xlsx")
    output_file = Path("data/processed/Renovaciones_Flexibles_processed.xlsx")

    process_file(input_file, output_file)


if __name__ == "__main__":
    main()
