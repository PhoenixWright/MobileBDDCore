from setuptools import setup, find_packages

args = dict(
    name='MobileBDDCore',
    version='1.0',
    # declare your packages
    packages=find_packages(exclude=("test",))
)

setup(**args)
