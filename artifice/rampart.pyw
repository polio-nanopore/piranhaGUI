import PySimpleGUI as sg
import os.path
from os import makedirs, mkdir
import sys
import json
import traceback
import time
from datetime import datetime
from shutil import copytree

from artifice_core import consts
from artifice_core.update_log import update_log
import artifice_core.language as language
import advanced_window.main_window
import basic_window.rampart_run_window
import basic_window.rampart_window
import artifice_core.startup_window
import artifice_core.window_functions as window_functions
from artifice_core.manage_protocols import add_protocol
from artifice_core.window_functions import scale_window, scale_image

#create artifice theme
def make_themes():

    consts.THEMES = {
        'DEFAULT': {'BACKGROUND': "#005B67",
                'TEXT': '#f7eacd',
                'INPUT': '#072429',
                'TEXT_INPUT': '#f7eacd',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#d97168'),
                'BUTTON_HOVER': ('#f7eacd', '#F48379'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0},
        'CONTENT': {'BACKGROUND': "#005B67",
                'TEXT': '#f7eacd',
                'INPUT': '#072429',
                'TEXT_INPUT': '#f7eacd',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#d97168'),
                'BUTTON_HOVER': ('#f7eacd', '#F48379'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 2},
        'PANEL': {'BACKGROUND': "#F5F1DF",
                'TEXT': '#1e5b67',
                'INPUT': '#f7eacd',
                'TEXT_INPUT': '#072429',
                'CONSOLE_TEXT': '#FFBF00',
                'CONSOLE_BACKGROUND': '#072429',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#005B67'),
                'BUTTON_HOVER': ('#f7eacd', '#328E9A'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 2},
        'HEADER': {'BACKGROUND': "#005B67",
                'TEXT': '#f7eacd',
                'INPUT': '#072429',
                'TEXT_INPUT': '#f7eacd',
                'SCROLL': '#707070',
                'BUTTON': ('#f7eacd', '#d97168'),
                'BUTTON_HOVER': ('#f7eacd', '#F48379'),
                'PROGRESS': ('#f7eacd', '#d97168'),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}
    }

    for key, value in consts.THEMES.items():
        sg.theme_add_new(key, value)


#make sure a directory exists to save runs
def check_runs_dir(runs_dir):
    filepath = runs_dir / 'archived_runs.json'
    if os.path.isfile(filepath):
        return True
    else:
        archived_dict = {"archived_runs": []}

        if not os.path.isdir(runs_dir):
            makedirs(runs_dir)

        with open(filepath, 'w') as file:
            json.dump(archived_dict, file)

# makes sure builtin protocols are installed
def setup_builtin_protocols():
    config = artifice_core.consts.retrieve_config()
    builtin_path = str(artifice_core.consts.get_datadir() / 'builtin_protocols')
    try:
        copytree('builtin_protocols', builtin_path)
    except:
        pass
    
    try:
        mkdir(config['PROTOCOLS_DIR'])
    except:
        pass

    try:
        add_protocol('ARTIC Poliovirus protocol v1.1', str(artifice_core.consts.get_datadir() / 'builtin_protocols' / 'rampart'), config)
    except:
        pass

    try:
        add_protocol('default RAMPART protocol', str(artifice_core.consts.get_datadir() / 'builtin_protocols' / 'default_protocol'), config)
    except:
        pass

def create_splash_window():
    sg.theme('CONTENT')
    
    main_logo_scaled = scale_image(consts.ICON_FILENAME,scale,(150,150))
    
    layout = [
        [sg.Image(source = main_logo_scaled)],
        [sg.Text(language.translator('Starting up..'), font=consts.TITLE_FONT, justification = 'center')]
        ]
    
    window = sg.Window('RAMPART', layout, resizable=False, enable_close_attempted_event=False, finalize=True,
                       icon=consts.ICON)

    return window

"""
def setup_config():
    # must be set first...
    consts.APPLICATION_NAME = 'RAMPART'
    
    consts.WINDOW_TITLE = "RAMPART"
    consts.ICON_FILENAME = "rampart-icon.png"
    consts.APPLICATION_TITLE_LINE_1 = "Read Assignment, Mapping, and Phylogenetic Analysis in Real Time"
    consts.APPLICATION_TITLE_LINE_2 = ""
    consts.APPLICATION_SUBTITLE_LINE = "built by James Hadfield, Áine O'Toole, Nick Loman and Andrew Rambaut as part of the ARTIC Network proiect"             
    consts.PROJECT_LOGO = "artic_panel.png"
    consts.PROJECT_FOOTER = ""
    consts.ICON = window_functions.scale_image(consts.ICON_FILENAME, consts.SCALING, (64,64))

    consts.setup_config('rampart.yml')
    consts.config = consts.retrieve_config()

    consts.ARCHIVED_RUNS = consts.get_config_value('ARCHIVED_RUNS')
    consts.RUNS_DIR = consts.get_config_value('RUNS_DIR')
    consts.LOGFILE = consts.get_config_value('LOGFILE')
    consts.THREADS = consts.get_config_value('THREADS')
    consts.SCALING = consts.get_config_value('SCALING')

    consts.RAMPART_PORT_1 = consts.get_config_value('RAMPART_PORT_1')
    consts.RAMPART_PORT_2 = consts.get_config_value('RAMPART_PORT_2')
    consts.RAMPART_IMAGE = consts.get_config_value('RAMPART_IMAGE')
    consts.RAMPART_LOGFILE = consts.get_config_value('RAMPART_LOGFILE')
"""

if __name__ == '__main__':

    advanced = False

    startup_time = datetime.today()

    #setup_config()
    check_runs_dir(consts.RUNS_DIR)
    update_log(f'Started {consts.APPLICATION_NAME} at {startup_time}\n', overwrite = True)
    setup_builtin_protocols()

    language.translator = language.setup_translator()

    scale = scale_window()

    make_themes()

    splash_window = create_splash_window()
    splash_closed = False

    # remove 'True or' to only show startup window if docker is not installed / updates needed to pipelines
    show_startup_window = True or artifice_core.startup_window.check_installation_required(usesPiranha = False)

    if show_startup_window:
        window = artifice_core.startup_window.create_startup_window(usesPiranha = False) #create the startup window to check/install docker and images

        splash_window.close()
        splash_closed = True

        advanced = artifice_core.startup_window.run_startup_window(window)

    
    if advanced != None: # if button pressed to launch artifice
        try:
            #while True: # user can go back and forth between editing and executing runs
                #window = basic_window.rampart_run_window.create_edit_window()
                #run_info = basic_window.rampart_run_window.run_edit_window(window)
                #if run_info == None:
                #    break
                #
                #update_log(f'\nrun details confirmed, creating main window\n')
                #window, rampart_running = basic_window.rampart_window.create_main_window()
                #edit = basic_window.rampart_window.run_main_window(window, run_info, rampart_running=rampart_running)
                #if edit != True:
                #    break
                
            window, rampart_running = basic_window.rampart_window.create_main_window()

            if not splash_closed:
                splash_window.close()
                splash_closed = True

            edit = basic_window.rampart_window.run_main_window(window, rampart_running=rampart_running)

            exit_time = datetime.today()
            update_log(f'\nExited successfully at {exit_time}\n')


        except Exception as err:
            exit_time = datetime.today()
            update_log(traceback.format_exc())
            update_log(f'\nExited unexpectedly at {exit_time}\n')
            print(traceback.format_exc(), file=sys.stderr)
        else:
            window.close()


    else:
        exit_time = datetime.today()
        update_log(f'\nExited successfully at {exit_time}\n')
