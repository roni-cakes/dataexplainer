"""Packaging settings for dataexplainer (used to build and upload to PyPI)."""

from pathlib import Path

from setuptools import find_packages, setup

# The README becomes the description shown on the PyPI page.
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="dataexplainer",
    version="0.1.0",  # keep the same as __version__ in dataexplainer/__init__.py
    description="Turn a table of data into a short summary in plain English.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="dataexplainer team",
    url="https://github.com/roni-cakes/dataexplainer",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["pandas"],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)

