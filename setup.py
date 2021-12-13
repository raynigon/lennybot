"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()


def version():
    with open('version.txt') as f:
        return f.read()


setup(
    name='lennybot',
    version=version(),
    author='Simon Schneider',
    author_email='dev@raynigon.com',
    description='Automatic Updates for Kustomize Resources',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    keywords='kustomize',
    url='http://github.com/raynigon/lennybot',
    project_urls={
        'Bug Reports': 'https://github.com/raynigon/lennybot/issues',
        'Source': 'https://github.com/raynigon/lennybot/',
    },
    install_requires=[
        'requests',
        'pyyaml'
    ],
    extras_require={
        'dev': ['setuptools', 'wheel'],
        'test': ['coverage'],
    },
    python_requires='>=3.6, <4',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),    
)