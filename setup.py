from setuptools import setup, find_packages

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bitrix24-python3-client',
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='A tiny Python3 client to make requests of Bitrix24 API.',
    keywords='bitrix24 api rest python3 client',
    version='0.4.0',
    url='https://github.com/yarbshk/bitrix24-python3-client',
    author='Yuriy Rabeshko',
    author_email='george.rabeshko@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    packages=find_packages(),
    install_requires=[
        'requests>=2.18.0'
    ],
    python_requires='>=3',
    platforms='any'
)
