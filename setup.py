from setuptools import setup, find_packages

setup(
    name='nesi_jupyter_helpers',
    version='0.1.0',
    description="Tools to help users to use NeSI's JupyterHub",
    url='https://github.com/nesi/nesi_jupyter_helpers',
    author=' New Zealand eScience Infrastructure',
    author_email='support@nesi.org.nz',
    license='MIT',
    packages=find_packages(),
    install_requires=['ipykernel'],
    extra_require={
        "dev": ["black", "flake8"]
    }
)