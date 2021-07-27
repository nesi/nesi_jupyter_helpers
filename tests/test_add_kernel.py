import uuid
from subprocess import run
from pathlib import Path
import shutil

from nesi_jupyter_helpers.add_kernel import add_kernel


def test_tf_module():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    add_kernel(kernel_name, "TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2")
    run(f"jupyter-kernelspec remove -f {kernel_name}", shell=True, check=True)


def test_conda_env_path():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    conda_path = Path.cwd() / kernel_name
    run(
        "module purge && module load Miniconda3/4.10.3 && "
        f"conda create -p {conda_path} -y python=3.8",
        shell=True,
        check=True,
    )
    add_kernel(kernel_name, conda_path=conda_path)
    run(f"jupyter-kernelspec remove -f {kernel_name}", shell=True, check=True)
    run(
        "module purge && module load Miniconda3/4.10.3 && "
        f"conda env remove -p {conda_path} -y",
        shell=True,
        check=True,
    )


def test_conda_env_name():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    run(
        "module purge && module load Miniconda3/4.10.3 && "
        f"conda create -n {kernel_name} -y python=3.8",
        shell=True,
        check=True,
    )
    add_kernel(kernel_name, conda_name=kernel_name)
    run(f"jupyter-kernelspec remove -f {kernel_name}", shell=True, check=True)
    run(
        "module purge && module load Miniconda3/4.10.3 && "
        "conda env remove -n {kernel_name} -y",
        shell=True,
        check=True,
    )


def test_venv():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    venv = Path.cwd() / kernel_name
    run(
        "module purge && module load Python/3.8.2-gimkl-2020a && "
        f"python -m venv {venv}",
        shell=True,
        check=True,
    )
    add_kernel(kernel_name, "Python/3.8.2-gimkl-2020a", venv=venv)
    run(f"jupyter-kernelspec remove -f {kernel_name}", shell=True, check=True)
    shutil.rmtree(venv)