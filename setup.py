#!/usr/bin/python3

from setuptools import setup

setup(
    name='wayround_org_carafe',
    version='0.4',
    description='micro web-framefork for wsgi',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_org_carafe',
    install_requires=[
        'wayround_org_utils',
        'wayround_org_http',
        'wayround_org_wsgi', # TODO: prabably this is not really required anymore
        ],
    packages=[
        'wayround_org.carafe'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        ]
    )
