import os
import sys
import json
import tempfile
import subprocess
import shutil
import typing as T
from pathlib import Path

import defopt


WRAPPER_TEMPLATE = """\
#!/usr/bin/env bash

set -e

# start with a clean environment
module purge

# load required modules
module load slurm NeSI  # ensure these modules gets loaded even on Maui ancil.
{modules_txt}
{conda_txt}
{venv_txt}
# run the kernel
exec python $@
"""

CONDA_TEMPLATE = """\

# load conda & CUDA modules on Mahuika or Maui
if hostname | grep -q "maui"; then
    module load Anaconda3
else
    module load Miniconda3
fi

# activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda deactivate  # enforce base environment to be unloaded
conda activate {conda_venv}
"""

VENV_TEMPLATE = """\

# activate virtual environment
source {venv_activate_script}
"""


def add_kernel(
    kernel_name: str,
    *module: str,
    conda_path: T.Optional[Path] = None,
    conda_name: T.Optional[str] = None,
    venv: T.Optional[Path] = None,
    shared: bool = False,
):
    """Register a new jupyter kernel, with a wrapper script to load NeSI modules

    :param kernel_name: Jupyter kernel name
    :param module: NeSI module(s) to load before running the kernel
    :param conda-path: path to a Conda environment
    :param conda-name: name of a Conda environment
    :param venv: path to a Python virtual environment
    :param shared: share the kernel with other members of your NeSI project
    """

    if conda_path is not None and conda_name is not None:
        sys.exit("ERROR: --conda-path and --conda-name options are not compatible")

    if (conda_path is not None or conda_name is not None) and venv is not None:
        sys.exit("ERROR: --conda-* and --venv options are not compatible")

    # path to kernel directory
    if shared:
        account = os.getenv("SLURM_JOB_ACCOUNT")
        if account is None:
            sys.exit(
                "ERROR: cannot determine project to share kernel with, try"
                "running within a Jupyter terminal"
            )
        print(f"Creating shared kernel for {account}")
        prefix_dir = Path(f"/nesi/project/{account}/.jupyter")
        kernel_dir = prefix_dir / "share/jupyter/kernels/" / kernel_name
    else:
        kernel_dir = Path.home() / ".local/share/jupyter/kernels/" / kernel_name

    # check kernel directory does not already exist
    if kernel_dir.exists():
        sys.exit(f"ERROR: Kernel already exists: {kernel_dir}")

    # create a bash wrapper script
    if len(module) == 0:
        modules_txt = ""
    else:
        modules_txt = "module load " + " ".join(module)

    # add conda environment
    if conda_name is None and conda_path is None:
        conda_txt = ""
    else:
        if shared:
            print(
                "Make sure your conda environment is accessible to members of "
                f"{account}"
            )
        conda_venv = conda_path.resolve() if conda_name is None else conda_name
        conda_txt = CONDA_TEMPLATE.format(conda_venv=conda_venv)

    # add virtual environment
    if venv is None:
        venv_txt = ""
    else:
        if shared:
            print(
                "Make sure your virtual environment is accessible to members of "
                f"{account}"
            )
        venv = venv.resolve()
        if not venv.is_dir():
            sys.exit(
                f"ERROR: --venv ({venv}) should point to a virtual environment "
                "directory"
            )
        venv_activate_script = venv / "bin/activate"
        if not venv_activate_script.exists():
            sys.exit(
                f"ERROR: --venv ({venv}) does not appear to be a virtual "
                "environment (cannot find bin/activate)"
            )
        venv_txt = VENV_TEMPLATE.format(venv_activate_script=venv_activate_script)
        print(
            "Make sure you have specified the appropriate Python module(s) for "
            "your virtual environment"
        )

    wrapper_script_code = WRAPPER_TEMPLATE.format(
        conda_txt=conda_txt, modules_txt=modules_txt, venv_txt=venv_txt
    )

    # use a temporary file for testing purpose
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as fh:
        fh.write(wrapper_script_code)

    wrapper_script = Path(fh.name)
    wrapper_script.chmod(0o770)

    print("Testing wrapper script")
    try:
        subprocess.run(
            [wrapper_script, "--version"],
            check=True,
            capture_output=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        wrapper_script.unlink()
        sys.exit(
            "ERROR: unable to create wrapper script, check modules and other "
            "options are correct"
        )

    print("Checking & installing ipykernel package in the kernel environment")
    try:
        subprocess.run(
            [wrapper_script, "-m", "pip", "install", "ipykernel"],
            check=True,
            capture_output=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        wrapper_script.unlink()
        sys.exit("ERROR: ipykernel could not be installed in the kernel environment")

    # create a new kernel
    cmdargs = ["python", "-m", "ipykernel", "install", "--name", kernel_name]
    if shared:
        cmdargs.extend(["--prefix", prefix_dir])
    else:
        cmdargs.append("--user")
    print(f"Installing kernel: {' '.join(map(str, cmdargs))}")
    subprocess.run(cmdargs, check=True)

    # add the wrapper script to the kernel dir
    wrapper_script_dest = kernel_dir / "wrapper.bash"
    shutil.move(wrapper_script, wrapper_script_dest)
    print(f"Added wrapper script in {wrapper_script_dest}")

    # modify the kernel description file
    kernel_def = {
        "argv": [
            str(wrapper_script_dest),
            "-m",
            "ipykernel_launcher",
            "-f",
            "{connection_file}",
        ],
        "display_name": kernel_name,
        "language": "python",
    }
    kernel_file = kernel_dir / "kernel.json"
    with kernel_file.open("w") as fd:
        json.dump(kernel_def, fd, indent=4)
    print(f"Updated kernel JSON file {kernel_file}")

    print("\nUse the following command to remove the kernel:")
    print(f"\n    jupyter-kernelspec remove {kernel_name}\n")


def main():
    defopt.run(add_kernel)
