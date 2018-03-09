"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

setup(
    name='django-nested-forms',
    description='A util to make Django formsets easy to use.',
    packages=find_packages(include=['nested_forms']),
    install_requires=['django >= 1.5, <2'],
    use_scm_version = True,
    setup_requires=['setuptools_scm'],
    test_suite='run_tests.py',
)
