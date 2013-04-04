import re, sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


version = re.search("__version__ = '([^']+)'",
                    open('bitpay/__init__.py').read()).group(1)


setup(
    name='python-bitpay',
    version=version,
    author='Jonathan Enzinna',
    author_email='jonnyfunfun@gmail.com',
    maintainer='Jonathan Enzinna',
    maintainer_email='jonnyfunfun@gmail.com',
    url='https://github.com/JonnyFunFun/python-bitpay',
    description='BitPay API wrapper for Python',
    long_description=open('README.rst').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Office/Business :: Financial',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Utilities'],
    license='GPLv3',
    dependency_links=['simplejson'],
    keywords=['bitcoin','btc','bitpay'],
    packages=['bitpay'],
    package_data={'': ['COPYING'], 'bitpay': ['*.cfg']},
    zip_safe=False
)