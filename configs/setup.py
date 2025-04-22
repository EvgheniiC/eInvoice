from setuptools import setup, find_packages

# python setup.py sdist
setup(
    name='com.sixt.lib.python.eInvoice',
    version='0.1',
    packages=find_packages(),
    package_data={
        "archive": ["utils/*", "utils/config/*", "utils/templates/*"]
    },
    install_requires=[
        'numpy>=1.18.1',
        'pandas>=1.0.1',
        'python-decouple>=3.8',
        "requests==2.32.0",
        'xmltodict>=0.13.0'
    ],
    description='Einvoice'
)
