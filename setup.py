# setup.py
# Setup installation for the application.

from pathlib import Path

from setuptools import setup

BASE_DIR = Path(__file__).parent

with open(Path(BASE_DIR, "requirements.txt")) as file:
    required_packages = [ln.strip() for ln in file.readlines()]

dev_packages = ["black==21.7b0", "flake8==3.9.2", "isort==5.9.3"]

setup(
    name="magicgenerator",
    version="0.1",
    description="Console utility to generate test data.",
    author="Dmytro Shurko",
    python_requires=">=3.6",
    install_requires=[required_packages],
    extras_require={"dev": dev_packages},
    entry_points={
        "console_scripts": [
            "magicgenerator = app.cli:main",
        ]
    },
)
