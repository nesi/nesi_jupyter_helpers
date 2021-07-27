# NeSI Jupyter helpers

This repository contains a Python package providing tools to help users of 
[jupyter.nesi.org.nz](https://jupyter.nesi.org.nz).


## Installation

You can install this Python package in your home using `pip`:
```
pip install --user git+https://github.com/nesi/nesi_jupyter_helpers
```


## Getting started

TODO document `nesi-add-kernel` usage

Example to add a TensorFlow kernel, using NeSI's module:
```
nesi-add-kernel tf_kernel TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2
```

and to share the kernel with other members of your NeSI project:
```
nesi-add-kernel --shared tf_kernel_shared TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2
```

To add a Conda environment created using `conda create -p <conda_env_path>`, use:
```
nesi-add-kernel my_conda_env --conda-path <conda_env_path>
```
otherwise if created using `conda create -n <conda_env_name>`, use:
```
nesi-add-kernel my_conda_env --conda-name <conda_env_name>
```

TODO add same examples for Python venv


## TODOs

- add singularity option
