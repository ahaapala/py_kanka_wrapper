from setuptools import setup

setup(
   name='py_kanka_wrapper',
   version='0.0.1',
   description='A library to make calling the Kanka.io API easier',
   author='Adam Haapala',
   author_email='adamhaapala@yahoo.com',
   packages=['py_kanka_wrapper'],  #same as name
   install_requires=['requests'], #external packages as dependencies
)
