import uuid
from subprocess import run
from pathlib import Path
import shutil

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

from nesi_jupyter_helpers.add_kernel import add_kernel


def execute_notebook(code, kernel_name):
    """create a dummy notebook and execute it using a given kernel"""
    nb = nbformat.v4.new_notebook()
    nb["cells"].append(nbformat.v4.new_code_cell(code))
    ep = ExecutePreprocessor(kernel_name=kernel_name)
    ep.preprocess(nb)


def test_tf_module():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    try:
        add_kernel(kernel_name, "TensorFlow/2.4.1-gimkl-2020a-Python-3.8.2")
        execute_notebook(
            "import tensorflow; assert tensorflow.__version__ == '2.4.1'", kernel_name
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])


def test_conda_env_path():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    conda_path = Path.cwd() / kernel_name
    run(
        "module purge && module load Miniconda3/4.10.3 && "
        f"conda create -p {conda_path} -y python=3.8 numpy=1.19.1",
        shell=True,
        check=True,
    )
    try:
        add_kernel(kernel_name, conda_path=conda_path)
        execute_notebook(
            "import numpy; assert numpy.__version__ == '1.19.1'", kernel_name
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
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
        f"conda create -n {kernel_name} -y python=3.8 numpy=1.19.1",
        shell=True,
        check=True,
    )
    try:
        add_kernel(kernel_name, conda_name=kernel_name)
        execute_notebook(
            "import numpy; assert numpy.__version__ == '1.19.1'", kernel_name
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
        run(
            "module purge && module load Miniconda3/4.10.3 && "
            f"conda env remove -n {kernel_name} -y",
            shell=True,
            check=True,
        )


def test_venv():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    venv = Path.cwd() / kernel_name
    run(
        "module purge && module load Python/3.8.2-gimkl-2020a && "
        f"python -m venv {venv} && {venv}/bin/pip install numpy==1.19.1",
        shell=True,
        check=True,
    )
    try:
        add_kernel(kernel_name, "Python/3.8.2-gimkl-2020a", venv=venv)
        execute_notebook(
            "import numpy; assert numpy.__version__ == '1.19.1'", kernel_name
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
        shutil.rmtree(venv)


def test_container_python():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    container = Path.cwd() / f"{kernel_name}.sif"
    run(
        "module purge && module load Python/3.11.6-foss-2023a && "
        f"apptainer pull {container} docker://jupyter/base-notebook:lab-3.0.16",
        shell=True,
        check=True,
    )
    try:
        # -cp: a python kernel running inside the container (needs ipykernel)
        add_kernel(kernel_name, container_python=container)
        execute_notebook(
            "import jupyterlab; assert jupyterlab.__version__ == '3.0.16'", kernel_name
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
        container.unlink()


def test_container_python_args():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    container = Path.cwd() / f"{kernel_name}.sif"
    run(
        "module purge && module load Python/3.11.6-foss-2023a && "
        f"apptainer pull {container} docker://jupyter/base-notebook:lab-3.0.16",
        shell=True,
        check=True,
    )
    try:
        add_kernel(
            kernel_name, container_python=container, container_args="--no-home"
        )
        execute_notebook(
            "import jupyterlab; assert jupyterlab.__version__ == '3.0.16'", kernel_name
        )
        execute_notebook(
            "from pathlib import Path; assert not Path.home().exists()", kernel_name
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
        container.unlink()


def test_container_bash():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    container = Path.cwd() / f"{kernel_name}.sif"
    # -cb runs bash_kernel on the host (from the loaded Python module), so
    # bash_kernel must be importable by that interpreter
    run(
        "module purge && module load Python/3.11.6-foss-2023a && "
        "pip install --user bash_kernel && "
        f"apptainer pull {container} docker://jupyter/base-notebook:lab-3.0.16",
        shell=True,
        check=True,
    )
    try:
        add_kernel(kernel_name, "Python/3.11.6-foss-2023a", container_bash=container)
        # the kernel is a bash kernel dispatching each cell into the container,
        # so this bash cell runs the container's python and checks JupyterLab
        execute_notebook(
            "python -c \"import jupyterlab; "
            "assert jupyterlab.__version__ == '3.0.16'\"",
            kernel_name,
        )
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
        container.unlink()


def test_container_bash_args():
    kernel_name = f"test_kernel_{uuid.uuid4()}"
    container = Path.cwd() / f"{kernel_name}.sif"
    run(
        "module purge && module load Python/3.11.6-foss-2023a && "
        "pip install --user bash_kernel && "
        f"apptainer pull {container} docker://jupyter/base-notebook:lab-3.0.16",
        shell=True,
        check=True,
    )
    try:
        add_kernel(
            kernel_name,
            "Python/3.11.6-foss-2023a",
            container_bash=container,
            container_args="--no-home",
        )
        execute_notebook(
            "python -c \"import jupyterlab; "
            "assert jupyterlab.__version__ == '3.0.16'\"",
            kernel_name,
        )
        # with --no-home the host home directory is not mounted in the container
        execute_notebook('test ! -e "$HOME"', kernel_name)
    finally:
        run(["jupyter-kernelspec", "remove", "-f", kernel_name])
        container.unlink()
