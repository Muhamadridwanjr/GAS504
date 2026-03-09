from setuptools import setup, find_packages

setup(
    name="gas_strategy_core",
    version="1.0.0",
    description="Engine Layer Library for GAS Ecosystem",
    author="Muhamad RidwanJr / GAS Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "PyYAML>=6.0",
        "pydantic>=2.0.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.11",
)
