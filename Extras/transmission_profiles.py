import laser_wavelength_sweep as laser_sweep
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
from matplotlib import pyplot as plt
import numpy as np
import imp
from math import log

c = 3.0e8
load_sim = True
save_data = False

lumapi = imp.load_source("lumapi.py", "/Applications/Lumerical 2020a.app/Contents/API/Python/lumapi.py")

def setup():
    ic = lumapi.INTERCONNECT("./weight_bank.icp")

    # restore design mode in case we are in analysis mode
    ic.switchtodesign();
    return ic

def run(ic):
    if ic is None:
        print("Error initializing Lumerical API")
        return

    ic.run()
    print("Done running")
    return

def get_single_result(ic, osa, result_name):
    result = ic.getresult(osa, result_name)
    wavelength_param = result['Lumerical_dataset']['parameters'][0][0]
    signal_param = result['Lumerical_dataset']['attributes'][0]

    wavelength = result[wavelength_param]
    wavelength = [x[0] for x in wavelength]

    signal = result[signal_param]

    return wavelength, signal

def plot_tranmission(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission):
    plt.subplot(2, 1, 1)
    plt.plot(thru_wavelength, thru_transmission)
    plt.ylabel("thru tranmission (dBm)")

    plt.subplot(2, 1, 2)
    plt.plot(drop_wavelength, drop_transmission)
    plt.xlabel("wavelength (m)")
    plt.ylabel("drop tranmission (dBm)")
    plt.show()

# loads np array, not sweep results
def load_results():
    drop_wavelength = np.load("Extras/transmission_profiles/drop_wavelength.npy")
    thru_wavelength = np.load("Extras/transmission_profiles/thru_wavelength.npy")
    drop_transmission = np.load("Extras/transmission_profiles/drop_transmission.npy")
    thru_transmission = np.load("Extras/transmission_profiles/thru_transmission.npy")

    return drop_wavelength, thru_wavelength, drop_transmission, thru_transmission

# saves np array, not sweep results
def save_results(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission):
    np.save("Extras/transmission_profiles/drop_wavelength", np.array(drop_wavelength))
    np.save("Extras/transmission_profiles/thru_wavelength", np.array(thru_wavelength))
    np.save("Extras/transmission_profiles/drop_transmission", np.array(drop_transmission))
    np.save("Extras/transmission_profiles/thru_transmission", np.array(thru_transmission))

if load_sim:
    drop_wavelength, thru_wavelength, drop_transmission, thru_transmission = load_results()
else:
    ic = setup()
    run(ic)

    drop_wavelength, drop_transmission = get_single_result(ic, "OSA_1", "mode 1/signal")
    thru_wavelength, thru_transmission = get_single_result(ic, "OSA_2", "mode 1/signal")
    if save_data:
        save_results(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission)

plot_tranmission(drop_wavelength, thru_wavelength, drop_transmission, thru_transmission)
