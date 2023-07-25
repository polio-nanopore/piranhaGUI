import PySimpleGUI as sg
import sys

import artifice_core.consts as consts
import artifice_core.window_functions as window_functions
from artifice_core.language import translator
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import error_popup
from artifice_core.manage_runs import save_run, save_changes, load_run

def setup_panel():
    sg.theme("PANEL")

    config = consts.retrieve_config()

    button_size=(120,36)

    sample_types_list = ['stool', 'environmental']
    orientations_list = ['horizontal', 'vertical']

    tooltips = {
        '-USER NAME-':translator('Username to appear in report. Default: no user name'),
        '-INSTITUTE NAME-':translator('Institute name to appear in report. Default: no institute name'),
        '-ORIENTATION-':translator('Orientation of barcodes in wells on a 96-well plate. If `well` is supplied as a column in the barcode.csv, this default orientation will be overwritten. Default: `horizontal`. Options: `horizontal` or `vertical`.'),
        '-SAMPLE TYPE-':translator(f'Specify sample type. Options: `stool`, `environmental`. Default: {consts.VALUE_SAMPLE_TYPE}'),
        '-POSITIVE CONTROL-':translator(f'Sample name of positive control. Default: {consts.VALUE_POSITIVE}'),
        '-NEGATIVE CONTROL-':translator('Sample name of negative control. Default: `negative`'),
    }

    layout = [[
        sg.Column([ 
            #[sg.Sizer(128,0)],
            [
            sg.Sizer(16,32),sg.Text(translator('User Name:'),tooltip=tooltips['-USER NAME-']),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Institute:'),tooltip=tooltips['-INSTITUTE NAME-']),
            ],
            [sg.Sizer(0,8)],
            [
            sg.Sizer(16,32),sg.Text(translator('Orientation:'),tooltip=tooltips['-ORIENTATION-']),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Sample Type:'),tooltip=tooltips['-SAMPLE TYPE-'],),
            ],
            [sg.Sizer(0,8)],
            [
            sg.Sizer(16,32),sg.Text(translator('Positive Control:'),tooltip=tooltips['-POSITIVE CONTROL-']),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Negative Control:'),tooltip=tooltips['-NEGATIVE CONTROL-']),
            ],
        ],element_justification='right',pad=(0,0)),
        sg.Column([ 
            [sg.Sizer(256,0)],
            [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,border_width=1,
                      tooltip=tooltips['-USER NAME-'], key='-USER NAME-',),
            ],
            [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,border_width=1,
                      tooltip=tooltips['-INSTITUTE NAME-'], key='-INSTITUTE NAME-',),
            ],
            [sg.Sizer(0,8)],
            [
                sg.Sizer(16,32),
                sg.OptionMenu(orientations_list, default_value=orientations_list[0],tooltip=tooltips['-ORIENTATION-'],key='-ORIENTATION-'),
            ],
            [
                sg.Sizer(16,32),
                sg.OptionMenu(sample_types_list, default_value=sample_types_list[0],tooltip=tooltips['-SAMPLE TYPE-'],key='-SAMPLE TYPE-'),
            ],
            [sg.Sizer(0,8)],
            [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,border_width=1,
                      default_text=consts.VALUE_POSITIVE,tooltip=tooltips['-POSITIVE CONTROL-'], key='-POSITIVE CONTROL-',),
            ],
            [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,border_width=1,
                      default_text=consts.VALUE_NEGATIVE,tooltip=tooltips['-NEGATIVE CONTROL-'], key='-NEGATIVE CONTROL-',),
            ]
        ],pad=(0,0))
    ]]

    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,0))

    return panel

def create_run_options_window(version = 'ARTIFICE', window = None):
    update_log('creating run options window')

    panel = setup_panel()

    content = window_functions.setup_content(panel, small=True, button_text='Continue', button_key='-CONFIRM-')

    layout = window_functions.setup_header_footer(content, small=True)

    new_window = sg.Window(version, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           font=consts.DEFAULT_FONT, icon=consts.ICON, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_run_options_window(window, run_info, version = 'ARTIFICE'):
    config = consts.retrieve_config()
    selected_run_title = run_info['title']

    element_dict = {'-POSITIVE CONTROL-':'-pc',
                    '-NEGATIVE CONTROL-':'-nc',
                    '-SAMPLE TYPE-':'-s', 
                    '-USER NAME-':'--username',
                    '-INSTITUTE NAME-':'--institute',
                    '-ORIENTATION-':'--orientation'}
    run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], update_archive_button=False, clear_previous=False)
    
    window['-SAMPLE TYPE-'].update(size=(100,100))
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [run options window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return run_info
       
        elif event == '-CONFIRM-':
            try:
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                window.close()
                return run_info
            except Exception as err:
                error_popup(err)

    window.close()
