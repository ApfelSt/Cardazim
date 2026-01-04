from pathlib import Path
from setuptools import find_packages, setup
from typing import List


REQUIREMENTS_FILE = Path('.') / 'requirements.txt'


def _read_requirements(file: Path) -> List[str]:
    with open(file) as req_file:
        lines = req_file.readlines()
    return [line.rstrip() for line in lines]


setup(
    name='cardazim',
    version='0.0.1',
    author='Cardazim',
    author_email='cardazim@protonmail.com',
    description='A template for the cardazim project!',
    long_description='''A basic template intended as a reference guide for the Cardazim Project!
    Use wisely!
    ''',
    packages=find_packages('cardazim'),
    install_requires=_read_requirements(REQUIREMENTS_FILE)
)
