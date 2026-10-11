from plotter import plot_simulation_curve, plot_iv_pv_curve_for_irradiance_analysis, plot_iv_pv_curve_for_temperature_analysis, plot_iv_pv_curve_for_combined_analysis
from pv_model import calculate_parameters


def irradiance_analysis_template(model_data, reference_data, fixed_temperature=25):
    """Display the irradiance analysis report for a set of input irradiance values."""

    print("=" * 59)
    print(f"{'IRRADIANCE ANALYSIS':^59}")
    print("=" * 59)
    print()
    print(f"Fixed Cell Temperature : {fixed_temperature} °C")
    print()
    print("Enter irradiance values")
    print("Example: 200 400 600 800 1000")
    irrad_values = [int(x) for x in input("Irradiance (W/m²) : ").split()]
    if any(value <= 0 for value in irrad_values):
        raise ValueError("Irradiance values must be greater than zero")
    results = {
        value: calculate_parameters(
            model_data, reference_data, irradiance=value, temperature=fixed_temperature
        )
        for value in irrad_values
    }
    print()
    print(f"Irradiance (W/m²) : {', '.join(str(v) for v in irrad_values)}")
    print()
    print("-" * 60)
    print("Generating simulations...")
    print("-" * 60)
    print()
    print(f"{'G (W/m²)':<15} {'Isc (A)':<15} {'Voc (V)':<15} {'Pmax (W)':<15}")
    print("-" * 60)

    for value in irrad_values:
        item = results.get(value)
        if item is None:
            isc = 0.0
            voc = 0.0
            pmax = 0.0
        else:
            isc = item["short_circuit_current"]
            voc = item["open_circuit_voltage"]
            pmax = item["max_power"]

        print(f"{value:<15} {isc:>7.2f} {voc:>12.2f} {pmax:>12.2f}")

    print("-" * 60)
    print("Generating I-V and P-V curves...")
    plot_iv_pv_curve_for_irradiance_analysis(irrad_values, results, fixed_temperature)
    print()
    


def temperature_analysis_template(model_data, reference_data, fixed_irradiance=1000):
    """Display the temperature analysis report for a set of input temperature values."""

    print("=" * 59)
    print(f"{'TEMPERATURE ANALYSIS':^59}")
    print("=" * 59)
    print()
    print(f"Fixed Irradiance : {fixed_irradiance} W/m²")
    print()
    print("Enter temperature values")
    print("Example: -10 0 10 20 30 40 50")
    temp_values = [int(x) for x in input("Temperature (°C) : ").split()]
    if any(value < -273.15 for value in temp_values):
        raise ValueError("Temperature values must be above absolute zero (-273.15 °C)")
    results = {
        value: calculate_parameters(
            model_data, reference_data, irradiance=fixed_irradiance, temperature=value
        )
        for value in temp_values
    }
    print()
    print(f"Temperature (°C) : {', '.join(str(v) for v in temp_values)}")
    print()
    print("-" * 60)
    print("Generating simulations...")
    print("-" * 60)
    print()
    print(f"{'T (°C)':<15} {'Isc (A)':<15} {'Voc (V)':<15} {'Pmax (W)':<15}")
    print("-" * 60)

    for value in temp_values:
        item = results.get(value)
        if item is None:
            isc = 0.0
            voc = 0.0
            pmax = 0.0
        else:
            isc = item["short_circuit_current"]
            voc = item["open_circuit_voltage"]
            pmax = item["max_power"]

        print(f"{value:<15} {isc:>7.2f} {voc:>12.2f} {pmax:>12.2f}")

    print("-" * 60)
    print("Generating I-V and P-V curves...")
    plot_iv_pv_curve_for_temperature_analysis(temp_values, results, fixed_irradiance)
    print()

def curve_template(model_data, reference_data, calculated_data, irradiance=1000, temperature=25):
    """Display the curve analysis screen for I-V and P-V simulation results."""

    isc = calculated_data["short_circuit_current"]
    voc = calculated_data["open_circuit_voltage"]
    vmp = calculated_data["max_power_voltage"]
    imp = calculated_data["max_power_current"]
    pmax = calculated_data["max_power"]

    print("=" * 56)
    print(f"{'CURVE ANALYSIS':^56}")
    print("=" * 56)
    print()
    print("Simulation Condition")
    print("-" * 60)
    print(f"Irradiance         : {irradiance} W/m²")
    print(f"Temperature        : {temperature} °C")
    print()
    print("Generating I-V curve...")
    print("Generating P-V curve...")
    print("Finding Maximum Power Point...")
    print("-" * 60)
    print()
    print("I-V CHARACTERISTICS")
    print("-" * 60)
    print(f"Isc                : {isc:.2f} A")
    print(f"Voc                : {voc:.2f} V")
    print()
    print("P-V CHARACTERISTICS")
    print("-" * 60)
    print(f"Vmp                : {vmp:.2f} V")
    print(f"Imp                : {imp:.2f} A")
    print(f"Pmax               : {pmax:.2f} W")
    print("-" * 60)
    print()
    print("Opening I-V and P-V plots...")
    plot_simulation_curve(model_data, reference_data, calculated_data)
    print()
    try:
        input("[Press ENTER to return to menu]")
    except EOFError:
        pass
    menu()

def combined_analysis_template(model_data, reference_data):
    """Display simulation results for combinations of irradiance and temperature."""

    print("=" * 59)
    print(f"{'COMBINED IRRADIANCE & TEMPERATURE ANALYSIS':^59}")
    print("=" * 59)
    print()
    print("Enter irradiance values")
    print("Example: 400 600 800 1000")

    irrad_values = [
        int(x) for x in input("Irradiance (W/m²) : ").split()
    ]

    if not irrad_values or any(value <= 0 for value in irrad_values):
        raise ValueError("Irradiance values must be greater than zero")

    print()
    print("Enter temperature values")
    print("Example: 15 25 35 45 55")

    temp_values = [
        float(x) for x in input("Temperature (°C) : ").split()
    ]

    if not temp_values or any(value <= -273.15 for value in temp_values):
        raise ValueError("Temperature must be above -273.15 °C")

    results = {
        (irradiance, temperature): calculate_parameters(
            model_data,
            reference_data,
            irradiance=irradiance,
            temperature=temperature
        )
        for irradiance in irrad_values
        for temperature in temp_values
    }

    print()
    print("-" * 75)
    print("Generating simulations...")
    print("-" * 75)
    print()

    print(
        f"{'G (W/m²)':<15} {'T (°C)':<12} "
        f"{'Isc (A)':<15} {'Voc (V)':<15} {'Pmax (W)':<15}"
    )
    print("-" * 75)

    for (irradiance, temperature), item in results.items():
        isc = item["short_circuit_current"]
        voc = item["open_circuit_voltage"]
        pmax = item["max_power"]

        print(
            f"{irradiance:<15} {temperature:<12.1f} "
            f"{isc:>7.2f} {voc:>12.2f} {pmax:>12.2f}"
        )

    print("-" * 75)
    print()
    plot_iv_pv_curve_for_combined_analysis(irrad_values, temp_values, model_data, reference_data)



def simulation_template(
    model_data, reference_data, calculated_data, irradiance=1000, temperature=25
):
    """Display the formatted simulation report and analysis menu."""

    width = 60
    separator = "-" * width
    print("=" * width)
    print(f"{'SOLAR PV I-V SIMULATOR':^{width}}")
    print(f"{'Single-Diode + De Soto Model':^{width}}")
    print("=" * width)

    print("\nMODULE")
    print(separator)
    print(f"{'Model':<19} : {model_data['model']}")
    print(f"{'Rated Power':<19} : {model_data['peak_power']} Wp")
    print(f"{'Cells in Series':<19} : {model_data['cells']}")

    print("\nREFERENCE CONDITIONS")
    print(separator)
    print(f"{'Irradiance':<19} : {model_data['irradiance']} W/m²")
    print(f"{'Temperature':<19} : {model_data['temperature']} °C")
    print()
    print(f"{'Voc':<19} : {model_data['open_circuit_voltage']:.2f} V")
    print(f"{'Isc':<19} : {model_data['short_circuit_current']:.2f} A")
    print(f"{'Vmp':<19} : {model_data['max_power_voltage']:.2f} V")
    print(f"{'Imp':<19} : {model_data['max_power_current']:.2f} A")
    print(f"{'Pmax':<19} : {model_data['peak_power']:.2f} W")
    print(separator)

    print("\nCALCULATED MODEL PARAMETERS")
    print(separator)
    print(f"{'IL':<19} : {reference_data['light_generated_current_(I_l)']:.4f} A")
    print(f"{'I0':<19} : {reference_data['diode_reverse_saturation_current_(I_0)']:.4e} A")
    print(f"{'Rs':<19} : {reference_data['series_resistance_(Rs)']:.4f} Ω")
    print(f"{'Rsh':<19} : {reference_data['shunt_resistance_(Rsh)']:.4f} Ω")
    print(f"{'a_ref':<19} : {reference_data['model_ideality_factor_(a)']:.4f} V")
    print(f"{'n':<19} : {reference_data['diode_ideality_factor_(n)']:.4f}")
    print(separator)

    print("\nSIMULATION CONDITION")
    print(separator)
    print(f"{'Irradiance':<19} : {irradiance} W/m²")
    print(f"{'Temperature':<19} : {temperature} °C")
    print(separator)

    print("\nSIMULATED MODEL PARAMETERS")
    print(separator)
    print(f"{'IL':<19} : {calculated_data['light_induced_photocurrent']:.4f} A")
    print(f"{'I0':<19} : {calculated_data['diode_reverse_saturation_current']:.4e} A")
    print(f"{'Rs':<19} : {calculated_data['series_resistance']:.4f} Ω")
    print(f"{'Rsh':<19} : {calculated_data['shunt_resistance']:.4f} Ω")
    print(f"{'a':<19} : {calculated_data['model_ideality_factor']:.4f} V")
    print(separator)

    fill_factor = (
        calculated_data["max_power"]
        / (
            calculated_data["open_circuit_voltage"]
            * calculated_data["short_circuit_current"]
        )
        * 100
    )
    print("\nSIMULATED RESULTS")
    print(separator)
    print(
        f"{'Short Circuit Current (Isc)':<28} : "
        f"{calculated_data['short_circuit_current']:.2f} A"
    )
    print(
        f"{'Open Circuit Voltage (Voc)':<28} : "
        f"{calculated_data['open_circuit_voltage']:.2f} V"
    )
    print(
        f"{'Maximum Power Voltage (Vmp)':<28} : "
        f"{calculated_data['max_power_voltage']:.2f} V"
    )
    print(
        f"{'Maximum Power Current (Imp)':<28} : "
        f"{calculated_data['max_power_current']:.2f} A"
    )
    print(f"{'Maximum Power (Pmax)':<28} : {calculated_data['max_power']:.2f} W")
    print(f"{'Fill Factor (FF)':<28} : {fill_factor:.2f} %")
    print(separator)

def menu():
    width = 60
    separator = "-" * width
    print(f"\n{'ANALYSIS MENU':^{width}}")
    print(separator)
    print("1. Show I-V / P-V Curves")
    print("2. Irradiance Analysis")
    print("3. Temperature Analysis")
    print("4. Combined Analysis")
    print("5. Change Simulation Condition")
    print("6. Exit")
    print("-" * width)
    
    