# NeSI Jupyter helpers

This repository contains a Python package providing tools to help users of 
[jupyter.nesi.org.nz](https://jupyter.nesi.org.nz).


## Installation

You can install this Python package in your home using `pip`:
```
pip install --user git+https://github.com/nesi/nesi_jupyter_helpers
```


## Getting started

This package provide the `nesi-add-kernel` command-line tool to add a custom
kernel in the JupyterLab interface. You can use it to specify which modules to
load before running a kernel and which Conda or Python virtual environment to
use.

To list all available options, use the `-h` or `--help` options as follows:
```
nesi-add-kernel --help
```

Here is an example to add a TensorFlow kernel, using NeSI's module:
```
nesi-add-kernel tf_kernel TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2
```

and to share the kernel with other members of your NeSI project:
```
nesi-add-kernel --shared tf_kernel_shared TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2
```

To add a Conda environment created using `conda create -p <conda_env_path>`, use:
```
nesi-add-kernel my_conda_env -p <conda_env_path>
```
otherwise if created using `conda create -n <conda_env_name>`, use:
```
nesi-add-kernel my_conda_env -n <conda_env_name>
```

If you want to use a Python virtual environment, don't forget to specify which
Python module you used to create it.

For example, if we create a virtual environment named `my_test_venv` using
Python 3.8.2:
```
module purge
module load Python/3.8.2-gimkl-2020a
python -m venv my_test_venv
```
to create the corresponding `my_test_kernel` kernel, we need to use the command:
```
nesi-add-kernel my_test_kernel Python/3.8.2-gimkl-2020a --venv my_test_venv
```


## For maintainers

To run the tests, you need to log in Mahuika and install the `dev` dependencies:
```
module purge && module load Python/3.8.2-gimkl-2020a
git clone https://github.com/nesi/nesi_jupyter_helpers
cd nesi_jupyter_helpers
python -m venv venv
. venv/bin/activate
pip install -e .[dev]
pytest
```


## TODOs

- add a test for "--shared"
- run some code using the kernel in tests
- add tests for incompatible options
- add singularity option
