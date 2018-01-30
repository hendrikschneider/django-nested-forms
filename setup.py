"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

setup(
    name='django-nested-forms',
    version='0.1.0',
    description='A util to make Django formsets easy to use.',
    packages=find_packages(include=['nested_forms']),
    install_requires=['django >= 1.5, <2'],
    test_suite='run_tests.py',
)
