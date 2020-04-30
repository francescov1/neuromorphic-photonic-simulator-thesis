import imp
import numpy as np
from scipy.stats import linregress
from scipy.constants import c
from matplotlib import pyplot as plt

time_window = 5.12e-09
n_samples = 15360

lumapi = imp.load_source("lumapi.py", "/Applications/Lumerical 2020a.app/Contents/API/Python/lumapi.py")

def wgT_name(min_v, max_v, interval_v):
    return "cache/wgT_" + str(min_v) + "_" + str(max_v) + "_" + str(interval_v) + "_.mat"

def passivebentwg_name(start_wavelength, end_wavelength):
    return "cache/passivebentwg_" + str(start_wavelength) + "_" + str(end_wavelength) + "_.ldf"

def activebentwg_name(start_wavelength, end_wavelength, min_v, max_v, interval_v):
    return "cache/activebentwg_" + str(start_wavelength) + "_" + str(end_wavelength) + "_" + str(min_v) + "_" + str(max_v) + "_" + str(interval_v) + "_.ldf"

def neff_name(laser_wavelength, min_v, max_v, interval_v):
    return "cache/neff_" + str(laser_wavelength) + "_" + str(min_v) + "_" + str(max_v) + "_" + str(interval_v) + "_.txt"

def heat(min_v, max_v, interval_v):
    device = lumapi.DEVICE("ndoped_heater.ldev")
    device.switchtolayout()
    device.setnamed("HEAT::temp", "filename", wgT_name(min_v, max_v, interval_v))

    v_bc_name = "HEAT::boundary conditions::wire1"
    device.setnamed(v_bc_name, "range start", min_v)
    device.setnamed(v_bc_name, "range stop", max_v)
    device.setnamed(v_bc_name, "range interval", interval_v)

    device.run()

    boundaries = device.getresult('HEAT','boundaries');

    current = [x[0] for x in boundaries['I_wire1'][0][0]]
    voltage = [x[0] for x in boundaries['V_wire1']]

    reg = linregress(current, voltage)
    resistance = reg[0]
    print("Resistance = " + str(resistance) + " Ohms")

    '''
    plt.plot(current, voltage)
    plt.xlabel("current")
    plt.ylabel("voltage")
    plt.show()
    '''

    device.close()
    return current, voltage


# NOTE: straight waveguides arent included here
# NOTE: this does not usually need to be re-simulated
def passiveBentWg(start_wavelength, end_wavelength):
    mode = lumapi.MODE("rib_waveguide.lms")

    mode.switchtolayout()
    mode.select("temperature")
    mode.setnamed('temperature','enabled', 0);

    mode.run()
    mode.setanalysis("number of trial modes", 5)
    mode.setanalysis("wavelength", start_wavelength)
    mode.setanalysis("use max index", 1)

    mode.findmodes()
    mode.selectmode(1)

    mode.setanalysis("stop wavelength", end_wavelength)
    mode.setanalysis("track selected mode", 1);

    mode.frequencysweep()

    dataname = mode.copydcard("frequencysweep");
    mode.savedcard(passivebentwg_name(start_wavelength, end_wavelength), dataname);
    mode.close()
    return


#def neffModeSolver(laser_wavelength, min_v, max_v, interval_v):
def activeBentWg(start_wavelength, end_wavelength, min_v, max_v, interval_v):
    mode = lumapi.MODE("rib_waveguide.lms")

    mode.switchtolayout()
    mode.select("temperature")
    mode.importdataset(wgT_name(min_v, max_v, interval_v))

    mode.run()
    mode.setanalysis("number of trial modes", 2)
    mode.setanalysis("wavelength", start_wavelength)
    mode.setanalysis("use max index", 1)

    mode.findmodes()
    mode.selectmode(1)

    mode.setanalysis("stop wavelength", end_wavelength)
    mode.setanalysis("track selected mode", 1)

    mode.frequencysweep()
    dataname = mode.copydcard("frequencysweep")
    mode.savedcard(activebentwg_name(start_wavelength, end_wavelength, min_v, max_v, interval_v), dataname)

    # same sim will be used for neff.txt so dont close yet
    return mode

def effective_index(mode, laser_wavelength, min_v, max_v, interval_v):
    voltage = np.arange(min_v, max_v, step=interval_v) # volts
    neffT = []

    result_str = ""
    for v in voltage:
        mode.switchtolayout();
        mode.setnamed('temperature','enabled', 1);
        mode.setnamed('temperature','V_wire1', v);
        mode.findmodes();

        data = mode.getdata('mode1','neff');

        neff = data[0][0]
        neffT.append(neff)

        result_str += str(v) + " " + str(np.real(neff)) + " " + str(np.imag(neff)) + "\n"

    f = open(neff_name(laser_wavelength, min_v, max_v, interval_v),"w+")
    f.write(result_str)
    f.close()
    mode.close()

    return neffT

def interconnect(laser_wavelength, sim_type):
    ic = lumapi.INTERCONNECT("weight_bank.icp")

    ic.switchtodesign()
    ic.setnamed("::Root Element","time window", time_window)
    # number of samples defines the INTERCONNECT time step dt
    # by dt = time_window/(Nsamples+1).
    ic.setnamed("::Root Element","number of samples", n_samples)

    if sim_type == "single laser":
        ic.addelement("CW Laser")
        ic.setnamed("CWL_1", "frequency", c/laser_wavelength)
        ic.setnamed("CWL_1", "power", 0.001)
        ic.select("ONA_1")
        ic.delete()
        ic.connect("CWL_1", "output", "COMPOUND_1", "input")

    ic.run()
    return ic

#heat(0,20,0.2)

#neffModeSolver(1545e-9, 0, 20, 0.2)
#mode = activeBentWg(1500e-9, 1600e-9, 0, 20, 0.2)
#effective_index(mode, 1500e-9, 0, 20, 0.2)

passiveBentWg(1500e-9, 1698e-9)
