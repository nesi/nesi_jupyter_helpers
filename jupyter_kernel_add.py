#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path


WRAPPER_TEMPLATE="""\
#!/usr/bin/env bash

# This script is used in ~/.local/share/jupyter/kernels/{kernel_name}/kernel.json
# to load environment modules before starting the kernel.

# start with a clean environment
module purge

# load required modules here
module load slurm NeSI
module load {modules}

{conda}

# run the kernel
exec python $@
"""

CONDA_TEMPLATE="""\
# load conda & CUDA modules on Mahuika or Maui
if hostname | grep -q "maui"; then
    CONDA_MODULE="Anaconda3/2020.02-GCC-7.1.0"
else
    CONDA_MODULE="Miniconda3/4.8.2"
fi
module load "$CONDA_MODULE"

# activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda deactivate  # enforce base environment to be unloaded
conda activate {CONDA_VENV_PATH}
"""

kernel_name = "test_script"
modules = ["TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2"]

# create a new kernel
# python -m ipykernel install --user --name $(KERNEL_NAME)
subprocess.run(
    ["python", "-m", "ipykernel", "install", "--user", "--name", kernel_name],
    check=True
)

kernel_dir = Path.home() / ".local/share/jupyter/kernels/" / kernel_name

# add a bash wrapper script
wrapper_script_code = WRAPPER_TEMPLATE.format(
    kernel_name=kernel_name, conda="", modules=" ".join(modules)
)
wrapper_script = kernel_dir / "wrapper.bash"
wrapper_script.write_text(wrapper_script_code)

# modify the kernel description file
kernel_def = {
     "argv": [
         str(wrapper_script),
         "-m",
         "ipykernel_launcher",
         "-f",
         "{connection_file}"
     ],
     "display_name": kernel_name,
     "language": "python"
}
with (kernel_dir / "kernel.json").open("w") as fd:
    json.dump(kernel_def, fd, indent=4)