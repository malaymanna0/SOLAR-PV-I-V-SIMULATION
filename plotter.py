import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq
from pv_model import calculate_parameters

from parameters import BOLTZMANN_CONSTANT, ELECTRON_CHARGE


def pv_equation(
    current,
    voltage,
    photocurrent,
    saturation_current,
    series_resistance,
    shunt_resistance,
    ideality_voltage,
):
    series_voltage = voltage + current * series_resistance
    return (
        photocurrent
        - saturation_current * (np.exp(series_voltage / ideality_voltage) - 1)
        - series_voltage / shunt_resistance
        - current
    )


def plot_iv_curve_reference(model_data, reference_data):
    photocurrent = reference_data["light_generated_current_(I_l)"]
    saturation_current = reference_data["diode_reverse_saturation_current_(I_0)"]
    series_resistance = reference_data["series_resistance_(Rs)"]
    shunt_resistance = reference_data["shunt_resistance_(Rsh)"]
    ideality_voltage = (
        reference_data["diode_ideality_factor_(n)"]
        * model_data["cells"]
        * reference_data["thermal_voltage_(Vth)"]
    )

    voltages = np.linspace(0, model_data["open_circuit_voltage"], 100)
    currents = []

    for voltage in voltages:
        equation = lambda current: pv_equation(
            current,
            voltage,
            photocurrent,
            saturation_current,
            series_resistance,
            shunt_resistance,
            ideality_voltage,
        )
        try:
            current = brentq(equation, 0, photocurrent)
        except ValueError:
            current = np.nan
        currents.append(current)
    power = voltages * currents
    plt.figure()
    plt.plot(voltages, currents, label="Reference")
    plt.plot(voltages, power, label="Power", color="orange")
    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (A)")
    plt.title("Reference I-V Curve")
    plt.grid(True)
    plt.legend()
    plt.savefig("reference_iv_curve.png")
    plt.show()


def plot_iv_curve_condition(model_data, calculated_data):
    figure, current_axis = plt.subplots(figsize=(10, 6))
    power_axis = current_axis.twinx()

    voltages = np.linspace(0, calculated_data["open_circuit_voltage"], 100)
    currents = []

    for voltage in voltages:
        equation = lambda current: pv_equation(
            current,
            voltage,
            calculated_data["light_induced_photocurrent"],
            calculated_data["diode_reverse_saturation_current"],
            calculated_data["series_resistance"],
            calculated_data["shunt_resistance"],
            calculated_data["diode_ideality_voltage"],
        )
        try:
            current = brentq(
                equation,
                0,
                calculated_data["light_induced_photocurrent"],
            )
        except ValueError:
            current = np.nan
        currents.append(current)

    currents = np.asarray(currents)
    power = voltages * currents

    current_axis.plot(
        voltages,
        currents,
        linewidth=2,
        label="Condition - I-V",
    )
    power_axis.plot(
        voltages,
        power,
        linestyle="--",
        linewidth=2,
        label="Condition - P-V",
    )

    current_axis.set_xlabel("Voltage (V)")
    current_axis.set_ylabel("Current (A)")
    power_axis.set_ylabel("Power (W)")
    current_axis.set_title(
        f"Condition I-V and P-V Curve at "
        f"{calculated_data['temperature']}°C and "
        f"{calculated_data['irradiance']} W/m²"
    )
    current_axis.grid(True, alpha=0.3)

    current_handles, current_labels = current_axis.get_legend_handles_labels()
    power_handles, power_labels = power_axis.get_legend_handles_labels()
    current_axis.legend(
        current_handles + power_handles,
        current_labels + power_labels,
        loc="best",
        fontsize=8,
    )

    figure.tight_layout()
    figure.savefig("condition_iv_pv_curve.png", dpi=300)
    plt.show()


def plot_iv_pv_curve_for_irradiance_analysis(irrad_values, results, fixed_temperature=25):
    figure, current_axis = plt.subplots(figsize=(10, 6))
    power_axis = current_axis.twinx()

    for irrad in irrad_values:
        data = results[irrad]
        voltages = np.linspace(0, data["open_circuit_voltage"], 100)
        currents = []
        for voltage in voltages:
            equation = lambda current: pv_equation(
                current,
                voltage,
                data["light_induced_photocurrent"],
                data["diode_reverse_saturation_current"],
                data["series_resistance"],
                data["shunt_resistance"],
                data["diode_ideality_voltage"],
            )
            try:
                current = brentq(equation, 0, data["light_induced_photocurrent"])
            except ValueError:
                current = np.nan
            currents.append(current)
        power = voltages * currents
        current_axis.plot(
            voltages, currents, label=f"Irradiance {irrad} W/m² - I-V"
        )
        power_axis.plot(
            voltages,
            power,
            linestyle="--",
            label=f"Irradiance {irrad} W/m² - P-V",
        )

    current_axis.set_xlabel("Voltage (V)")
    current_axis.set_ylabel("Current (A)")
    power_axis.set_ylabel("Power (W)")
    current_axis.set_title(
        f"I-V and P-V Curves for Different Irradiance Levels "
        f"at {fixed_temperature}°C"
    )
    current_axis.grid(True)
    current_handles, current_labels = current_axis.get_legend_handles_labels()
    power_handles, power_labels = power_axis.get_legend_handles_labels()
    current_axis.legend(
        current_handles + power_handles, current_labels + power_labels
    )
    figure.tight_layout()
    figure.savefig("irradiance_analysis_iv_pv_curves.png")
    plt.show()


def plot_iv_pv_curve_for_temperature_analysis(temp_values, results, fixed_irradiance=1000):
    figure, current_axis = plt.subplots(figsize=(10, 6))
    power_axis = current_axis.twinx()

    for temp in temp_values:
        data = results[temp]
        voltages = np.linspace(0, data["open_circuit_voltage"], 100)
        currents = []
        for voltage in voltages:
            equation = lambda current: pv_equation(
                current,
                voltage,
                data["light_induced_photocurrent"],
                data["diode_reverse_saturation_current"],
                data["series_resistance"],
                data["shunt_resistance"],
                data["diode_ideality_voltage"],
            )
            try:
                current = brentq(equation, 0, data["light_induced_photocurrent"])
            except ValueError:
                current = np.nan
            currents.append(current)
        power = voltages * currents
        current_axis.plot(
            voltages, currents, label=f"Temperature {temp}°C - I-V"
        )
        power_axis.plot(
            voltages,
            power,
            linestyle="--",
            label=f"Temperature {temp}°C - P-V",
        )

    current_axis.set_xlabel("Voltage (V)")
    current_axis.set_ylabel("Current (A)")
    power_axis.set_ylabel("Power (W)")
    current_axis.set_title(
        f"I-V and P-V Curves for Different Temperatures "
        f"at {fixed_irradiance} W/m²"
    )
    current_axis.grid(True)
    current_handles, current_labels = current_axis.get_legend_handles_labels()
    power_handles, power_labels = power_axis.get_legend_handles_labels()
    current_axis.legend(
        current_handles + power_handles, current_labels + power_labels
    )
    figure.tight_layout()
    figure.savefig("temperature_analysis_iv_pv_curves.png")
    plt.show()


def plot_iv_pv_curve_for_combined_analysis(
    irrad_values,
    temp_values,
    model_data,
    reference_data,
    ):
    if len(irrad_values) != len(temp_values):
        raise ValueError(
            "Irradiance and temperature lists must have equal lengths."
        )

    if not irrad_values:
        raise ValueError("At least one condition is required.")

    figure, current_axis = plt.subplots(figsize=(12, 7))
    power_axis = current_axis.twinx()

    for irradiance, temperature in zip(irrad_values, temp_values):

        data = calculate_parameters(
            model_data,
            reference_data,
            irradiance=irradiance,
            temperature=temperature,
            )

        voltages = np.linspace(
            0, data["open_circuit_voltage"], 200
            )

        currents = []

        for voltage in voltages:
            equation = lambda current: pv_equation(
                current,
                voltage,
                data["light_induced_photocurrent"],
                data["diode_reverse_saturation_current"],
                data["series_resistance"],
                data["shunt_resistance"],
                data["diode_ideality_voltage"],
                )

            try:
                current = brentq(
                    equation,
                    0,
                    data["light_induced_photocurrent"],
                    )
            except ValueError:
                current = np.nan

            currents.append(current)

        currents = np.array(currents)
        power = voltages * currents

        label = f"G={irradiance} W/m², T={temperature}°C"

        current_axis.plot(
            voltages,
            currents,
            linewidth=2,
            label=f"I-V ({label})",
            )

        power_axis.plot(
            voltages,
            power,
            linestyle="--",
            linewidth=2,
            label=f"P-V ({label})",
            )

    current_axis.set_xlabel("Voltage (V)")
    current_axis.set_ylabel("Current (A)")
    power_axis.set_ylabel("Power (W)")

    current_axis.set_title(
        "I-V and P-V Characteristics at Different "
        "Irradiance-Temperature Conditions"
        )

    current_axis.grid(True, alpha=0.3)

    handles1, labels1 = current_axis.get_legend_handles_labels()
    handles2, labels2 = power_axis.get_legend_handles_labels()

    current_axis.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="best",
        fontsize=8,
        )

    figure.tight_layout()
    figure.savefig("combined_iv_pv_analysis.png", dpi=300)
    plt.show()
