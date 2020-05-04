import imp
import numpy as np
from scipy.stats import linregress
from scipy.constants import c
from matplotlib import pyplot as plt
from math import log

time_window = 5.12e-09
n_samples = 15360

# TODO: set path of the Lumerical installation. See Automation API docs for more information.
# For MacOS, the following should suffice as long as the version is correct
lum_version = "2020a"
lum_path = "/Applications/Lumerical " + lum_version + ".app/Contents/API/Python/lumapi.py"
lumapi = imp.load_source("lumapi.py", lum_path)

def wgT_name(min_v, max_v, interval_v):
    return "cache/wgT_" + str(min_v) + "_" + str(max_v) + "_" + str(interval_v) + "_.mat"

def passivebentwg_name(start_wavelength, end_wavelength):
    return "cache/passivebentwg_" + str(start_wavelength) + "_" + str(end_wavelength) + "_.ldf"

def activebentwg_name(start_wavelength, end_wavelength, min_v, max_v, interval_v):
    return "cache/activebentwg_" + str(start_wavelength) + "_" + str(end_wavelength) + "_" + str(min_v) + "_" + str(max_v) + "_" + str(interval_v) + "_.ldf"

def neff_name(laser_wavelength, min_v, max_v, interval_v):
    return "cache/neff_" + str(laser_wavelength) + "_" + str(min_v) + "_" + str(max_v) + "_" + str(interval_v) + "_.txt"

def heat(inputs):
    print("Running heat simulation")
    min_v, max_v, interval_v = [inputs[k] for k in ('min_v','max_v', 'interval_v')]
    filename = wgT_name(min_v, max_v, interval_v)

    device = lumapi.DEVICE("Lumerical/ndoped_heater.ldev")
    device.switchtolayout()
    device.setnamed("HEAT::temp", "filename", filename)

    v_bc_name = "HEAT::boundary conditions::wire1"
    device.setnamed(v_bc_name, "range start", min_v)
    device.setnamed(v_bc_name, "range stop", max_v)
    device.setnamed(v_bc_name, "range interval", interval_v)

    device.run()

    '''
    boundaries = device.getresult('HEAT','boundaries');

    current = [x[0] for x in boundaries['I_wire1'][0][0]]
    voltage = [x[0] for x in boundaries['V_wire1']]

    reg = linregress(current, voltage)
    resistance = reg[0]
    print("Resistance = " + str(resistance) + " Ohms")

    plt.plot(current, voltage)
    plt.xlabel("current")
    plt.ylabel("voltage")
    plt.show()
    '''

    device.close()
    #return current, voltage

    return filename


# NOTE: straight waveguides arent included here
# NOTE: this does not usually need to be re-simulated
def passivebentwg(inputs):
    print("Running passive bent waveguide simulation")
    start_wavelength, end_wavelength = [inputs[k] for k in ('start_wavelength', 'end_wavelength')]
    filename = passivebentwg_name(start_wavelength, end_wavelength)

    mode = lumapi.MODE("Lumerical/rib_waveguide.lms")

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
    mode.savedcard(filename, dataname);
    mode.close()
    return filename

#def neffModeSolver(laser_wavelength, min_v, max_v, interval_v):
def activebentwg(inputs):
    print("Running active bent waveguide simulation")
    start_wavelength, end_wavelength, min_v, max_v, interval_v = [inputs[k] for k in ('start_wavelength', 'end_wavelength', 'min_v', 'max_v', 'interval_v')]
    filename = activebentwg_name(start_wavelength, end_wavelength, min_v, max_v, interval_v)

    mode = lumapi.MODE("Lumerical/rib_waveguide.lms")

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
    mode.savedcard(filename, dataname)

    # same sim can be used for neff.txt so dont close yet
    return filename, mode

def effective_index(inputs, mode = None):
    print("Running effective index simulation")
    source_wavelength, min_v, max_v, interval_v = [inputs[k] for k in ('source_wavelength', 'min_v', 'max_v', 'interval_v')]
    filename = neff_name(source_wavelength, min_v, max_v, interval_v)

    if mode is None:
        print("Setting up mode")
        mode = lumapi.MODE("Lumerical/rib_waveguide.lms")
        mode.setanalysis("number of trial modes", 2)
        mode.setanalysis("wavelength", source_wavelength)
        mode.setanalysis("use max index", 1)

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

    f = open("Lumerical/" + filename,"w+")
    f.write(result_str)
    f.close()
    mode.close()

    return filename

def laser_wavelength_sweep(ic, inputs):
    print("Running laser wavelength sweep")
    min_v, max_v, interval_v = [inputs[k] for k in ('min_v', 'max_v', 'interval_v')]
    sweep_name = "laser_wavelength_sweep"

    # delete any sweeps already saved
    ic.deletesweep(sweep_name);

    ic.addsweep(0)
    ic.setsweep("sweep", "name", sweep_name);
    ic.setsweep(sweep_name, "type", "Ranges");
    ic.setsweep(sweep_name, "number of points", int((max_v-min_v)/interval_v));

    params = {
        "Name": "dc_amplitude",
        "Parameter": "::Root Element::DC_1::amplitude",
        "Type": "Number",
        "Start": min_v,
        "Stop": max_v
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

    ic.runsweep(sweep_name)
    print("Done running laser wavelength sweep. Results can be accessed from the laser_wavelength_sweep in Lumerical")
    return

# NOTE: there are sometimes weird race conditions here where the sweep receives
# no results because automation api is too slow
def ona_sweep(ic, inputs):
    print("Running ona sweep")
    min_v, max_v, interval_v = [inputs[k] for k in ('min_v', 'max_v', 'interval_v')]
    sweep_name = "ona_sweep"

    # delete any sweeps already saved
    ic.deletesweep(sweep_name);

    ic.addsweep(0)
    ic.setsweep("sweep", "name", sweep_name);
    ic.setsweep(sweep_name, "type", "Ranges");
    ic.setsweep(sweep_name, "number of points", int((max_v-min_v)/interval_v));

    params = {
        "Name": "dc_amplitude",
        "Parameter": "::Root Element::DC_1::amplitude",
        "Type": "Number",
        "Start": min_v,
        "Stop": max_v
    }

    ic.addsweepparameter(sweep_name, params);

    results = [
        {
            "Name": "drop_transmission",
            "Result": "::Root Element::ONA_1::input 2/mode 1/gain"
        },
        {
            "Name": "thru_transmission",
            "Result": "::Root Element::ONA_1::input 1/mode 1/gain"
        }
    ]

    for result in results:
        ic.addsweepresult(sweep_name, result);

    ic.runsweep(sweep_name)
    print("Done running ona sweep. Results can be accessed from the ona_sweep in Lumerical")
    return

def interconnect(inputs, files):
    print("Running interconnect simulation")
    source_wavelength, sim_type, heater_sim_type = [inputs[k] for k in ('source_wavelength', 'sim_type', 'heater_sim_type')]

    ic = lumapi.INTERCONNECT(files['interconnect'])

    ic.switchtodesign()
    ic.setnamed("::Root Element","time window", time_window)
    # number of samples defines the INTERCONNECT time step dt
    # by dt = time_window/(Nsamples+1).
    ic.setnamed("::Root Element","number of samples", n_samples)

    # set simulated/cached resources
    ic.setnamed("::Root Element::COMPOUND_1::WGD_6","ldf filename", files['activebentwg'])
    ic.setnamed("::Root Element::COMPOUND_1::WGD_5","ldf filename", files['passivebentwg'])
    ic.setnamed("::Root Element::COMPOUND_1::OM_1","measurement filename", files['effective_index'])

    if sim_type == "single laser":
        ic.addelement("CW Laser")
        ic.setnamed("CWL_1", "frequency", c/source_wavelength)
        ic.setnamed("CWL_1", "power", 0.001)
        ic.select("ONA_1")
        ic.delete()
        ic.connect("CWL_1", "output", "COMPOUND_1", "input")

        if heater_sim_type == "sweep":
            laser_wavelength_sweep(ic, inputs)
        else:
            ic.run()

    else:
        if heater_sim_type == "sweep":
            ona_sweep(ic, inputs)
        else:
            ic.run()

    input("Simulation complete. Please export any data you would like to keep from Lumerical and press ENTER once finished.")
    ic.close()
    return
