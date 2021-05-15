import io
import pybitrix24

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=pybitrix24.__name__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='The simplest zero dependency polyversion Python library for Bitrix24 REST API.',
    keywords='bitrix24 rest api client sdk library',
    version=pybitrix24.__version__,
    url='https://github.com/yarbshk/pybitrix24',
    author='Yurii Rabeshko',
    author_email='george.rabeshko@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    python_requires='>=2.7',
    platforms='any'
)
