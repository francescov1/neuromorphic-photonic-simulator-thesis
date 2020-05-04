from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

class CLI:

    def __init__(self, defaults):
        self.defaults = defaults

    def run(self):
        # NOTE: a bug in PyInquirer ignores the default for lists
        # a workaround is to place your default as the first element
        # in the array. See sim_type and heater_sim_type questions
        questions = [
            {
                'type': 'list',
                'name': 'sim_type',
                'message': 'What type of simulation would you like to run?',
                'choices': ['scatter', 'single laser'],
                'default': 'scatter'
            },
            {
                'type': 'input',
                'name': 'source_wavelength',
                'message': 'Source wavelength (m) (for scatter, this is the center wavelength):',
                'default': self.defaults['laser_wavelength']
            },
            {
                'type': 'input',
                'name': 'wavelength_window',
                'message': 'Wavelength window (m):',
                'default': self.defaults['wavelength_window'],
                'when': lambda answers: answers['sim_type'] == 'scatter'
            },
            {
                'type': 'list',
                'name': 'heater_sim_type',
                'message': 'How do you want to simulate the N-doped heater?',
                'choices': ['constant voltage', 'sweep'],
                'default': 'constant voltage'
            },
            {
                'type': 'input',
                'name': 'constant_v',
                'message': 'Voltage applied to N-doped heater (V):',
                'default': self.defaults['constant_v'],
                'when': lambda answers: answers['heater_sim_type'] == 'constant voltage'
            },
            {
                'type': 'input',
                'name': 'min_v',
                'message': 'Min voltage for N-doped heater sweep (V):',
                'default': self.defaults['min_v'],
                'when': lambda answers: answers['heater_sim_type'] == 'sweep'
            },
            {
                'type': 'input',
                'name': 'max_v',
                'message': 'Max voltage for N-doped heater sweep (V):',
                'default': self.defaults['max_v'],
                'when': lambda answers: answers['heater_sim_type'] == 'sweep'
            },
            {
                'type': 'input',
                'name': 'interval_v',
                'message': 'Voltage precision for N-doped heater (V):',
                'default': self.defaults['interval_v'],
                'when': lambda answers: answers['heater_sim_type'] == 'sweep'
            }
        ]

        params = prompt(questions)
        params['source_wavelength'] = float(params['source_wavelength'])

        # this is to standardize parameter names
        if (params['sim_type'] == "single laser"):
            params['start_wavelength'] = params['source_wavelength']
            params['end_wavelength'] = params['source_wavelength']
        else:
            params['wavelength_window'] = float(params['wavelength_window'])

            half_window = params['wavelength_window'] / 2
            params['start_wavelength'] = params['source_wavelength'] - half_window
            params['end_wavelength'] = params['source_wavelength'] + half_window

        if params['heater_sim_type'] == "constant voltage":
            params['constant_v'] = float(params['constant_v'])
            params['min_v'] = params['constant_v']
            params['max_v'] = params['constant_v']
            params['interval_v'] = 1
        else:
            params['min_v'] = float(params['min_v'])
            params['max_v'] = float(params['max_v'])
            params['interval_v'] = float(params['interval_v'])

        self.params = params
        return params
