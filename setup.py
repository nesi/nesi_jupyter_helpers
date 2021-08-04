from setuptools import setup, find_packages

setup(
    name="nesi_jupyter_helpers",
    version="0.2.0",
    description="Tools to help users of jupyter.nesi.org.nz",
    url="https://github.com/nesi/nesi_jupyter_helpers",
    author=" New Zealand eScience Infrastructure",
    author_email="support@nesi.org.nz",
    license="MIT",
    packages=find_packages(),
    install_requires=["ipykernel", "defopt", "jupyter_core"],
    extras_require={"dev": ["black", "flake8", "pytest", "nbformat", "nbconvert"]},
    entry_points={
        "console_scripts": ["nesi-add-kernel=nesi_jupyter_helpers.add_kernel:main"]
    },
)
