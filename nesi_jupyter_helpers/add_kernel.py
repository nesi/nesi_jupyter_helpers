import sys
import json
import tempfile
import subprocess
import typing as T
from pathlib import Path
from argparse import ArgumentParser, Namespace

WRAPPER_TEMPLATE = """\
#!/usr/bin/env bash

set -e

# start with a clean environment
module purge

# load required modules
module load slurm NeSI  # ensure these modules gets loaded even on Maui ancil.
{modules_txt}
{conda_txt}
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


def parse_args() -> Namespace:
    """Command line input parser"""

    parser = ArgumentParser(
        description="register a new Jupyter kernel, with a wrapper script to "
        "load NeSI modules",
    )
    parser.add_argument("kernel_name", help="Jupyter kernel name")
    parser.add_argument(
        "module", nargs="*", help="NeSI module to load before running the kernel"
    )
    parser.add_argument("--conda-path", help="path to a Conda environment")
    parser.add_argument("--conda-name", type=Path, help="name of a Conda environment")

    args = parser.parse_args()

    if args.conda_path is not None and args.conda_name is not None:
        sys.exit("error: --conda-path and --conda-name options are not compatible")
    elif args.conda_path is not None:
        args.conda = str(Path(args.conda_path).resolve())
    elif args.conda_name is not None:
        args.conda = args.conda_name
    else:
        args.conda = None

    return args


def add_kernel(
    kernel_name: str,
    modules: T.Iterable[str],
    conda: T.Optional[str] = None,
):
    """Register a new jupyter kernel, with a wrapper script to load NeSI modules"""

    kernel_dir = Path.home() / ".local/share/jupyter/kernels/" / kernel_name

    # check kernel directory does not already exist
    if kernel_dir.exists():
        sys.exit(f"Error: Kernel already exists: {kernel_dir}")

    # create a bash wrapper script
    if len(modules) == 0:
        modules_txt = ""
    else:
        modules_txt = "module load " + " ".join(modules)

    if conda is None:
        conda_txt = ""
    else:
        conda_txt = CONDA_TEMPLATE.format(conda_venv=conda)

    wrapper_script_code = WRAPPER_TEMPLATE.format(
        conda_txt=conda_txt, modules_txt=modules_txt
    )

    # check the wrapper script actually runs
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as fh:
        fh.write(wrapper_script_code)
    tmp_wrapper_script = Path(fh.name)
    tmp_wrapper_script.chmod(0o770)
    try:
        subprocess.run(
            [tmp_wrapper_script, "--version"],
            check=True,
            capture_output=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        tmp_wrapper_script.unlink()
        sys.exit("Error: unable to create wrapper script, check modules and other options are correct")

    # check ipykernel is installed in the kernel environment
    try:
        subprocess.run(
            [tmp_wrapper_script, "-m", "ipykernel_launcher", "--version"],
            check=True,
            capture_output=True,
            universal_newlines=True,
        )
    except subprocess.CalledProcessError as exc:
        print(exc.stdout)
        print(exc.stderr)
        tmp_wrapper_script.unlink()
        sys.exit("Error: ipykernel is not installed in the kernel environment")

    tmp_wrapper_script.unlink()

    # create a new kernel
    subprocess.run(
        ["python", "-m", "ipykernel", "install", "--user", "--name", kernel_name],
        check=True,
    )

    # add the wrapper script to the kernel dir
    wrapper_script = kernel_dir / "wrapper.bash"
    wrapper_script.write_text(wrapper_script_code)
    wrapper_script.chmod(0o770)
    print(f"Added wrapper script in {wrapper_script}")

    # modify the kernel description file
    kernel_def = {
        "argv": [
            str(wrapper_script),
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
    args = parse_args()
    add_kernel(args.kernel_name, args.module, args.conda)
