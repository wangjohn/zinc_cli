from distutils.core import setup

setup(
    name='Zinc',
    version='0.1.5',
    author='John Wang',
    author_email='john@zinc.io',
    packages=['zinc'],
    package_dir={'zinc': ''},
    package_data={'zinc': ['examples/*.py', 'examples/*.json', 'README']},
    include_package_data=True,
    url='https://github.com/wangjohn/zinc_cli',
    license='LICENSE.txt',
    description='Wrapper for Zinc ecommerce API (zinc.io)',
    install_requires=[
        "requests >= 1.1.0"
    ],
)
