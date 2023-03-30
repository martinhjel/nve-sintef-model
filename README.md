# nve-sintef-model
A python library of functions for using SINTEF models.
Developed in NVE.
Current version 0.0.1 released in January 2023.

## Installation

To install the package run:

pip install git+https://github.com/NVE/nve-sintef-model.git#egg=nve-sintef-model

To uninstall the package run:

pip uninstall nve_sintef_model

## Contributing

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging. If you don't have Poetry installed, you can install it by following the [official installation guide](https://python-poetry.org/docs/#installation).

### Installing the project
To install this project and its dependencies, follow these steps:

1. Clone the repository:
```
git clone https://github.com/your_username/your_project_name.git

```
2. Navigate to the project directory:
```
cd your_project_name
```
3. Install the project dependencies:
```
poetry install
````

This command will create a virtual environment (if it doesn't exist) and install the project dependencies inside it.

### Updating the project
If you need to update the project's dependencies, run:
```
poetry update
```
This command will update the installed packages to their latest compatible versions.

### Usage
To run a script or command within the project's virtual environment, use poetry run. For example, to run a Python script:
```
poetry run python your_script.py
```
You can also use poetry shell to activate the virtual environment in your current terminal session:

```
poetry shell
```
Once the virtual environment is activated, you can run commands without the poetry run prefix.

## Usage

The following modules are included into versjon 0.0.1 per January 2023:
* exe
* input: latest functions for updating the model input (2022-2023)
* io: functions for processing model input and output
* kalibrering: functions used for automatic model calibration
* output: latest functions for reading model output (2022-2023)
* plot: functions for plotting model output
* prognoseresultater: functions for runing model version used for short-term forecasting
* utils: diverse utility functions used by other skripts


