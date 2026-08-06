from setuptools import find_packages, setup

setup(
    name="einvoice",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "app": [
            "helper_functions/config/*",
        ],
    },
    include_package_data=True,
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.32.0",
        "python-multipart>=0.0.12",
        "pydantic-settings>=2.6.0",
        "requests>=2.31.0",
        "jsonpath-ng>=1.7.0",
        "xmltodict>=0.13.0",
        "PyPDF2>=3.0.0",
        "openpyxl>=3.1.0",
    ],
    description="eInvoice receiver API — XRechnung / ZUGFeRD parse & validate",
)
