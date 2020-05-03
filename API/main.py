import os
from pprint import pprint

class API:

    def __init__(self):
        self.init = True

    def load_cache(self):
        wgT = []
        activeBentWg = []
        passiveBentWg = []
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
                    activeBentWg.append({
                        "start_wavelength": float(start_wavelength),
                        "end_wavelength": float(end_wavelength),
                        "min_v": float(min_v),
                        "max_v": float(max_v),
                        "interval_v": float(interval_v),
                        "filename": filename,
                    })


                elif filename.startswith("passivebentwg_") and filename.endswith(".ldf"):
                    _, start_wavelength, end_wavelength, _ = filename.split("_")
                    passiveBentWg.append({
                        "start_wavelength": float(start_wavelength),
                        "end_wavelength": float(end_wavelength),
                        "filename": filename,
                    })
                    passiveBentWg.append(filename)
            break

        self.wgT = wgT
        self.activeBentWg = activeBentWg
        self.passiveBentWg = passiveBentWg
        self.neff = neff

    def get_param_suggestions(self):

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

    def run(self, params):
        print("API run func called. Params:")
        pprint(params)
        # TODO: split each component into own function
        # TODO: look into if wavelength precision changes affect cached sims

        # TODO
        # heat
        cached_to_use = None
        for cached in self.wgT:
            if (params['max_v'] <= cached['max_v'] and
                params['min_v'] >= cached['min_v'] and
                params['interval_v'] >= cached['interval_v']):
                cached_to_use = cached
                break

        if not cached_to_use:
            print("Run heat sim")
            # run sim


        # active bend
        cached_to_use = None
        for cached in self.activeBentWg:
            if (params['min_v'] >= cached['min_v'] and
                params['max_v'] <= cached['max_v'] and
                params['interval_v'] >= cached['interval_v'] and
                params['start_wavelength'] >= cached['start_wavelength'] and
                params['end_wavelength'] <= cached['end_wavelength']):
                cached_to_use = cached
                break

        if not cached_to_use:
            # run sim
            print("run active sim")

        # passive bend
        cached_to_use = None
        for cached in self.passiveBentWg:
            if (params['start_wavelength'] >= cached['start_wavelength'] and
                params['end_wavelength'] <= cached['end_wavelength']):
                cached_to_use = cached
                break

        if not cached_to_use:
            # run sim
            print("run passive sim")

        # neff
        cached_to_use = None
        for cached in self.neff:
            if (params['min_v'] >= cached['min_v'] and
                params['max_v'] <= cached['max_v'] and
                params['interval_v'] >= cached['interval_v'] and
                params['source_wavelength'] <= cached['laser_wavelength']):
                cached_to_use = cached
                break

        if not cached_to_use:
            # run sim
            print("run neff sim")
