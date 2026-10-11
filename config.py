"""Load PV module reference data from the model catalogue."""

import csv
from contextlib import contextmanager
from pathlib import Path


CSV_FILE = Path(__file__).with_name("pv_models.csv")

REQUIRED_COLUMNS = {
    "model",
    "irradiance",
    "temperature",
    "voc",
    "isc",
    "vmp",
    "imp",
    "pmax",
    "temp_coeff_isc",
    "temp_coeff_voc",
    "temp_coeff_pmax",
    "cell_efficiency",
    "model_efficiency",
    "cells",
}


def _number(row, column):
    """Convert a numeric CSV field and give a useful error for bad data."""
    try:
        return float(row[column])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError(f"Invalid numeric value for '{column}'") from error


@contextmanager
def _open_catalogue(csv_file):
    """Open the catalogue and validate its required columns."""
    with open(csv_file, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"{csv_file} has no header row")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            names = ", ".join(sorted(missing))
            raise ValueError(f"{csv_file} is missing required columns: {names}")
        yield reader


def available_models(csv_file=CSV_FILE):
    """Return the model names available in the CSV catalogue."""
    with _open_catalogue(csv_file) as reader:
        return [row["model"].strip() for row in reader if row["model"].strip()]


def load_model(model_name, csv_file=CSV_FILE):
    """Load one model row and return its values using descriptive keys."""
    requested_name = model_name.strip().casefold()
    with _open_catalogue(csv_file) as reader:
        for row in reader:
            if row["model"].strip().casefold() == requested_name:
                return {
                    "model": row["model"].strip(),
                    "irradiance": _number(row, "irradiance"),
                    "temperature": _number(row, "temperature"),
                    "open_circuit_voltage": _number(row, "voc"),
                    "short_circuit_current": _number(row, "isc"),
                    "max_power_voltage": _number(row, "vmp"),
                    "max_power_current": _number(row, "imp"),
                    "peak_power": _number(row, "pmax"),
                    "temp_coeff_isc": _number(row, "temp_coeff_isc"),
                    "temp_coeff_voc": _number(row, "temp_coeff_voc"),
                    "temp_coeff_pmax": _number(row, "temp_coeff_pmax"),
                    "cell_efficiency": _number(row, "cell_efficiency"),
                    "model_efficiency": _number(row, "model_efficiency"),
                    "cells": int(_number(row, "cells")),
                }

    choices = ", ".join(available_models(csv_file))
    raise ValueError(f"Unknown model '{model_name}'. Available models: {choices}")


def configure(model_name=None, csv_file=CSV_FILE):
    """Select a model and publish its values as module-level configuration."""
    if model_name is None:
        models = available_models(csv_file)
        print("Available PV models:")
        for name in models:
            print(f"- {name}")
        model_name = input("Enter model name: ")

    data = load_model(model_name, csv_file)
    globals().update(data)

    # Existing simulation names retained for compatibility.
    globals().update(
        Model_name = data["model"],
        Peak_Power=data["peak_power"],
        Cells=data["cells"],
        max_power_voltage_V_mp=data["max_power_voltage"],
        I_mp=data["max_power_current"],
        V_oc=data["open_circuit_voltage"],
        I_sc=data["short_circuit_current"],
        Cell_Efficiency=data["cell_efficiency"],
        Module_Efficiency=data["model_efficiency"],
        Temp_Coeff_I_sc=data["temp_coeff_isc"],
        Temp_Coeff_V_oc=data["temp_coeff_voc"],
        Temp_Coeff_P_Max=data["temp_coeff_pmax"],
        irridance_W_m2=data["irradiance"],
    )
    return data


if __name__ == "__main__":
    configure()
    
