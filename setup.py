from setuptools import setup, find_packages

with open("README.md") as file:
    description = file.read()

setup(
    name='dynamodbfaker',
    version='1.0.2',
    description='A Python package to generate and insert fake data for AWS Dynamodb',
    long_description = description,
    long_description_content_type = "text/markdown",
    author='Necati Arslan',
    author_email='necatia@gmail.com',
    packages=find_packages(),
    install_requires=[
        'faker',
        'pyyaml',
        'boto3'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries',
    ],
    project_urls={
        "Documentation": "https://github.com/necatiarslan/dynamodb-faker/blob/main/README.md",
        "Source": "https://github.com/necatiarslan/dynamodb-faker",
    },
    entry_points={
        'console_scripts': [
            'dynamodbfaker = dynamodbfaker.cli:main',
        ],
    },
)