from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    install_requires = f.read().split('\n')

setup(
    name='webspot',
    version='0.1.0',
    packages=find_packages(where='webspot_package'),
    url='https://github.com/tikazyq/webspot',
    license='BSD-3-Clause',
    author='tikazyq',
    author_email='tikazyq@163.com',
    description='A smart web content identification tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    scripts=[],
    package_data={'': ['webspot_package']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'crawlab-cli=crawlab.cli.main:main'
        ]
    }
)
