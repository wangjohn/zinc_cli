from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='Zinc',
    version='0.2.1',
    author='John Wang',
    author_email='john@zinc.io',
    packages=['zinc'],
    package_dir={'zinc': ''},
    package_data={'zinc': ['examples/*.py', 'examples/*.json']},
    include_package_data=True,
    scripts=['bin/zinc_interactive.py','bin/zinc_simple_order.py'],
    url='http://pypi.python.org/pypi/Zinc/',
    license='LICENSE.txt',
    description='Wrapper for Zinc ecommerce API (zinc.io)',
    long_description=readme,
    install_requires=[
        "requests >= 1.1.0"
    ],
)
