# Silicon Photonic Neuromorphic Chip Simulation

<i>Author: Francesco Virga</i>

## Usage

1. In <i>Lumerical/interface.py</i>, set the Lumerical version and Lumerical installation path. For more information on how to find this information, see the Automation API documentation.

2. Install dependencies

```
pip install -r requirements.txt
```

3. Run simulation platform

```
python main.py
```

4. The application will walk you through setting up a simulation and give you an opportunity to download results.

## Code Structure

This repository contains 3 main modules which make up the Silicon Photonic Neuromorphic software simulation package
* <b>Lumerical</b>: This module contains all resources related to Lumerical simulations. Cached simulation files are also stored here. <i>interface.py</i> implements the Lumerical Automation API to control simulations.
* <b>CLI</b>: This module collects input from a user using an intuitive command-line interface. It prompts the user for required information, making suggestions and aggregating the information for Lumerical.
* <b>API</b>: This module acts as the middleman between the CLI and Lumerical. It receives inputs from the CLI module and decides how to use them with the Lumerical module. It also decides which simulation files can be used from the cache and which need to be re-simulated based on the user's inputs.

    <i>Note: Default simulation resources are provided at the root level of the <i>Lumerical</i> module (the same resources that are stored in the cache). These have been heavily tested, so if any strange behaviour occurs with cached simulation data, try running the same simulation manually using the default files (as long as you haven't saved any changes to <i>weight_bank.icp</i> these should be setup to be used by default <b>only when opening & running the simulation manually, not through the CLI</b>)

* <b>Extras</b> This folder is not part of the software but has various code files and data I used to experiment, test and build this project. Most of the files are not setup to be used out of the box but could provide some solid resources to better understand Lumerical, INTERCONNECT and the Automation API.
