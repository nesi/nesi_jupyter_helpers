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

TODO example to add a TF kernel, using NeSI's module
```
nesi-add-kernel tf_kernel TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2
```

Example to add a TF kernel, using NeSI's module, and share the kernel with other members of your NeSI project
```
nesi-add-kernel --shared tf_kernel TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2
```

TODO example to add a conda env, using it's path


## TODOs

- add venv option
- add singularity option
- check conda module not loaded by user
