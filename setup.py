import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--cov=arrested', '--cov-report=term-missing', '-s', '--tb=short']
        self.test_suite = True

    def run_tests(self):
        # import here. outside, the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='userlist',
    version='1.0.0',
    author='Mikey Waites',
    author_email='mikey.waites@gmail.com',
    description='A python Rest API framework for flask',
    long_description='flask arrested RESTFul api framework',
    packages=find_packages(
        exclude=["tests"]
    ),
    include_package_data=True,
    zip_safe=False,
    tests_require=[
        'ipdb==0.10.0',
        'pytest==2.9.2',
        'pytest-cov==2.2.1',
        'Flask-SQLAlchemy==2.1',
        'flask-oauthlib==0.9.3',
    ],
    cmdclass={
        'test': PyTest
    },
    extras_require={
        'develop': [
            'sphinx==1.4.4',
        ]
    },
    entry_points={},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content']
    )
