from setuptools import find_packages
from setuptools import setup

setup(
    name='tenki-no-ko',
    description='tenki.jp scraper modules',
    author='Gary Sentosa',
    author_email='gary.sentosa@gmail.com',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
 )
