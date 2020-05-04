import laser_wavelength_sweep as laser_sweep
from scipy.optimize import curve_fit
from scipy import asarray as ar,exp
from matplotlib import pyplot as plt
import numpy as np

def plot_results(results):
    keys = []
    for key, value in results.items():
        keys.append(key)
    print("Result properties")
    print(keys)

    time = results['time']
    amplitude = results['amplitude (a.u.)']

    plt.plot(time, amplitude)
    plt.xlabel("time (s)")
    plt.ylabel("amplitude (a.u.)")
    plt.show()

def plot_tranmission(wavelength, drop_transmission, thru_transmission):
    plt.subplot(2, 1, 1)
    plt.plot(wavelength, thru_transmission)
    plt.ylabel("thru tranmission (dBm)")

    plt.subplot(2, 1, 2)
    plt.plot(wavelength, drop_transmission)
    plt.xlabel("wavelength (m)")
    plt.ylabel("drop tranmission (dBm)")
    plt.show()

# loads np array, not sweep results
def load_results():
    wavelength = np.load("Extras/wavelength.npy")
    drop_transmission = np.load("Extras/drop_transmission.npy")
    thru_transmission = np.load("Extras/thru_transmission.npy")

    return wavelength, drop_transmission, thru_transmission

# saves np array, not sweep results
def save_results(wavelength, drop_transmission, thru_transmission):
    np.save("Extras/wavelength", np.array(wavelength))
    np.save("Extras/drop_transmission", np.array(drop_transmission))
    np.save("Extras/thru_transmission", np.array(thru_transmission))

# if False, runs a new sim. If True, loads results from disk
load_sim = False
save_data = True

# simulation config
time_window = 5.12e-09
n_samples = 15360

# sweep config
#start_wavelength = 1515e-9 # m
#end_wavelength = 1535e-9 # m
start_wavelength = 1517e-9
end_wavelength = 1524e-9
n_sims = 100

if load_sim:
    wavelength, drop_transmission, thru_transmission = load_results()
else:
    ic = laser_sweep.setup(start_wavelength, end_wavelength, n_sims, time_window, n_samples, save_data)
    wavelength, drop_transmission, thru_transmission = laser_sweep.run(ic)
    if save_data:
        save_results(wavelength, drop_transmission, thru_transmission)

plot_tranmission(wavelength, drop_transmission, thru_transmission)
