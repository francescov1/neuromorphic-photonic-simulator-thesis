import imp
import numpy as np
from math import log
import os
from scipy.stats import linregress
from scipy.constants import c
from matplotlib import pyplot as plt
from prompt_toolkit import PromptSession
#from prompt_toolkit.history import InMemoryHistory
#from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

time_window = 5.12e-09
n_samples = 15360
heater_path = "./n-doped-heater/"

# TODO BEFORE ANYTHING
# thermally tuned waveguide
# https://support.lumerical.com/hc/en-us/articles/360042833673-Thermally-tuned-waveguide-FDE-
# https://kx.lumerical.com/t/different-doping-regions-device/7682/2
# pg 13: https://open.library.ubc.ca/cIRcle/collections/ubctheses/24/items/1.0363058
laser_wavelength = 1545e-9
min_voltage = 0
max_voltage = 20
n_voltages = 100

lumapi = imp.load_source("lumapi.py", "/Applications/Lumerical 2020a.app/Contents/API/Python/lumapi.py")

# TODOs:
'''
- setup interactive config: https://codeburst.io/building-beautiful-command-line-interfaces-with-python-26c7e1bb54df
- last paragraph from alex fb control pg 3, 8, (both code and report) to improve ndoped heater description & calibration
- calc params from alex fb control last par. pg 5 & pg 6, thermo-optic coefficient looks doable - see what else
- run headless
- pip freeze
- cleanup file structure
- readme
'''

# important notes
'''
https://support.lumerical.com/hc/en-us/articles/360042322794
calc passive wg: step 2, or passivebentwg
'''

def heat(min_v, max_v, prec_v):
    # TODO: if resim not required, skip
    # need to do heat if values out of saved range, or precision is smaller than saved
    device = lumapi.DEVICE(heater_path + "NdopedHeaterDesign.ldev")
    device.switchtolayout()
    device.setnamed("HEAT::temp", "filename", "wgT1_" + str(min_v) + "_" + str(max_v) + "_" + str(prec_v) + ".mat")

    v_bc_name = "HEAT::boundary conditions::wire1"
    device.setnamed(v_bc_name, "range start", min_v)
    device.setnamed(v_bc_name, "range stop", max_v)
    device.setnamed(v_bc_name, "range interval", prec_v)

    device.run()

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

    #plot(V,-I,'Voltage (V)','Current (A)');

    # this could be useful for power or ohms/power
    '''
    P1 = pinch(boundaries.P_lead_left);
    P2 = pinch(boundaries.P_lead_right);
    P3 = pinch(boundaries.P_substrate);
    P4 = pinch(boundaries.P_top_surface);

    Ptotal = abs(P1+P2+P3+P4);

    R = 50; # ohm
    Panalytic = V^2/R;

    plot(V,Ptotal,Panalytic,'Voltage (V)','Power (W)');
    legend('simulation','analytic');
    '''

    device.close()

# TODO: this needs to be tested
# go through lums example and see how its done - then just replicate
def passivebentwg():
    mode = lumapi.MODE(heater_path + "rib_waveguide.lms")

    # import T map
    mode.switchtolayout()
    mode.select("temperature")
    mode.setnamed('temperature','enabled', 0);

    mode.run()
    #print(mode.getanalysis())
    mode.setanalysis("number of trial modes", 2)
    mode.setanalysis("wavelength", laser_wavelength)
    mode.setanalysis("use max index", 1)

    mode.findmodes()
    print("Num nodes: " + str(mode.nummodes()))
    mode.selectmode(1)

    mode.setanalysis("track selected mode", 1);
    input("Run frequency sweep")
    mode.frequencysweep()
    dataname = mode.copydcard("frequencysweep");
    mode.savedcard("passive_bent_wg.ldf", dataname);
    mode.close()

def neffModeSolver():
    mode = lumapi.MODE(heater_path + "rib_waveguide.lms")

    # import T map
    mode.switchtolayout()
    mode.select("temperature")
    mode.importdataset("wgT1.mat")

    mode.run()
    #print(mode.getanalysis())
    mode.setanalysis("number of trial modes", 2)
    mode.setanalysis("wavelength", laser_wavelength)
    mode.setanalysis("use max index", 1)

    mode.findmodes()
    print("Num nodes: " + str(mode.nummodes()))

    mode.selectmode(1)
    mode.setanalysis("track selected mode", 1)
    mode.frequencysweep()
    dataname = mode.copydcard("frequencysweep")
    mode.savedcard("active_bent_wg.ldf", dataname)

    voltage = np.linspace(min_voltage, max_voltage, n_voltages) # volts
    neffT = []

    # TODO: ensure i dont need to use seteigensolver instead of setanalysis
    # read T map
    result_str = ""
    for v in voltage:
        mode.switchtolayout();
        mode.setnamed('temperature','enabled', 1);
        mode.setnamed('temperature','V_wire1', v);
        mode.findmodes();

        data = mode.getdata('mode1','neff');

        if len(data) != 1 or len(data[0]) != 1:
            print("Error, length of data wrong")
            print(data)

        neff = data[0][0]
        neffT.append(neff)

        result_str += str(v) + " " + str(np.real(neff)) + " " + str(np.imag(neff)) + "\n"

    f = open("Delta_neffTemp1.txt","w+")
    f.write(result_str)
    f.close()
    mode.close()

def interconnect():
    ic = lumapi.INTERCONNECT("./weight_bank.icp")

    # TODO: configure sim with files from previous sims
    # restore design mode in case we are in analysis mode
    ic.switchtodesign()

    # time to execute simulation
    ic.setnamed("::Root Element","time window", time_window)
    # number of samples defines the INTERCONNECT time step dt
    # by dt = time_window/(Nsamples+1).
    ic.setnamed("::Root Element","number of samples", n_samples)

    use_laser = False
    # TODO: configure by user
    if user_laser:
        ic.addelement("CW Laser")
        ic.setnamed("CWL_1", "frequency", c/laser_wavelength)
        ic.setnamed("CWL_1", "power", 0.001)
        ic.select("ONA_1")
        ic.delete()
        ic.connect("CWL_1", "output", "COMPOUND_1", "input")

    ic.run()
    return ic

def main():
    # take in values, show previous given as default
    # depending on which are changed, re run sims
    session = PromptSession()
    voltage = session.prompt('Enter n-doped heater voltage range (start,end,precision): ', default='4.5,4.62,0.003')
    min_v, *rest_v = list(map(float, voltage.split(",")))

    max_v = rest_v[0] if rest_v else min_v
    prec_v = rest_v[1] if rest_v else 1

    print(min_v)
    print(max_v)
    print(prec_v)

    heat(min_v, max_v, prec_v)
    #input("Run neff mode solver?")

interconnect()
