# Silicon Photonic Neuromorphic Chip Simulation

<i>Author: Francesco Virga</i>

## Usage

* Install dependencies

```
pip install -r requirements.txt
```

* Run simulation platform

```
python main.py
```

* The application will walk you through setting up a simulation and give you an opportunity to download results.

## Code Structure

This repository contains 3 main modules which make up the Silicon Photonic Neuromorphic software simulation package
* <b>Lumerical</b>: This module contains all resources related to Lumerical simulations. Cached simulation files are also stored here. <i>interface.py</i> implements the Lumerical Automation API to control simulations.
* <b>CLI</b>: This module collects input from a user using an intuitive command-line interface. It prompts the user for required information, making suggestions and aggregating the information for Lumerical.
* <b>API</b>: This module acts as the middleman between the CLI and Lumerical. It receives inputs from the CLI module and decides how to use them with the Lumerical module.

* <b>Extras</b> This folder is not part of the software but has various code files and data I used to experiment, test and build this project. Most of the files are not setup to be used out of the box but could provide some solid resources to better understand Lumerical, INTERCONNECT and the Automation API.
