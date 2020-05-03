import io

from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pybitrix24',
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='The simplest Bitrix24 REST API client written in Python.',
    keywords='bitrix24 rest api client sdk',
    version='1.0.0',
    url='https://github.com/yarbshk/pybitrix24',
    author='Yurii Rabeshko',
    author_email='yurii.rabeshko@mail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    python_requires='>=2.6',
    platforms='any'
)
