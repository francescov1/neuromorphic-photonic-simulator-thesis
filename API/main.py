import os
from pprint import pprint
from Lumerical import interface
#import Lumerical

class API:

    def __init__(self):
        self.init = True

    def load_cache(self):
        wgT = []
        activebentwg = []
        passivebentwg = []
        neff = []

        for root, subdirs, files in os.walk("./Lumerical/cache"):
            for filename in files:
                # heat sim files
                if filename.startswith("wgT_") and filename.endswith(".mat"):
                    _, min_v, max_v, interval_v, _ = filename.split("_")
                    wgT.append({
                        "min_v": float(min_v),
                        "max_v": float(max_v),
                        "interval_v": float(interval_v),
                        "filename": filename,
                    })

                elif filename.startswith("neff_") and filename.endswith(".txt"):
                    _, laser_wavelength, min_v, max_v, interval_v, _ = filename.split("_")
                    neff.append({
                        "laser_wavelength": float(laser_wavelength),
                        "min_v": float(min_v),
                        "max_v": float(max_v),
                        "interval_v": float(interval_v),
                        "filename": filename,
                    })

                elif filename.startswith("activebentwg_") and filename.endswith(".ldf"):
                    _, start_wavelength, end_wavelength, min_v, max_v, interval_v, _ = filename.split("_")
                    activebentwg.append({
                        "start_wavelength": float(start_wavelength),
                        "end_wavelength": float(end_wavelength),
                        "min_v": float(min_v),
                        "max_v": float(max_v),
                        "interval_v": float(interval_v),
                        "filename": filename,
                    })


                elif filename.startswith("passivebentwg_") and filename.endswith(".ldf"):
                    _, start_wavelength, end_wavelength, _ = filename.split("_")
                    passivebentwg.append({
                        "start_wavelength": float(start_wavelength),
                        "end_wavelength": float(end_wavelength),
                        "filename": filename,
                    })
                    passivebentwg.append(filename)
            break

        self.wgT = wgT
        self.activebentwg = activebentwg
        self.passivebentwg = passivebentwg
        self.neff = neff

    def get_param_suggestions(self):
        print("Getting param suggestions")
        # fallbacks if no files in cache
        laser_wavelength = 1545e-9
        min_v = 4.5
        max_v = 4.6
        interval_v = 0.001
        wavelength_window = 25e-9

        if len(self.neff) > 0:
            # take last file in cache for suggested values
            last_sim = self.neff[-1]
            laser_wavelength = last_sim['laser_wavelength']
            min_v = last_sim['min_v']
            max_v = last_sim['max_v']
            interval_v = last_sim['interval_v']

        constant_v = min_v if min_v > 0 else 4.5

        return {
            'laser_wavelength': '%.3e' % laser_wavelength,
            'wavelength_window': '%.2e' % wavelength_window,
            'min_v': str(min_v),
            'max_v': str(max_v),
            'interval_v': str(interval_v),
            'constant_v': str(constant_v)
        }

    def get_heat_sim(self):
        cached_to_use = None
        for cached in self.wgT:
            if (self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['interval_v'] >= cached['interval_v']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("Using cached heat simulation: " + cached_to_use['filename'])
            return "cache/" + cached_to_use['filename']
        else:
            return interface.heat(self.inputs)

    def get_passivebentwg_sim(self):
        cached_to_use = None
        for cached in self.passivebentwg:
            if (self.inputs['start_wavelength'] >= cached['start_wavelength'] and
                self.inputs['end_wavelength'] <= cached['end_wavelength']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("Using cached passivebentwg simulation: " + cached_to_use['filename'])
            return "cache/" + cached_to_use['filename']
        else:
            return interface.passivebentwg(self.inputs)


    def get_activebentwg_sim(self):
        cached_to_use = None
        for cached in self.activebentwg:
            if (self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['interval_v'] >= cached['interval_v'] and
                self.inputs['start_wavelength'] >= cached['start_wavelength'] and
                self.inputs['end_wavelength'] <= cached['end_wavelength']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("Using cached activebentwg simulation: " + cached_to_use['filename'])
            return "cache/" + cached_to_use['filename']
        else:
            filename, mode = interface.activebentwg(self.inputs)

            # this can then be used for neff calc, rather than reconfiguring a sim
            self.lum_mode = mode
            return filename


    def get_effective_index_sim(self):
        cached_to_use = None
        for cached in self.neff:
            if (self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['interval_v'] >= cached['interval_v'] and
                self.inputs['source_wavelength'] <= cached['laser_wavelength']):
                cached_to_use = cached
                break

        lum_mode = self.lum_mode if hasattr(self, 'lum_mode') else None
        if cached_to_use:
            print("Using cached effective_index simulation: " + cached_to_use['filename'])
            # if lum_mode is defined we should close it to minimize resources
            # (since this sim is cached, so we dont need it)
            if lum_mode is not None:
                lum_mode.close()
            return "cache/" + cached_to_use['filename']
        else:
            return interface.effective_index(self.inputs, lum_mode)

    def get_interconnect_sim(self):
        return "Lumerical/weight_bank.icp"

    def run(self, inputs):
        print("API inputs:")
        pprint(inputs)
        self.inputs = inputs

        files = {
            'heat': self.get_heat_sim(),
            'passivebentwg': self.get_passivebentwg_sim(),
            'activebentwg': self.get_activebentwg_sim(),
            'effective_index': self.get_effective_index_sim(),
            'interconnect': self.get_interconnect_sim()
        }

        interface.interconnect(inputs, files)
