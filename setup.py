from distutils.core import setup

with open('README') as f:
    readme = f.read()

setup(
    name='Zinc',
    version='0.1.3',
    author='John Wang',
    author_email='john@zinc.io',
    packages=['zinc'],
    package_dir={'zinc': ''},
    package_data={'zinc': ['examples/*.py', 'examples/*.json']},
    include_package_data=True,
    url='http://pypi.python.org/pypi/Zinc/',
    license='LICENSE.txt',
    description='Wrapper for Zinc ecommerce API (zinc.io)',
    long_description=readme,
    install_requires=[
        "requests >= 1.1.0"
    ],
)
