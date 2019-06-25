from setuptools import setup

setup(
   name='py_kanka_wrapper',
   version='0.0.2',
   description='A library to make calling the Kanka.io API easier',
   author='Adam Haapala',
   author_email='adamhaapala@yahoo.com',
   packages=['py_kanka_wrapper'],  # Same as name
   install_requires=['requests'],  # External packages as dependencies
)
