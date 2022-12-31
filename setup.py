#!/usr/bin/env python3

"""A download & media library management tool for HelixStudios"""

import pathlib

__version__ = '0.0.2'

from pip._internal.req import parse_requirements
from setuptools import setup, find_packages


MY_DIR = pathlib.Path(__file__).parent.resolve()

# parse the requirements.txt file, generating a list of all
# packages needed for this tool
REQUIREMENTS = list([str(ir.requirement) for ir in
                     parse_requirements('requirements.txt', session=False)])

# Get the long description from the README file
long_description = (MY_DIR / 'README.md').read_text(encoding='utf-8')


setup(
    name='helixstudios',
    version=__version__,
    description=__doc__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.helixstudios.com/',

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords=['helixstudios'],

    package_dir={'': 'src'},

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(where='src'),
    python_requires='>=3.7, <4',

    # install_requires specifies a list of packages that will be installed
    # so that tdmYES can run correctly.
    install_requires=REQUIREMENTS,

    # executable script entry points
    entry_points={  # Optional
        'console_scripts': [
            'helixstudios=helixstudios:main',
        ],
    },
)
