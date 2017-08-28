#!/usr/bin/env python3

import setuptools

# Read version from version.py into __version__
with open('insta/version.py') as fp:
    exec(fp.read())

setuptools.setup(
    name='instatools',
    version=__version__,
    description='Instagram scraping tools',
    url='https://github.com/zmwangx/instatools',
    author='Zhiming Wang',
    author_email='zmwangx@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Multimedia',
        'Topic :: Utilities',
    ],
    packages=['insta'],
    python_requires='>=3.6',
    install_requires=['feedgen', 'requests'],
    extras_require={
        'dev': ['flake8'],
    },
    entry_points={'console_scripts': [
        'instaconfig=insta.config:main',
        'instafeed=insta.feed:main',
    ]},
)
