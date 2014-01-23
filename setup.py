from distutils.core import setup

setup(
    name='Zinc',
    version='0.1.2',
    author='John Wang',
    author_email='john@zinc.io',
    packages=['zinc_request_processor'],
    scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/Zinc/',
    license='LICENSE.txt',
    description='Wrapper for Zinc ecommerce API (zinc.io)',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 1.1.0"
    ],
)
