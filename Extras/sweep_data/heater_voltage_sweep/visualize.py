from matplotlib import pyplot as plt
import numpy as np

# laser wavelength: 1.475e-06
start_v = 4.52
end_v = 4.63
n = 20

start_wavelength = 1542.5
end_wavelength = 1557.5
#prefix = str(start_v) + "-" + str(end_v) + "V/"
prefix = "2fsrproper_456769v/"
c = 3.0e8
#R = 800 # ohms

def plot_slice(wavelength, drop_dbm, thru_dbm):
    drop = (1/1000)*(10**(drop_dbm/10))
    thru = (1/1000)*(10**(thru_dbm/10))

    output = -(drop-thru)
    #output_dbm = 10*np.log10(output*1000)

    # convert to mW
    output *= 1000
    drop *= 1000
    thru *= 1000

    plt.subplot(2, 1, 1)
    plt.plot(wavelength, output)
    plt.ylabel("Output Weight")
    plt.xlabel("Wavelength (um)")

    plt.subplot(2, 1, 2)
    plt.plot(wavelength, drop, label='drop')
    plt.plot(wavelength, thru, label='thru')
    plt.xlabel("Wavelength (um)")
    plt.ylabel("Tranmission (mW)")
    plt.legend()
    plt.show()

drop_dbm = np.loadtxt(prefix + "drop.txt", skiprows=1)
thru_dbm = np.loadtxt(prefix + "thru.txt", skiprows=1)

wavelength = np.linspace(start_wavelength, end_wavelength, 1000)

plot_slice(wavelength, drop_dbm, thru_dbm)


'''
#4.3->4.5 40 points
voltage = np.linspace(start_v, end_v, n)
#current = voltage/R

drops = np.loadtxt(prefix + "drop.txt", skiprows=1)
thrus = np.loadtxt(prefix + "thru.txt", skiprows=1)

for i in range(n):
    drop = drops[i]
    thru = thrus[i]
    v = voltage[i]

    drop_P = (1/1000)*(10**(drop/10))
    thru_P = (1/1000)*(10**(thru/10))

    output = -(drop_P-thru_P)
    output *= 1000
    #output_dbm = 10*np.log10(output*1000)

    #plt.subplot(2, 1, 1)
    plt.plot(wavelength, output, label="%.3fV" % v)

    plt.ylabel("Power (mW)")
    plt.xlabel("Wavelength (um)")

'''
