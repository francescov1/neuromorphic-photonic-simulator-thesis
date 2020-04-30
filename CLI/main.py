from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError

class CLI:

    def __init__(self, defaults):
        self.defaults = defaults

    def run(self):
        questions = [
            {
                'type': 'list',
                'name': 'sim_type',
                'message': 'What type of simulation would you like to run?',
                'choices': [
                    'scatter',
                    'single laser'
                ],
                'default': 'single laser'
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
                'choices': ['sweep', 'constant voltage'],
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
                'default': self.defaults['interval_v']
            }
        ]

        params = prompt(questions)
        self.params = params
        return params
