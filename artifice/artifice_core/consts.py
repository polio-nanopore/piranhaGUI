import PySimpleGUI as sg
from yaml import safe_load, safe_dump
from pathlib import Path
import pathlib
import sys
import csv
import shutil
import os.path

from os import getenv, cpu_count, mkdir, remove



#returns directory where Artifice stores data, dependent on os
def get_datadir():
    home = pathlib.Path.home()

    if sys.platform.startswith("win"): #windows
        os_path = getenv("LOCALAPPDATA")
    elif sys.platform.startswith("darwin"): #macOS
        os_path = "~/Library/Application Support"
    else: #linux
        os_path = getenv("XDG_DATA_HOME", "~/.local/share")

    path = Path(os_path) /  'piranhaGUI'#"RAMPART"

    path = path.expanduser()

    if not os.path.isdir(path): #creates data directory if it doesn't exist
        mkdir(path)

    return path

#def setup_config():
    # must be set first...
    APPLICATION_NAME = 'RAMPART'
    
    APPLICATION_NAME = "RAMPART"
    WINDOW_TITLE = "RAMPART"
    ICON_FILENAME = "rampart-icon.png"
    APPLICATION_TITLE_LINE_1 = "Read Assignment, Mapping, and Phylogenetic Analysis in Real Time"
    APPLICATION_TITLE_LINE_2 = "built by James Hadfield, Nick Loman and Andrew Rambaut as part of the ARTIC Network proiect"             
    PROJECT_LOGO = "artic_panel.png"
    PROJECT_FOOTER = ""
    ICON = window_functions.scale_image(ICON_FILENAME, SCALING, (64,64))

    setup_config('rampart.yml')
    config = retrieve_config()

    ARCHIVED_RUNS = get_config_value('ARCHIVED_RUNS')
    RUNS_DIR = get_config_value('RUNS_DIR')
    LOGFILE = get_config_value('LOGFILE')
    THREADS = get_config_value('THREADS')
    SCALING = get_config_value('SCALING')

    RAMPART_PORT_1 = get_config_value('RAMPART_PORT_1')
    RAMPART_PORT_2 = get_config_value('RAMPART_PORT_2')
    RAMPART_IMAGE = get_config_value('RAMPART_IMAGE')
    RAMPART_LOGFILE = get_config_value('RAMPART_LOGFILE')

# checks config file exists, if not creates the config file
def setup_config(default_config_file='config.yml'):
    config_path = str(get_datadir() / 'config.yml')
    if os.path.isfile(config_path):
        return True
    else:
        shutil.copyfile(get_resource(f'./{default_config_file}'), config_path)

# reset config to defaults
def set_config_to_default(default_config_file='config.yml'):
    config_path = str(get_datadir() / 'config.yml')
    if os.path.isfile(config_path):
        remove(config_path)
    shutil.copyfile(get_resource(f'./{default_config_file}'), config_path)

def get_config_value(key, config):
    try:
        value = config[key]
    except:
        with open(get_resource('./config.yml')) as file:
            default_config = safe_load(file)
            value = default_config[key]
            edit_config(key, value)
    
    return value
                  
# returns a dict with config value taken from the config file
def retrieve_config():
    config_path = str(get_datadir() / 'config.yml')
    with open(config_path) as file:
        config = safe_load(file)

    config['RUNS_DIR'] = get_datadir() / 'runs'
    config['PROTOCOLS_DIR'] = get_datadir() / 'protocols'

    THREADS = config['THREADS'] #how many threads pipelines should use
    if THREADS == None:
        THREADS = max(int(cpu_count()/2),1)
        if THREADS == None:
            THREADS = 1

    config['THREADS'] = THREADS

    if 'LANGUAGE' not in config:
        config['LANGUAGE'] = 'English'

    if 'PROTOCOL' not in config:
        config['PROTOCOL'] = 'Select RAMPART protocol'
    
    return config

# edits the value of one config value
def edit_config(key, value):
    config_path = str(get_datadir() / 'config.yml')
    with open(config_path) as file:
        config = safe_load(file)

    config[key] = value

    with open(config_path, 'w') as file:
        safe_dump(config, file)
          
def get_theme(key = None):
    if key == None:
        key = sg.theme()

    if THEMES[key] != None:
        return THEMES[key]
    else:
        return THEMES['DEFAULT']

# This function converts relative paths to absolute paths, fixes issues for packaged application. 
# Should be used to access any file not saved in the application data directory
def get_resource(filepath):
    filepath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), filepath))
    return filepath

#VERSION = get_config_value('VERSION', retrieve_config())

#APPLICATION_NAME = 'ARTIFICE'
#WINDOW_TITLE = 'ARTIFICE'
#ICON_FILENAME = 'artic.png'
#ICON = None

#APPLICATION_TITLE_LINE_1 = ""
#APPLICATION_TITLE_LINE_2 = ""             
#PROJECT_LOGO = "artic_logo.png"
#PROJECT_FOOTER = ""

#   NOTE THIS SHOULD BE UPDATED WITH EACH NEW MAJOR PACKAGE RELEASE (assuming it's compatible with the latest artifice version)
COMPATIBLE_VERSIONS = {
    'polionanopore/piranha':1.6
    }

APPLICATION_HEADER = 'Powered by ARTIFICE | ARTICnetwork: http://artic.network'
APPLICATION_CREDITS = 'ARTIFICE developed by Corey Ansley, Áine O\'Toole, Rachel Colquhoun, Zoe Vance & Andrew Rambaut'
APPLICATION_FOOTER='ARTIC-network supported by the Wellcome Trust Award 206298/Z/17/Z'

# styling constants
BUTTON_SIZE = (128,32)
BUTTON_FONT_FAMILY = 'Helvetica Neue Light'
BUTTON_FONT_SIZE = 14
BUTTON_FONT = (BUTTON_FONT_FAMILY, BUTTON_FONT_SIZE)

DEFAULT_FONT_FAMILY = 'Helvetica Neue Light'
DEFAULT_FONT_SIZE = 16
DEFAULT_FONT = (DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
if sys.platform.startswith("darwin"): #macOS
    MONOTYPE_FONT_FAMILY = 'Menlo'
else:
    MONOTYPE_FONT_FAMILY = 'Consolas'
CONSOLE_FONT_SIZE = 14
CONSOLE_FONT = (MONOTYPE_FONT_FAMILY, CONSOLE_FONT_SIZE)

HEADER_TITLE_FONT = ('Helvetica Neue Thin', 24)
HEADER_FONT = (DEFAULT_FONT_FAMILY, 14)
FOOTER_FONT = (DEFAULT_FONT_FAMILY, 14)

TITLE_FONT = ('Helvetica Neue Thin', 24)
SUBTITLE_FONT = (DEFAULT_FONT_FAMILY, 18)
CAPTION_FONT = (DEFAULT_FONT_FAMILY, 14)

# URLS
ARTIC_URL = 'https://artic.network/'
POSECO_URL = 'http://polionanopore.org'
PIRANHA_URL = 'https://github.com/polio-nanopore/piranha/'

RAMPART_VERSION = None
PIRANHA_VERSION = None
PIRANHA_GUI_VERSION = '1.6.11'

config = None
#LOGFILE = None
#RUNS_DIR = None
#ARCHIVED_RUNS = None
#SCALING = 1
#THREADS = 1
THEMES = { }

APPLICATION_NAME = 'RAMPART'
    
APPLICATION_NAME = "RAMPART"
WINDOW_TITLE = "RAMPART"
ICON_FILENAME = "rampart-icon.png"
APPLICATION_TITLE_LINE_1 = "Read Assignment, Mapping, and Phylogenetic Analysis in Real Time"
APPLICATION_TITLE_LINE_2 = "built by James Hadfield, Nick Loman and Andrew Rambaut as part of the ARTIC Network proiect"             
APPLICATION_SUBTITLE_LINE = '' #None
PROJECT_LOGO = "artic_panel.png"
PROJECT_FOOTER = ""
ICON = ICON_FILENAME #window_functions.scale_image(ICON_FILENAME, SCALING, (64,64))

setup_config() #setup_config('rampart.yml')
config = retrieve_config()

ARCHIVED_RUNS = get_config_value('ARCHIVED_RUNS',config)
RUNS_DIR = get_config_value('RUNS_DIR',config)
LOGFILE = get_config_value('LOGFILE',config)
THREADS = get_config_value('THREADS',config)
SCALING = get_config_value('SCALING',config)
PHYLO_ENABLED = get_config_value('PHYLO_ENABLED', config)
PHYLO_DIR = get_config_value('PHYLO_DIR', config)

RAMPART_PORT_1 = get_config_value('RAMPART_PORT_1',config)
RAMPART_PORT_2 = get_config_value('RAMPART_PORT_2',config)
RAMPART_IMAGE = get_config_value('RAMPART_IMAGE',config)
RAMPART_LOGFILE = get_config_value('RAMPART_LOGFILE',config)

if __name__ == '__main__':
    #home = pathlib.Path.home()
    print(RUNS_DIR)
