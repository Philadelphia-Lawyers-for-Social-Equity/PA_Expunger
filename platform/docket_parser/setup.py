from setuptools import setup

setup(
    name='docket_parser',
    version='0.1.0',
    packages=['docket_parser'],
    entry_points={
        'console_scripts': [
        'docket_parser = docket_parser.__main__:main'
        ]
    },
)

