"""Calculate single-diode parameters away from catalogue reference conditions."""

from math import exp, log

from parameters import BOLTZMANN_CONSTANT, ELECTRON_CHARGE
from config import configure
from parameters import extract_reference_parameters

def calculate_iv_characteristics(
		irradiance, temperature, model_data, reference_data, calculated_parameters
):
	"""Calculate Isc, Voc, Vmp, Imp, and Pmax for the requested conditions.

	The catalogue has no Vmp or Imp temperature coefficients, so the Voc and
	Isc coefficients are used as proxies for those respective coefficients.
	"""
	if irradiance <= 0:
		raise ValueError("Irradiance must be greater than zero")
	if reference_data["irradiance_(G)"] <= 0:
		raise ValueError("Reference irradiance must be greater than zero")

	temperature_delta = temperature - model_data["temperature"]
	temperature_kelvin = temperature + 273.15
	irradiance_ratio = irradiance / reference_data["irradiance_(G)"]
	light_generated_current = calculated_parameters["light_induced_photocurrent"]
	saturation_current = calculated_parameters["diode_reverse_saturation_current"]
	if light_generated_current < 0 or saturation_current <= 0:
		raise ValueError("Photocurrent must be non-negative and saturation current positive")

	short_circuit_current = light_generated_current
	thermal_voltage = BOLTZMANN_CONSTANT * temperature_kelvin / ELECTRON_CHARGE
	diode_ideality_voltage = (
		reference_data["diode_ideality_factor_(n)"]
		* model_data["cells"]
		* thermal_voltage
	)
	open_circuit_voltage = diode_ideality_voltage * log(
		light_generated_current / saturation_current + 1
	)

	max_power_voltage_ref = model_data["max_power_voltage"]
	max_power_current_ref = model_data["max_power_current"]
	max_power_voltage = max_power_voltage_ref * (
		1 + model_data["temp_coeff_voc"] * temperature_delta
	) + max_power_voltage_ref * log(irradiance_ratio)
	max_power_current = max_power_current_ref * irradiance_ratio * (
		1 + model_data["temp_coeff_isc"] * temperature_delta
	)
	max_power = max_power_voltage * max_power_current

	return {
		"short_circuit_current": short_circuit_current,
		"open_circuit_voltage": open_circuit_voltage,
		"max_power_voltage": max_power_voltage,
		"max_power_current": max_power_current,
		"max_power": max_power,
	}


def calculate_parameters(model_data, reference_data, irradiance=1000, temperature=25):
	"""Return model parameters for irradiance in W/m2 and temperature in Celsius."""
	if irradiance < 0:
		raise ValueError("Irradiance must be greater than zero")

	temperature_kelvin = temperature + 273.15
	t_ref = reference_data["temperature_(T)"]
	if temperature_kelvin <= 0:
		raise ValueError("Temperature must be above absolute zero")

	diode_ideality_voltage = reference_data["diode_ideality_voltage_(Vd)"] * (
		temperature_kelvin / t_ref
	)

	light_induced_photocurrent = (
		irradiance / reference_data["irradiance_(G)"]
	) * (
		reference_data["light_generated_current_(I_l)"]
		+ model_data["temp_coeff_isc"] * (temperature - model_data["temperature"])
	)

	material_bandgap_energy = reference_data["bandgap_energy_(Eg)"] * (
		1 - 0.0002677 * (temperature_kelvin - t_ref)
	)
	diode_reverse_saturation_current = reference_data["diode_reverse_saturation_current_(I_0)"] * (
		(temperature_kelvin / t_ref) ** 3
	) * exp(
		(ELECTRON_CHARGE / BOLTZMANN_CONSTANT)
		* (
			reference_data["bandgap_energy_(Eg)"] / t_ref
			- material_bandgap_energy / temperature_kelvin
		)
	)

	shunt_resistance = reference_data["shunt_resistance_(Rsh)"] * (
		reference_data["irradiance_(G)"] / irradiance
	)

	calculated_parameters = {
		"irradiance": irradiance,
		"temperature": temperature,
		"temperature_kelvin": temperature_kelvin,
		"light_induced_photocurrent": light_induced_photocurrent,
		"diode_reverse_saturation_current": diode_reverse_saturation_current,
		"diode_ideality_voltage": diode_ideality_voltage,
		"material_bandgap_energy": material_bandgap_energy,
		"shunt_resistance": shunt_resistance,
		"series_resistance": reference_data["series_resistance_(Rs)"],
		"diode_ideality_factor": reference_data["diode_ideality_factor_(n)"],
		"model_ideality_factor": reference_data["model_ideality_factor_(a)"],
	}
	calculated_parameters.update(
		calculate_iv_characteristics(
			irradiance, temperature, model_data, reference_data, calculated_parameters
		)
	)
	return calculated_parameters
