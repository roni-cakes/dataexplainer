from setuptools import setup, find_packages

setup(
    name="dataexplainer",
    version="0.1.0",
    description="Turn a table of data into a short summary in plain English.",
    packages=find_packages(),
    install_requires=["pandas"],
    python_requires=">=3.8",
)
