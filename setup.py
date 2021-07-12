#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import find_packages, setup

with open("README.md") as readme_file:
    readme = readme_file.read()

setup_requirements = [
    "pytest-runner>=5.2",
]

test_requirements = [
    "black>=19.10b0",
    "codecov>=2.1.4",
    "docutils>=0.10,<0.16",
    "flake8>=3.8.3",
    "flake8-debugger>=3.2.1",
    "isort>=5.7.0",
    "mypy>=0.800",
    "psutil>=5.7.0",
    "pytest>=5.4.3",
    "pytest-cov>=2.9.0",
    "pytest-raises>=0.11",
    "quilt3~=3.4.0",
]

dev_requirements = [
    *setup_requirements,
    *test_requirements,
    "bump2version>=1.0.1",
    "coverage>=5.1",
    "ipython>=7.15.0",
    "pytest-runner>=5.2",
    "tox>=3.15.2",
    "twine>=3.1.1",
    "wheel>=0.34.2",
]

requirements = [
    "aicsimageio[all]~=4.0.2",
    "fsspec[http]",  # no version pin, we pull from aicsimageio
    "napari~=0.4.10",
    "napari_plugin_engine~=0.1.4",
]

extra_requirements = {
    "setup": setup_requirements,
    "test": test_requirements,
    "dev": dev_requirements,
}

setup(
    author="Jackson Maxfield Brown",
    author_email="jmaxfieldbrown@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Framework :: napari",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    description=(
        "AICSImageIO for napari. "
        "Multiple file format reading directly into napari using pure Python."
    ),
    entry_points={
        "napari.plugin": [
            "aicsimageio-out-of-memory = napari_aicsimageio.out_of_memory",
            "aicsimageio-in-memory = napari_aicsimageio.in_memory",
        ],
    },
    install_requires=requirements,
    license="BSD-3-Clause",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    keywords="napari, aicsimageio, TIFF, CZI, LIF, imageio, image reading, metadata",
    name="napari-aicsimageio",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.8",
    setup_requires=setup_requirements,
    test_suite="napari_aicsimageio/tests",
    tests_require=test_requirements,
    extras_require=extra_requirements,
    url="https://github.com/AllenCellModeling/napari-aicsimageio",
    project_urls={
        "Source Code": "https://github.com/AllenCellModeling/napari-aicsimageio",
        "Bug Tracker": "https://github.com/AllenCellModeling/napari-aicsimageio/issues",
        "Documentation": "https://github.com/AllenCellModeling/napari-aicsimageio#README.md",
        "User Support": "https://github.com/AllenCellModeling/napari-aicsimageio/issues",
    },
    # Do not edit this string manually, always use bumpversion
    # Details in CONTRIBUTING.rst
    version="0.3.4",
    zip_safe=False,
)
