"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import find_packages, setup


def readme():
    with open("README.md", encoding="utf-8") as f:
        return f.read()


def version():
    with open("version.txt", encoding="utf-8") as f:
        return f.read()


def install_requires():
    # pkg_resources was removed from recent setuptools; requirements.txt only
    # holds plain requirement lines, so strip comments and blanks ourselves.
    with open("requirements.txt", encoding="utf-8") as f:
        lines = [line.split("#", 1)[0].strip() for line in f]
        return [line for line in lines if line]


setup(
    name="lennybot",
    version=version(),
    author="Simon Schneider",
    author_email="dev@raynigon.com",
    description="Automatic Updates for Kustomize Resources",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    keywords="kustomize",
    url="http://github.com/raynigon/lennybot",
    project_urls={
        "Bug Reports": "https://github.com/raynigon/lennybot/issues",
        "Source": "https://github.com/raynigon/lennybot/",
    },
    install_requires=install_requires(),
    extras_require={
        "dev": ["setuptools", "wheel", "black"],
        "test": ["coverage", "pytest"],
    },
    python_requires=">=3.6, <4",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    data_files=[("generic", ["version.txt", "README.md", "requirements.txt"])],
    entry_points={
        "console_scripts": [
            "lennybot=lennybot:main",
        ],
    },
)
