import os

class API:

    def __init__(self):
        #print("init")
        self.init = True

    def get_param_suggestions(self):
        wgT = []
        neff = []

        # if input is not a text file, recursively read text files in dir
        for root, subdirs, files in os.walk("./Lumerical/cache"):

            for filename in files:
                # heat sim files
                if filename.startswith("wgT_") and filename.endswith(".mat"):
                    wgT.append(filename)
                elif filename.startswith("neff_") and filename.endswith(".txt"):
                    neff.append(filename)
            break

        # fallbacks if no files in cache
        laser_wavelength = '%.3e' % 1545e-9
        min_v = str(4.5)
        max_v = str(4.6)
        interval_v = str(0.001)
        wavelength_window = '%.2e' % 25e-9


        if len(neff) > 0:
            # take last file in cache for suggested values
            # _, min_v, max_v, interval_v, _ = wgT[-1].split("_")
            _, laser_wavelength, min_v, max_v, interval_v, _ = neff[-1].split("_")

        constant_v = min_v if float(min_v) > 0 else str(4.5)

        return {
            'laser_wavelength': laser_wavelength,
            'wavelength_window': wavelength_window,
            'min_v': min_v,
            'max_v': max_v,
            'interval_v': interval_v,
            'constant_v': constant_v
        }

    def run(self, params):
        print("Running")
        # TODO add logic for which to simulate
        #look into if wavelength precision changes affect cached sims
        #TODO
