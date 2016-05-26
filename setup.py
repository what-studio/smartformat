import os

from setuptools import find_packages, setup


# Include __about__.py.
__dir__ = os.path.dirname(__file__)
about = {}
with open(os.path.join(__dir__, 'smartformat', '__about__.py')) as f:
    exec(f.read(), about)


setup(
    name='smartformat',
    version=about['__version__'],
    license=about['__license__'],
    author=about['__author__'],
    maintainer=about['__maintainer__'],
    maintainer_email=about['__maintainer_email__'],
    url='https://github.com/what-studio/smartformat',
    description='Python implementation of SmartFormat.NET',
    platforms='any',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Localization',
        'Topic :: Text Processing :: Linguistic',
    ],
    install_requires=['babel', 'six', 'valuedispatch'],
)
