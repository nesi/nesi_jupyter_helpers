#!/usr/bin/env python3

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
module load {modules}
{conda}
# run the kernel
exec python $@
"""

CONDA_TEMPLATE = """\

# load conda & CUDA modules on Mahuika or Maui
if hostname | grep -q "maui"; then
    CONDA_MODULE="Anaconda3"
else
    CONDA_MODULE="Miniconda3"
fi
module load "$CONDA_MODULE"

# activate conda environment
source $(conda info --base)/etc/profile.d/conda.sh
conda deactivate  # enforce base environment to be unloaded
conda activate {CONDA_VENV_PATH}

"""


def parse_args(args: T.Optional[T.Iterable[str]] = None) -> Namespace:
    """Command line input parser"""
    parser = ArgumentParser(
        description="register a new Jupyter kernel",
    )
    parser.add_argument("kernel_name", help="Jupyter kernel name")
    parser.add_argument(
        "module", nargs="+", help="NeSI module to load before running the kernel"
    )
    return parser.parse_args(args)


def main(kernel_name: str, modules: T.Iterable[str]):
    """Register a new jupyter kernel, with a wrapper script to load modules"""

    # create a new kernel
    subprocess.run(
        ["python", "-m", "ipykernel", "install", "--user", "--name", kernel_name],
        check=True,
    )

    kernel_dir = Path.home() / ".local/share/jupyter/kernels/" / kernel_name

    # add a bash wrapper script
    wrapper_script_code = WRAPPER_TEMPLATE.format(conda="", modules=" ".join(modules))
    wrapper_script = kernel_dir / "wrapper.bash"
    wrapper_script.write_text(wrapper_script_code)
    wrapper_script.chmod(0o770)

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
    with (kernel_dir / "kernel.json").open("w") as fd:
        json.dump(kernel_def, fd, indent=4)


if __name__ == "__main__":
    args = parse_args()
    main(args.kernel_name, args.module)
