#!/usr/bin/env python3

import sys
import json
import subprocess
import typing as T
from pathlib import Path
from argparse import ArgumentParser, Namespace

WRAPPER_TEMPLATE = """\
#!/usr/bin/env bash

# start with a clean environment
module purge

# load required modules
module load slurm NeSI
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


def main(
    kernel_name: str,
    modules: T.Iterable[str],
    conda: T.Optional[str] = None,
):
    """Register a new jupyter kernel, with a wrapper script to load NeSI modules"""

    # create a new kernel
    subprocess.run(
        ["python", "-m", "ipykernel", "install", "--user", "--name", kernel_name],
        check=True,
    )

    kernel_dir = Path.home() / ".local/share/jupyter/kernels/" / kernel_name

    # add a bash wrapper script
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


if __name__ == "__main__":
    args = parse_args()
    main(args.kernel_name, args.module, args.conda)
