from config import configure
from parameters import extract_reference_parameters
from pv_model import calculate_parameters
from template import simulation_template, irradiance_analysis_template, temperature_analysis_template, curve_template, menu, combined_analysis_template
import sys

def main():
    model_data = configure()
    reference_data = extract_reference_parameters(model_data)
    try:
        irradiance = float(input("Enter irradiance (W/m^2): "))
        temperature = float(input("Enter temperature (C): "))
    except ValueError:
        pass
    calculated_data = calculate_parameters(
        model_data, reference_data, irradiance = irradiance, temperature = temperature
    )
    simulation_template(
        model_data,
        reference_data,
        calculated_data,
        irradiance=irradiance,
        temperature=temperature,
    )
    while True:
        menu()
        try:
            response_1 = int(input("\nEnter your choice : _"))
        except ValueError:
            print("Invalid input. Please enter a number.")
            continue

        match response_1:
            case 1:
                curve_template(model_data, calculated_data, irradiance=irradiance, temperature=temperature)
            case 2:
                irradiance_analysis_template(model_data, reference_data)
            case 3:
                temperature_analysis_template(model_data, reference_data)
            case 4:
                combined_analysis_template(model_data, reference_data)
            case 5:
                main()
            case 6:
                sys.exit("Thank You!")
            case _:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()