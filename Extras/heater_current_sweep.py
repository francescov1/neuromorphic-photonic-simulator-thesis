import imp
import numpy as np
from math import log

c = 3.0e8
sweep_name = "heater_current_sweep"
time_window = 5.12e-09
n_samples = 15360
save_data = False
load_sim = False

add_sweep = True

start_amplitude = 0
stop_amplitude = 10
n_sims = 10
lumapi = imp.load_source("lumapi.py", "/Applications/Lumerical 2020a.app/Contents/API/Python/lumapi.py")

def setup():
    ic = lumapi.INTERCONNECT("./weight_bank.icp")

    # restore design mode in case we are in analysis mode
    ic.switchtodesign();

    # time to execute simulation
    ic.setnamed("::Root Element","time window", time_window);
    # number of samples defines the INTERCONNECT time step dt
    # by dt = time_window/(Nsamples+1).
    ic.setnamed("::Root Element","number of samples", n_samples);

    if add_sweep:
        # delete any sweeps already saved
        ic.deletesweep(sweep_name);

        ic.addsweep(0)
        ic.setsweep("sweep", "name", sweep_name);
        ic.setsweep(sweep_name, "type", "Ranges");
        ic.setsweep(sweep_name, "number of points", n_sims);

        if save_data:
            ic.setsweep(sweep_name, "resave files after analysis", "true");

        params = {
            "Name": "dc_amplitude",
            "Parameter": "::Root Element::DC_1::amplitude",
            "Type": "Number",
            "Start": start_amplitude,
            "Stop": stop_amplitude
        }

        ic.addsweepparameter(sweep_name, params);

        results = [
            {
                "Name": "drop_transmission",
                "Result": "::Root Element::OSA_1::mode 1/signal"
            },
            {
                "Name": "thru_transmission",
                "Result": "::Root Element::OSA_2::mode 1/signal"
            }
        ]

        for result in results:
            ic.addsweepresult(sweep_name, result);

    return ic


def get_single_result(ic, result_name):
    result = ic.getsweepresult(sweep_name, result_name)
    print(result_name)
    print(result)
    '''
    wavelength_param = result['Lumerical_dataset']['parameters'][0][0]
    signal_param = result['Lumerical_dataset']['attributes'][0]

    wavelength = result[wavelength_param]
    wavelength = [x[0] for x in wavelength]

    signal = result[signal_param]

    return wavelength, signal
    '''
    return

# saves np array, not sweep results
def save_results(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission):
    np.save("Extras/sweep_data/transmission_profiles/drop_wavelength", np.array(drop_wavelength))
    np.save("Extras/sweep_data/transmission_profiles/thru_wavelength", np.array(thru_wavelength))
    np.save("Extras/sweep_data/transmission_profiles/drop_transmission", np.array(drop_transmission))
    np.save("Extras/sweep_data/transmission_profiles/thru_transmission", np.array(thru_transmission))

def run(ic):
    if ic is None:
        print("Error initializing Lumerical API")
        return

    ic.runsweep(sweep_name)
    print("Done running")

if load_sim:
    drop_wavelength, thru_wavelength, drop_transmission, thru_transmission = load_results()
else:
    ic = setup()
    run(ic)

    get_single_result(ic, "drop_transmission")
    #drop_wavelength, drop_transmission = get_single_result(ic, "drop_transmission")
    #thru_wavelength, thru_transmission = get_single_result(ic, "thru_transmission")
    #if save_data:
    #    save_results(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission)

#plot_tranmission(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission)
