import sys

from setuptools import setup, find_packages

install_requires = [
    'boto3>=1.2.3,<2.0',
    'clint>0.5,<1.0',
    'PyYAML>=3,<4.0',
    'troposphere>=1.6,<2.0',
    'Jinja2>=2.8,<3.0',
    'six>1.9,<2.0'
]

# as of Python >= 2.7 argparse module is maintained within Python.
if sys.version_info < (2, 7):
    install_requires.append('argparse>=1.1.0')


setup(
    name='gordon',
    version='0.5.0',
    url='http://github.com/jorgebastida/gordon',
    license='BSD',
    author='Jorge Bastida',
    author_email='me@jorgebastida.com',
    description='Gordon is a tool to create, wire and deploy AWS Lambdas using CloudFormation',
    keywords="aws lambda apigateway kinesis dynamodb s3 cloudwatch",
    packages=find_packages(),
    platforms='any',
    install_requires=install_requires,
    test_suite='nose.collector',
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
    include_package_data=True,
    zip_safe=False,
    use_2to3=True
)
