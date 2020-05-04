# Silicon Photonic Neuromorphic Chip Simulation

<i>Author: Francesco Virga</i>

## Code Structure

This repository contains 3 main modules which make up the Silicon Photonic Neuromorphic software simulation package
* <b>Lumerical</b>: This module contains all resources related to Lumerical simulations. Cached simulation files are also stored here. <i>interface.py</i> implements the Lumerical Automation API to control simulations.
* <b>CLI</b>: This module collects input from a user using an intuitive command-line interface. It prompts the user for required information, making suggestions and aggregating the information for Lumerical.
* <b>API</b>: This module acts as the middleman between the CLI and Lumerical. It receives inputs from the CLI module and decides how to use them with the Lumerical module. It also decides which simulation files can be used from the cache and which need to be re-simulated based on the user's inputs.

    <i>Note: Default simulation resources are provided at the root level of the <i>Lumerical</i> module (the same resources that are stored in the cache). These have been heavily tested, so if any strange behaviour occurs with cached simulation data, try running the same simulation manually using the default files (as long as you haven't saved any changes to <i>weight_bank.icp</i> these should be setup to be used by default <b>only when opening & running the simulation manually, not through the CLI</b>)

* <b>Extras</b>: This folder is not part of the software but has various code files and data I used to experiment, test and build this project. Most of the files are not setup to be used out of the box but could provide some solid resources to better understand Lumerical, INTERCONNECT and the Automation API.


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


## Useful Resources

I tried to aggregate a few resources I found useful while building this application. Note that this is not a complete list.

* [INTERCONNECT Product Reference Manual](https://support.lumerical.com/hc/en-us/articles/360037304774-INTERCONNECT-product-reference-manual) - Contains all information about INTERCONNECT
* [Lumerical Scripting Language](https://support.lumerical.com/hc/en-us/articles/360037228834-Lumerical-scripting-language-By-category) - All Lumerical scripting commands. Note that these are all of the same commands for the Automation API
* [Parameter sweeps, Optimization and Monte Carlo analysis overview](https://support.lumerical.com/hc/en-us/articles/360034922853-Parameter-sweeps-Optimization-and-Monte-Carlo-analysis-overview) - Information on sweeps, scripting and some solid examples
* [Ring modulator](https://support.lumerical.com/hc/en-us/articles/360042322794) - Ring modulator simulation set
* [Electro-optical modulator based on a graphene-coated waveguide](https://support.lumerical.com/hc/en-us/articles/360042243634) - I was not able to get to this simulation example but it looks promising
* [Thermally tuned waveguide (FDE)](https://support.lumerical.com/hc/en-us/articles/360042833673) - Thermally tuned waveguide simulation set
