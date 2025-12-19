"""
Main entry point for data processing and automation workflows.

This script orchestrates the execution of data cleaning,
business calculations, and database construction processes,
serving as the central control for the project.

Author: Ana Paula Marhx
"""

from pathlib import Path

# Data Cleaning
from data_cleaning.clean_names import clean_names_file

# Business Calculations
from business_calculation.flex_calculation import run_flex_calculation
from business_calculation.tradicional_calculation import run_traditional_calculation

# Database Construction
from database_construction.html_to_database_builder import build_policy_database


# ---------------------
# PATH CONFIGURATION
# ---------------------
BASE_DIR = Path(__file__).resolve().parent

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"


# ---------------------
# PIPELINE STEPS
# ---------------------
def run_data_cleaning():
    print("\n🧹 Running data cleaning...")

    input_file = DATA_RAW / "Limpiezanombres.xlsx"
    output_file = DATA_PROCESSED / "Limpiezanombres_clean.xlsx"
    column_name = "NOMBRES"

    clean_names_file(input_file, output_file, column_name)


def run_business_calculations():
    print("\n📊 Running business calculations...")

    run_flex_calculation()
    run_traditional_calculation()


def run_database_construction():
    print("\n🗄️ Building policy database from HTML files...")

    html_folder = DATA_RAW / "html_clientes"
    output_file = DATA_PROCESSED / "base_polizas.xlsx"

    build_policy_database(html_folder, output_file)


# ---------------------
# MAIN EXECUTION
# ---------------------
def main():
    print("🚀 Starting data automation pipeline...\n")

    run_data_cleaning()
    run_business_calculations()
    run_database_construction()

    print("\n✅ Pipeline completed successfully.")


if __name__ == "__main__":
    main()
