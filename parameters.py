"""Reference single-diode parameters extracted from a PV module datasheet.

The extraction uses the reference irradiance and temperature from the selected
model together with its Isc, Voc, Imp, and Vmp values.
"""

from math import exp, log
from scipy.special import lambertw



ELECTRON_CHARGE = 1.602176634e-19  # C
BOLTZMANN_CONSTANT = 1.380649e-23  # J/K
EG_REF = 1.121  # eV, silicon band-gap energy at the reference temperature

# These names are populated by extract_reference_parameters().
delta = None
diode_ideality_voltage = None
diode_ideality_factor = None
series_resistance = None
shunt_resistance = None
light_generated_current = None
diode_reverse_saturation_current = None


def extract_reference_parameters(model_data):
	"""Extract reference parameters using the Batzelis datasheet method.

	``model_data`` must be the dictionary returned by ``config.load_model`` or
	``config.configure``. The returned dictionary is also assigned to the
	module variables requested by the PV model.
	"""
	global delta
	global diode_ideality_voltage
	global diode_ideality_factor
	global series_resistance
	global shunt_resistance
	global light_generated_current
	global diode_reverse_saturation_current

	isc = model_data["short_circuit_current"]
	voc = model_data["open_circuit_voltage"]
	imp = model_data["max_power_current"]
	vmp = model_data["max_power_voltage"]
	temperature_celsius = model_data["temperature"]
	temperature_kelvin = temperature_celsius + 273.15

	if isc <= 0 or imp <= 0 or imp >= isc:
		raise ValueError("The model must satisfy 0 < I_mp < I_sc")
	if voc <= vmp:
		raise ValueError("The model must satisfy V_oc > V_mp")

	thermal_voltage = BOLTZMANN_CONSTANT * temperature_kelvin / ELECTRON_CHARGE

	# Batzelis reference extraction from the temperature coefficients.
	delta = (
		1 - (model_data["temp_coeff_voc"] / voc) * temperature_kelvin
	) / (
		50.1 - (model_data["temp_coeff_isc"] / isc) * temperature_kelvin
	)
	if delta <= 0:
		raise ValueError("The extracted delta must be positive")

	w = lambertw(exp(1 / delta + 1), k=0).real
	diode_ideality_voltage = delta * voc
	diode_ideality_factor = (
		diode_ideality_voltage * ELECTRON_CHARGE
		/ (model_data["cells"] * BOLTZMANN_CONSTANT * temperature_kelvin)
	)
	model_ideality_factor = model_data["cells"] * diode_ideality_factor * thermal_voltage
	series_resistance = (diode_ideality_voltage * (w - 1) - vmp) / imp
	shunt_resistance = (diode_ideality_voltage * (w - 1)) / (
		isc * (1 - 1 / w) - imp
	)
	light_generated_current = (1 + (series_resistance / shunt_resistance)) * isc
	diode_reverse_saturation_current = light_generated_current * exp(-1 / delta)
	if shunt_resistance <= 0:
		raise ValueError("The extracted shunt resistance is not positive")

	return {
		"delta": delta,
		"thermal_voltage_(Vth)": thermal_voltage, # Thermal voltage
		"diode_ideality_voltage_(Vd)": diode_ideality_voltage, # Diode ideality voltage
		"diode_ideality_factor_(n)": diode_ideality_factor, # Diode ideality factor
		"model_ideality_factor_(a)": model_ideality_factor, # Model ideality factor
		"light_generated_current_(I_l)": light_generated_current, # Light-generated current
		"diode_reverse_saturation_current_(I_0)": diode_reverse_saturation_current, # Diode reverse saturation current
		"shunt_resistance_(Rsh)": shunt_resistance,
		"series_resistance_(Rs)": series_resistance,
		"irradiance_(G)": model_data["irradiance"],
		"temperature_(T)": temperature_kelvin,
		"bandgap_energy_(Eg)": EG_REF,
		"ideality_factor_(n)": diode_ideality_factor
	}
