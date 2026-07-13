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
import basic_window.edit_run_window
import basic_window.execute_run_window
import basic_window.about_window
import artifice_core.startup_window
import artifice_core.window_functions as window_functions
from artifice_core.manage_protocols import add_protocol
from artifice_core.window_functions import scale_window, scale_image
from artifice_core.start_rampart import check_container, check_rampart_running, check_for_docker
from artifice_core.alt_popup import alt_popup_yes_no
from artifice_core.manage_runs import load_run

# colour_vars
CREAM = '#f7eacd'
DARK_BLUE = '#1e5b67'
NEAR_BLACK = '#072429'
GREY= '#707070'
RED = '#d97168'
LIGHTER_RED = '#F48379'
LIGHTER_BLUE = '#328E9A'
YELLOW = '#FFBF00'

#create artifice theme
def make_themes():

    consts.THEMES = {
        'DEFAULT': {'BACKGROUND':DARK_BLUE,
                'TEXT': CREAM,
                'INPUT': NEAR_BLACK,
                'TEXT_INPUT': CREAM,
                'SCROLL': GREY,
                'BUTTON': (CREAM, RED),
                'BUTTON_HOVER': (CREAM, LIGHTER_RED),
                'PROGRESS': (CREAM, RED),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0},
        'CONTENT': {'BACKGROUND': CREAM,
                'TEXT': DARK_BLUE,
                'INPUT': NEAR_BLACK,
                'TEXT_INPUT': CREAM,
                'SCROLL': GREY,
                'BUTTON': (CREAM, DARK_BLUE),
                'BUTTON_HOVER': (CREAM, LIGHTER_BLUE),
                'PROGRESS': (CREAM, RED),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 2},
        'PANEL': {'BACKGROUND': CREAM,
                'TEXT': DARK_BLUE,
                'INPUT': NEAR_BLACK,
                'TEXT_INPUT': CREAM,
                'CONSOLE_TEXT': YELLOW,
                'CONSOLE_BACKGROUND': NEAR_BLACK,
                'SCROLL': GREY,
                'BUTTON': (CREAM, DARK_BLUE),
                'BUTTON_HOVER': (CREAM, LIGHTER_BLUE),
                'PROGRESS': (CREAM, RED),
                'BORDER': 0,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 2},
        'HEADER': {'BACKGROUND':DARK_BLUE,
                'TEXT': CREAM,
                'INPUT': NEAR_BLACK,
                'TEXT_INPUT': CREAM,
                'SCROLL': GREY,
                'BUTTON': (CREAM, RED),
                'BUTTON_HOVER': (CREAM, LIGHTER_RED),
                'PROGRESS': (CREAM, RED),
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
    
    window = sg.Window('PiranhaGUI', layout, resizable=False, enable_close_attempted_event=False, finalize=True,
                       icon=consts.ICON)

    return window

def setup_config():
    # must be set first...
    consts.APPLICATION_NAME = 'PiranhaGUI'

    consts.WINDOW_TITLE = "Piranha-GUI"
    consts.ICON_FILENAME = "piranha-icon.png"
    consts.APPLICATION_TITLE_LINE_1 = "Polio Direct Detection by Nanopore Sequencing (DDNS)"
    consts.APPLICATION_TITLE_LINE_2 = "analysis pipeline and reporting tool"             
    consts.PROJECT_LOGO = "poseqco_logo_cropped.png"
    consts.PROJECT_FOOTER = "Bill & Melinda Gates Foundation OPP1171890 and OPP1207299"
    consts.ICON = window_functions.scale_image(consts.ICON_FILENAME, consts.SCALING, (64,64))

    consts.setup_config()
    consts.config = consts.retrieve_config()
    config = consts.config

    consts.RAMPART_PORT_1 = consts.get_config_value('RAMPART_PORT_1', config)
    consts.RAMPART_PORT_2 = consts.get_config_value('RAMPART_PORT_2', config)
    consts.ARCHIVED_RUNS = consts.get_config_value('ARCHIVED_RUNS', config)
    consts.RUNS_DIR = consts.get_config_value('RUNS_DIR', config)
    consts.RAMPART_IMAGE = consts.get_config_value('RAMPART_IMAGE', config)
    consts.RAMPART_LOGFILE = consts.get_config_value('RAMPART_LOGFILE', config)
    consts.SHOW_RAMPART = consts.get_config_value('SHOW_RAMPART', config)
    consts.PIRANHA_IMAGE = consts.get_config_value('PIRANHA_IMAGE', config)
    consts.PIRANHA_LOGFILE = consts.get_config_value('PIRANHA_LOGFILE', config)
    consts.LOGFILE = consts.get_config_value('LOGFILE', config)
    consts.THREADS = consts.get_config_value('THREADS', config)
    consts.SCALING = consts.get_config_value('SCALING', config)

    # piranhna options
    consts.VALUE_POSITIVE =  consts.get_config_value('VALUE_POSITIVE', config)
    consts.VALUE_NEGATIVE = consts.get_config_value('VALUE_NEGATIVE', config)
    consts.VALUE_SAMPLE_TYPE = consts.get_config_value('VALUE_SAMPLE_TYPE', config)
    consts.VALUE_ORIENTATION = consts.get_config_value('VALUE_ORIENTATION', config)
    consts.VALUE_MIN_MAP_QUALITY = consts.get_config_value('VALUE_MIN_MAP_QUALITY', config)
    consts.VALUE_MIN_READ_LENGTH = consts.get_config_value('VALUE_MIN_READ_LENGTH', config)
    consts.VALUE_MAX_READ_LENGTH = consts.get_config_value('VALUE_MAX_READ_LENGTH', config)
    consts.VALUE_MIN_READS = consts.get_config_value('VALUE_MIN_READS', config)
    consts.VALUE_MIN_PCENT = consts.get_config_value('VALUE_MIN_PCENT', config)
    consts.VALUE_PRIMER_LENGTH = consts.get_config_value('VALUE_PRIMER_LENGTH', config)
    consts.VALUE_OUTPUT_PREFIX = consts.get_config_value('VALUE_OUTPUT_PREFIX', config)
    consts.VALUE_ANALYSIS_MODE = consts.get_config_value('VALUE_ANALYSIS_MODE', config)
    consts.VALUE_DEFAULT_MEDAKA_MODEL = consts.get_config_value('VALUE_DEFAULT_MEDAKA_MODEL', config)



if __name__ == '__main__':
    advanced = False
    startup_time = datetime.today()

    setup_config()
    check_runs_dir(consts.RUNS_DIR)
    update_log(f'Started {consts.APPLICATION_NAME} v{consts.PIRANHA_GUI_VERSION} at {startup_time}\n', overwrite = True)
    setup_builtin_protocols()

    language.translator = language.setup_translator()

    scale = scale_window()

    make_themes()

    splash_window = create_splash_window()
    docker_running = check_for_docker(popup=False)
    if docker_running:
        piranha_running = check_container('piranha')
        rampart_running = check_rampart_running()
    else:
        piranha_running = False
        rampart_running = False

    if piranha_running or rampart_running:
        if piranha_running:
            software = 'Piranha'
        else:
            software = 'Rampart'

        skip_to_execute_window = alt_popup_yes_no(f'{software} software running, continue that run immediately?')
        if skip_to_execute_window == 'Yes':
            skip_to_execute_window = True
        else:
            skip_to_execute_window = False
    else:
        skip_to_execute_window = False
    
    if not skip_to_execute_window:
        window = artifice_core.startup_window.create_startup_window() #create the startup window to check/install docker and images

    splash_window.close()

    if not skip_to_execute_window:
        advanced = artifice_core.startup_window.run_startup_window(window)
    
    if advanced != None: # if button pressed to launch artifice
        try:
            if advanced:
                window, rampart_running = advanced_window.main_window.create_main_window()
                advanced_window.main_window.run_main_window(window, rampart_running=rampart_running)
            else:
                run_info = {'title': 'TEMP_RUN'}
                selected_run_title = 'TEMP_RUN'
                reset_run = True
                while True: # user can go back and forth between editing and executing runs
                    if not skip_to_execute_window:
                        window = basic_window.edit_run_window.create_edit_window()
                        run_info = basic_window.edit_run_window.run_edit_window(window, run_info, selected_run_title, reset_run=reset_run)
                        if run_info == None:
                            break
                    else:
                        run_info = load_run(None, selected_run_title, [], runs_dir = consts.RUNS_DIR, 
                            update_archive_button=False)

                    update_log(f'\nrun details confirmed, creating main window\n')
                    window, rampart_running, piranha_running = basic_window.execute_run_window.create_main_window()
                    edit = basic_window.execute_run_window.run_main_window(window, run_info, rampart_running=rampart_running, piranha_running=piranha_running)
                    reset_run = False
                    if edit != True:
                        break
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
