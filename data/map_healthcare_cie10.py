from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEFAULT_HEALTHCARE_FILE = Path("data/healthcare_dataset.csv")
DEFAULT_CIE10_FILE = Path("data/cie10.csv")
DEFAULT_OUTPUT_FILE = Path("data/healthcare_dataset_mapped.csv")

CONDITION_TO_CIE10 = {
    "arthritis": "M139",
    "asthma": "J45",
    "cancer": "C80",
    "diabetes": "E11",
    "hypertension": "I10",
    "obesity": "E66",
}


def normalize_condition(value: str) -> str:
    return " ".join(value.strip().casefold().split())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def map_healthcare(
    healthcare_file: Path,
    cie10_file: Path,
    output_file: Path,
) -> None:
    healthcare_rows = read_csv(healthcare_file)
    cie10_rows = read_csv(cie10_file)

    if not healthcare_rows:
        raise ValueError(f"El archivo principal no contiene registros: {healthcare_file}")
    if not cie10_rows:
        raise ValueError(f"El catálogo CIE-10 no contiene registros: {cie10_file}")
    if "Medical Condition" not in healthcare_rows[0]:
        raise ValueError("El archivo principal debe contener la columna 'Medical Condition'.")
    if not {"codigo", "diagnostico"}.issubset(cie10_rows[0]):
        raise ValueError("El catálogo CIE-10 debe contener las columnas 'codigo' y 'diagnostico'.")

    valid_codes = {row["codigo"].strip() for row in cie10_rows}
    invalid_mapping = {
        condition: code
        for condition, code in CONDITION_TO_CIE10.items()
        if code not in valid_codes
    }
    if invalid_mapping:
        raise ValueError(f"Hay códigos del mapeo que no existen en el catálogo: {invalid_mapping}")

    mapped_rows: list[dict[str, str]] = []
    for row in healthcare_rows:
        condition = normalize_condition(row["Medical Condition"])
        code = CONDITION_TO_CIE10.get(condition, "")

        mapped_row = dict(row)
        mapped_row["Codigo_CIE10"] = code
        mapped_rows.append(mapped_row)

    output_fields = list(healthcare_rows[0]) + ["Codigo_CIE10"]
    write_csv(output_file, mapped_rows, output_fields)

    print(f"Registros procesados: {len(mapped_rows)}")
    print(f"Registros con Codigo_CIE10: {sum(bool(row['Codigo_CIE10']) for row in mapped_rows)}")
    print(f"Salida principal: {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agrega Codigo_CIE10 a healthcare_dataset.csv y valida la FK contra cie10.csv."
    )
    parser.add_argument("--healthcare", type=Path, default=DEFAULT_HEALTHCARE_FILE)
    parser.add_argument("--cie10", type=Path, default=DEFAULT_CIE10_FILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_FILE)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    map_healthcare(
        arguments.healthcare,
        arguments.cie10,
        arguments.output,
    )