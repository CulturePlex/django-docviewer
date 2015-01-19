# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='django-docviewer',
    version='0.1',
    description='documentcloud for django',
    long_description="",
    author='robertour',
    author_email='robertour@gmail.com',
    url='https://github.com/robertour/django-docviewer',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'django-autoslug==1.7.1',
        'django-model-utils==2.2',
        'celery==3.0.23',
        'django-haystack==2.1.0',
        'django-pipeline==1.3.15',
        'django-celery==3.0.23',
        'celery-haystack==0.7.2',
    ],
    dependency_links = [
        'http://github.com/toastdriven/django-haystack/tarball/master#egg=django-haystack-2.0.0-beta'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
