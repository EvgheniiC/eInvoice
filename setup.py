from setuptools import setup, find_packages

# python setup.py sdist
setup(
    name='com.sixt.lib.python.eInvoice',
    version='0.1',
    packages=find_packages(),
    package_data={
        "scr": ["invoice_handler/*"]
    },
    install_requires=[
        'requests>=2.31.0' # Add any additional dependencies here
    ],
    description='General Einvoice handler'
)
