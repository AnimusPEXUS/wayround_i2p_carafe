#!/usr/bin/python3

from setuptools import setup

setup(
    name='wayround_i2p_carafe',
    version='0.5',
    description='micro web-framefork for wsgi',
    author='Alexey Gorshkov',
    author_email='animus@wayround.org',
    url='https://github.com/AnimusPEXUS/wayround_i2p_carafe',
    install_requires=[
        'wayround_i2p_utils',
        'wayround_i2p_http',
        'wayround_i2p_wsgi', # TODO: prabably this is not really required anymore
        ],
    packages=[
        'wayround_i2p.carafe'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)'
        ]
    )
