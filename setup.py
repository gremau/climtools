"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='climtools',
    description='Tools for working with weather or climate data',
    long_description=long_description,
    version='2021.1b1',
    url='https://github.com/gremau/climtools',  # Optional
    author='Gregory E. Maurer',  # Optional
    author_email='gmaurer@nmsu.edu',  # Optional
    package_dir={'': 'climtools'},
    packages=find_packages(where='climtools'),
    install_requires=[
        'pandas',
        'matplotlib']
    )
