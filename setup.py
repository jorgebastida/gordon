import sys

from setuptools import setup, find_packages

install_requires = [
    'jmespath==0.7.1',
    'botocore<=1.2.3',
    'boto3>1.0.0',
    'termcolor>=1.1.0',
]

tests_require = []

# as of Python >= 2.7 argparse module is maintained within Python.
if sys.version_info < (2, 7):
    install_requires.append('argparse>=1.1.0')

# as of Python >= 3.3 unittest.mock module is maintained within Python.
if sys.version_info < (3, 3):
    tests_require.append('pbr>=0.11,<1.7.0')
    tests_require.append('mock>=1.0.0')

setup(
    name='yeast',
    version='0.0.1',
    url='http://github.com/jorgebastida/yeast',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='yeast is a simple framework for creating server-less applications using AWS services',
    keywords="aws lambda api gateway",
    packages=find_packages(),
    platforms='any',
    install_requires=install_requires,
    test_suite='tests',
    tests_require=tests_require,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ],
    entry_points={
        'console_scripts': [
            'yeast = yeast.bin:main',
        ]
    },
    zip_safe=False
)
