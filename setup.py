from setuptools import setup
import os

README = os.path.join(os.path.dirname(__file__), 'README.txt')
long_description = open(README).read() + 'nn'

setup(
    name='Zinc',
    version='0.1.3',
    author='John Wang',
    author_email='john@zinc.io',
    packages=['zinc'],
    url='https://github.com/wangjohn/zinc_cli',
    scripts=[],
    license='LICENSE.txt',
    description='Wrapper for Zinc ecommerce API (zinc.io)',
    long_description=long_description,
    install_requires=[
        "requests >= 1.1.0"
    ],
)
