from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
import numpy as np

# loads np array, not sweep results
def load_results():
    wavelength = np.load("sweep_data/wavelength.npy")
    drop_transmission = np.load("sweep_data/drop_transmission.npy")
    thru_transmission = np.load("sweep_data/thru_transmission.npy")

    return wavelength, drop_transmission, thru_transmission

def plot_tranmission(wavelength, drop_transmission, thru_transmission):
    plt.subplot(2, 1, 1)
    plt.plot(wavelength, thru_transmission)
    plt.ylabel("thru tranmission (dBm)")

    plt.subplot(2, 1, 2)
    plt.plot(wavelength, drop_transmission)
    plt.xlabel("wavelength (m)")
    plt.ylabel("drop tranmission (dBm)")
    plt.show()

def slice_data(x_data, y_data, start_x, end_x):
    start_i = None
    end_i = None
    for i, x in enumerate(x_data):
        if start_i is None and x >= start_x:
            start_i = i-1
        elif end_i is None and x >= end_x:
            end_i = i+1
            break

    return x_data[start_i:end_i], y_data[start_i:end_i]

def guassian_fit(x_data, y_data, start_x = None, end_x = None):
    if start_x != None and end_x != None:
        x_data, y_data = slice_data(x_data, y_data, start_x, end_x)

    print(x_data)
    print("")
    print(y_data)
    print("")
    # fit doesnt work unless this is done
    # this gets reverted at the end of this function
    y_data+=40

    x0 = np.sum(x_data*y_data)/np.sum(y_data)
    sigma = np.sqrt(np.abs(np.sum((x_data-x0)**2*y_data)/np.sum(y_data)))
    max = y_data.max()

    print("Estimated max: " + str(max))
    print("Estimated x0: " + str(x0))
    print("Estimated sigma: " + str(sigma))

    def gaus(x_data,max,x0,sigma):
        return max*np.exp(-(x_data-x0)**2/(2*sigma**2))

    popt, pcov = curve_fit(gaus,x_data,y_data,p0=[max,x0,sigma])
    print("Fit max: " + str(popt[0]))
    print("Fit x0: " + str(popt[1]))
    print("Fit sigma: " + str(popt[2]) + "\n")

    y_data_fit = gaus(x_data,*popt)
    y_data_fit -= 40
    y_data -= 40
    return x_data, y_data_fit, popt

def fit_2_peaks(wavelength, transmission):
    start_x_peak1 = 1517e-9
    end_x_peak1 = 1524e-9
    start_x_peak2 = 1525e-9
    end_x_peak2 = 1535e-9

    #wavelength, transmission = slice_data(wavelength, transmission, start_x_peak1, end_x_peak2)

    # take drop, peak 1: 1515-1525, peak2: 1525-1535
    x_fit_peak1, y_fit_peak1, popt_peak1 = guassian_fit(wavelength, transmission, start_x_peak1, end_x_peak1)
    x_fit_peak2, y_fit_peak2, popt_peak2 = guassian_fit(wavelength, transmission, start_x_peak2, end_x_peak2)

    fsr = popt_peak2[1] - popt_peak1[1]
    print("FSR: " + str(fsr))

    plt.plot(wavelength,transmission,'b+:',label='data')
    plt.plot(x_fit_peak1,y_fit_peak1,'r-',label='fit1')
    plt.plot(x_fit_peak2,y_fit_peak2,'r-',label='fit2')
    plt.legend()
    plt.xlabel("wavelength (m)")
    plt.ylabel("drop tranmission (dBm)")
    plt.show()

def fit_peak(wavelength, transmission):

    # take drop, peak 1: 1515-1525, peak2: 1525-1535
    x_fit_peak, y_fit_peak, popt_peak = guassian_fit(wavelength, transmission)

    plt.plot(wavelength,transmission,'b+:',label='data')
    plt.plot(x_fit_peak,y_fit_peak,'r-',label='fit')
    plt.legend()
    plt.xlabel("wavelength (m)")
    plt.ylabel("drop tranmission (dBm)")
    plt.show()


wavelength, drop_transmission, thru_transmission = load_results()

#fit_2_peaks(wavelength, drop_transmission)
fit_peak(wavelength, drop_transmission)
#plot_tranmission(wavelength, drop_transmission, thru_transmission)
