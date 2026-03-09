from setuptools import setup, find_packages

setup(
    name="gas_market_data_processor",
    version="1.0.0",
    description="Engine for cleaning, resampling, and preparing OHLC data in the GAS ecosystem",
    author="Muhamad RidwanJr",
    author_email="ridwan@gasstrategy.io",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "redis>=5.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.24.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
        ]
    },
    python_requires=">=3.10",
)
