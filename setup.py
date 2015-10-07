import sys
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('z9/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

if sys.version_info < (3, 0):
    raise NotImplementedError("Sorry, you need at least Python 3.x to use z9.")

from setuptools import setup, find_packages

setup(
    name='z9',
    version=version,
    packages=find_packages(),
    url='',
    license='',
    author='ayurjev',
    author_email='',
    description=''
    # dependency_links=[
    #     'https://github.com/verteen/envi/tarball/master#egg=envi-0.1',
    #     'https://github.com/verteen/mapex/tarball/master#egg=mapex-0.1',
    #     'https://github.com/verteen/suit/tarball/master#egg=suit-1.1',
    # ]
)
