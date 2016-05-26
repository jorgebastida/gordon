import sys

from setuptools import setup, find_packages

install_requires = [
    'boto3>=1.2.3',
    'clint',
    'PyYAML>=3',
    'troposphere>=1.3',
    'Jinja2',
    'six'
]

tests_require = [
    'coverage'
]

# as of Python >= 2.7 argparse module is maintained within Python.
if sys.version_info < (2, 7):
    install_requires.append('argparse>=1.1.0')

# as of Python >= 3.3 unittest.mock module is maintained within Python.
if sys.version_info < (3, 3):
    tests_require.append('pbr>=0.11,<1.7.0')
    tests_require.append('mock>=1.0.0')
    tests_require.append('nose')
    tests_require.append('cfn-response')

setup(
    name='gordon',
    version='0.0.1',
    url='http://github.com/jorgebastida/gordon',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='Gordon is a high-level framework to create, wire and deploy AWS Lambdas in an easy way.',
    keywords="aws lambda api gateway",
    packages=find_packages(),
    platforms='any',
    install_requires=install_requires,
    test_suite='nose.collector',
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
            'gordon = gordon.bin:main',
        ]
    },
    zip_safe=False
)
