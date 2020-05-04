import imp
import numpy as np
from math import log

c = 3.0e8
sweep_name = "laser_wavelength_sweep"

lumapi = imp.load_source("lumapi.py", "/Applications/Lumerical 2020a.app/Contents/API/Python/lumapi.py")

def setup(start_wavelength, end_wavelength, n_sims, time_window, n_samples, save_data):
    ic = lumapi.INTERCONNECT("./weight_bank.icp")

    # restore design mode in case we are in analysis mode
    ic.switchtodesign();

    # time to execute simulation
    ic.setnamed("::Root Element","time window", time_window);
    # number of samples defines the INTERCONNECT time step dt
    # by dt = time_window/(Nsamples+1).
    ic.setnamed("::Root Element","number of samples", n_samples);

    # delete any sweeps already saved
    # TODO: instead just ensure params are right if a 1 or 2 is appended to them
    ic.deletesweep(sweep_name);

    ic.addsweep(0)
    ic.setsweep("sweep", "name", sweep_name);
    ic.setsweep(sweep_name, "type", "Ranges");
    ic.setsweep(sweep_name, "number of points", n_sims);

    if save_data:
        ic.setsweep(sweep_name, "resave files after analysis", "true");

    start_frequency = c/start_wavelength
    end_frequency = c/end_wavelength

    params = {
        "Name": "frequency",
        "Parameter": "::Root Element::CWL_1::frequency",
        "Type": "Frequency",
        "Start": start_frequency,
        "Stop": end_frequency
    }

    ic.addsweepparameter(sweep_name, params);

    results = [
        {
            "Name": "drop_transmission",
            "Result": "::Root Element::OOSC_2::mode 1/signal"
        },
        {
            "Name": "thru_transmission",
            "Result": "::Root Element::OOSC_1::mode 1/signal"
        }
    ]

    for result in results:
        ic.addsweepresult(sweep_name, result);

    return ic

def run(ic):
    if ic is None:
        print("Error initializing Lumerical API")
        return

    ic.runsweep(sweep_name)

    print("Done running")
    drop_result = ic.getsweepresult(sweep_name, "drop_transmission")
    thru_result = ic.getsweepresult(sweep_name, "thru_transmission")

    print(drop_result)

    attribute_name = drop_result['Lumerical_dataset']['attributes'][0]
    print('tranmission name: ' + attribute_name)

    drop_transmission = [10*log(x*1000, 10) for x in drop_result[attribute_name][-1]]
    thru_transmission = [10*log(x*1000, 10) for x in thru_result[attribute_name][-1]]

    # these should be equal
    drop_wavelength = [c/x for x in drop_result['frequency'][0]]
    thru_wavelength = [c/x for x in thru_result['frequency'][0]]

    return drop_wavelength, drop_transmission, thru_transmission
