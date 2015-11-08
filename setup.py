import sys

from setuptools import setup, find_packages

install_requires = [
    'boto3>=1.2.1',
    'termcolor>=1.1.0',
    'PyYAML>=3',
    'troposphere>=1.3',
    'Jinja2',
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
    name='piranha',
    version='0.0.1',
    url='http://github.com/jorgebastida/piranha',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='piranha is a simple framework for creating server-less applications using AWS services',
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
            'piranha = piranha.bin:main',
        ]
    },
    zip_safe=False
)
