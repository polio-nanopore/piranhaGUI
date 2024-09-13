"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['../artifice.pyw']
DATA_FILES = []
#OPTIONS = {"qt_plugins": ["dyld"], "resources": ["../resources", "../config.yml", "../docker_rampart", "../docker_piranha","../builtin_protocols"], "frameworks": ["/usr/lib/libffi.dylib"]} #, "../Keyboard.ttf"
#OPTIONS = {"qt_plugins": ["libffi", "dyld"], "resources": ["../resources", "../config.yml", "../docker_rampart", "../docker_piranha","../builtin_protocols"], 'iconfile':'../resources/piranha_resized.icns', "frameworks": ["/Users/corey/miniconda3/lib/libffi.7.dylib"]} # ["/usr/lib/libffi.7.dylib"]} #, "../Keyboard.ttf"
OPTIONS = {"qt_plugins": ["libffi", "dyld"], "resources": ["../resources", "../config.yml", "../docker_rampart", "../docker_piranha","../builtin_protocols"], 'iconfile':'../resources/piranha_resized.icns', "frameworks": ["/usr/lib/libffi.dylib"]} #, "../Keyboard.ttf"



setup(
    name="PiranhaGUI",
    version="1.5.0",
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)