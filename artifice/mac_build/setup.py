"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['../artifice.pyw']
DATA_FILES = []
OPTIONS = {"qt_plugins": ["libffi", "dyld"], "resources": ["../resources", "../config.yml", "../docker_rampart", "../docker_piranha", "../Keyboard.ttf"], "frameworks": ["/usr/lib/libffi.dylib"]}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
