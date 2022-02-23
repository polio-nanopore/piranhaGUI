import PySimpleGUI as sg
from os import listdir, mkdir, remove, getcwd, rename
import os.path
import requests
import json
from webbrowser import open_new_tab
from shutil import rmtree, move, copytree
from datetime import datetime
from time import sleep
import traceback

import consts
import selection_window
import parse_columns_window
import start_rampart
import view_barcodes_window
from update_log import log_event, update_log
from infotab import infotab_event
from manage_runs import save_run, delete_run, clear_selected_run, update_run_list, get_runs, save_changes

def make_theme():
    Artifice_Theme = {'BACKGROUND': "#072429",
               'TEXT': '#f7eacd',
               'INPUT': '#1e5b67',
               'TEXT_INPUT': '#f7eacd',
               'SCROLL': '#707070',
               'BUTTON': ('#f7eacd', '#d97168'),
               'PROGRESS': ('#000000', '#000000'),
               'BORDER': 1,
               'SLIDER_DEPTH': 0,
               'PROGRESS_DEPTH': 0}

    sg.theme_add_new('Artifice', Artifice_Theme)

#defines the layout of the window
def setup_layout(theme='Dark', font = None):
    sg.theme(theme)
    runs = get_runs()

    select_run_column = [
        [
            sg.Button(button_text='Create New Run',size=(15,2),key='-NEW RUN-'),
            sg.Push()
        ],
        [
            sg.Text('Previous Runs:')
        ],
        [
            sg.Listbox(
                values=runs, enable_events = True, size=(40,20), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-RUN LIST-',
            )
        ],
        [
            sg.Button(button_text='Show All Runs',key='-SHOW/HIDE ARCHIVED-'),
        ],
    ]

    run_info_tab = [
        [
        sg.Text('Name:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-RUN NAME-',),
        ],
        [
        sg.Text('Date Created:',size=(13,1)),
        sg.Text('', size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-DATE-',),
        ],
        [
        sg.Text('Description:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-RUN DESCR-',),
        ],
        [
        sg.Text('Samples:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-SAMPLES-',),
        sg.FileBrowse(file_types=(("CSV Files", "*.csv"),)),
        sg.Button(button_text='View',key='-INFOTAB-VIEW SAMPLES-'),
        ],
        [
        sg.Text('MinKnow run:',size=(13,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False, key='-INFOTAB-MINKNOW-',),
        sg.FolderBrowse(),
        ],
        [
        sg.Button(button_text='Delete',key='-INFOTAB-DELETE RUN-'),
        sg.Button(button_text='Archive',key='-INFOTAB-ARCHIVE/UNARCHIVE-'),
        ],
        [
        sg.Push(),
        sg.Button(button_text='RAMPART >', key='-INFOTAB-TO RAMPART-'),
        ],
    ]
    try:
        r = requests.get(f'http://localhost:{consts.RAMPART_PORT_1}')
        if r.status_code == 200:
            rampart_running = True
            rampart_button_text = 'Stop RAMPART'
        else:
            rampart_running = False
    except:
        rampart_running = False

    update_log('checking if RAMPART is running...')
    rampart_running = check_rampart_running()
    if rampart_running:
        rampart_button_text = 'Stop RAMPART'
        rampart_status = 'RAMPART is running'
    else:
        rampart_button_text = 'Start RAMPART'
        rampart_status = 'RAMPART is not running'




    rampart_tab = [
    [sg.Button(button_text='View Barcodes',key='-VIEW BARCODES-'),],
    [sg.Text(rampart_status, key='-RAMPART STATUS-'),],
    [
    sg.Button(button_text=rampart_button_text,key='-START/STOP RAMPART-'),
    sg.Button(button_text='View RAMPART', visible=rampart_running,key='-VIEW RAMPART-'),
    ],
    [
    sg.VPush()
    ],
    [
    sg.Button(button_text='< Info', key='-TO INFO-'),
    sg.Push(),
    sg.Button(button_text='PIRANHA >', key='-TO PIRANHA-'),
    ],
    ]

    piranha_tab = [
    [sg.Text('piranha'),],
    [
    sg.VPush()
    ],
    [
    sg.Button(button_text='< RAMPART', key='-TO RAMPART-'),
    sg.Push(),
    ],
    ]

    tabs_column = [
        [
        sg.TabGroup([[sg.Tab('Info',run_info_tab,key='-RUN INFO TAB-'),sg.Tab('RAMPART',rampart_tab,key='-RAMPART TAB-'),sg.Tab('PIRANHA',piranha_tab,key='-PIRANHA TAB-')]])
        ],
        [
        sg.Button(button_text='Hide Runs',key='-SHOW/HIDE RUNLIST-'),
        ],
    ]

    processed_image = './resources/a_logo.png'


    # Resize PNG file to size (300, 300)
    #image_file = './resources/logo.png'
    #size = (100, 120)
    #im = Image.open(image_file)
    #im = im.resize(size, resample=Image.BICUBIC)
    #im.save(processed_image)
    #im_bytes = im.tobytes()

    frame_bg = sg.LOOK_AND_FEEL_TABLE['Artifice']['INPUT']

    layout = [
        [
        sg.Frame('',[[sg.Image(source = processed_image), sg.Text("ARTIFICE", font = (consts.FONT,30), background_color = frame_bg)]], background_color = frame_bg)
        ],
        [
        sg.pin(sg.Column(select_run_column, element_justification = 'center', key='-SELECT RUN COLUMN-')),
        sg.Column(tabs_column, expand_y=True, expand_x=True,key='-TAB COLUMN-'),
        ],
    ]

    return layout, rampart_running


def check_rampart_running():
    try:
        r = requests.get(f'http://localhost:{consts.RAMPART_PORT_1}')
        if r.status_code == 200:
            update_log(f'detected RAMPART running on port: {consts.RAMPART_PORT_1}')
            return True
        else:
            return False
    except:
        return False

def create_run(font=None):
    update_log(f'creating new run')
    window = selection_window.create_select_window(font=font)
    selections = selection_window.run_select_window(window)

    if selections == None:
        return None

    samples, basecalledPath, has_headers = selections

    window, column_headers = parse_columns_window.create_parse_window(samples, font=font,has_headers=has_headers)
    samples_barcodes_indices = parse_columns_window.run_parse_window(window, samples, column_headers)

    if samples_barcodes_indices == None:
        return None

    samples_column, barcodes_column = samples_barcodes_indices

    run_info = {}

    run_info['date'] = datetime.today().strftime('%Y-%m-%d')
    run_info['samples'] = samples.strip()
    run_info['basecalledPath'] = basecalledPath.strip()
    run_info['barcodes_column'] = str(barcodes_column).strip()
    run_info['samples_column']  = str(samples_column).strip()
    run_info['has_headers'] = has_headers

    title = save_run(run_info)
    view_barcodes_window.save_barcodes(run_info)
    update_log(f'created run: "{title}" successfully')

    return title


def launch_rampart(run_info, client, firstPort = 1100, secondPort = 1200, runs_dir = consts.RUNS_DIR, font = None, container = None):
    if 'title' not in run_info or not len(run_info['title']) > 0:
        raise Exception('Invalid Name/No Run Selected')
    title = run_info['title']
    update_log(f'launching RAMPART on run: "{title}"')
    if 'samples' not in run_info or os.path.isfile(run_info['samples']) == False:
        raise Exception('Invalid samples file')
    if 'basecalledPath' not in run_info or os.path.isdir(run_info['basecalledPath']) == False:
        raise Exception('Invalid MinKnow')

    basecalled_path = run_info['basecalledPath']

    config_path = runs_dir+'/'+title+'/run_configuration.json'

    try:
        with open(config_path,'r') as file:
            run_configuration = json.loads(file.read())
    except:
        run_configuration = {}

    run_configuration['title'], run_configuration['basecalledPath'] = run_info['title'], run_info['basecalledPath']

    with open(config_path, 'w') as file:
        config_json = json.dump(run_configuration, file)
        #file.write(config_json)

    view_barcodes_window.check_barcodes(run_info,font=font)

    run_path = runs_dir+'/'+run_info['title']
    container = start_rampart.start_rampart(run_path, basecalled_path, client, consts.DOCKER_IMAGE, firstPort = firstPort, secondPort = secondPort, container=container)

    iter = 0
    while True:
        sleep(0.1)
        iter += 1
        if iter > 100:
            raise Exception('Something went wrong launching RAMPART')
        try:
            rampart_running = check_rampart_running()
            if rampart_running:
                return container
        except:
            pass

def create_main_window(theme = 'Artifice', font = None, window = None):
    update_log('creating main window')
    make_theme()
    layout, rampart_running = setup_layout(theme=theme, font=font)
    new_window = sg.Window('ARTIFICE', layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True)

    if window != None:
        window.close()

    new_window['-INFOTAB-RUN NAME-'].bind("<FocusOut>", "FocusOut")
    new_window['-INFOTAB-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-INFOTAB-RUN DESCR-'].bind("<FocusOut>", "FocusOut")
    new_window['-INFOTAB-MINKNOW-'].bind("<FocusOut>", "FocusOut")

    return new_window, rampart_running

def run_main_window(window, font = None, rampart_running = False):
    runlist_visible = True
    hide_archived = True
    run_info = {}
    selected_run_title = ''
    docker_client = None
    rampart_container = None

    docker_installed = start_rampart.check_for_docker()
    if not docker_installed:
        window.close()
        return None

    got_image, docker_client = start_rampart.check_for_image(docker_client, consts.DOCKER_IMAGE, font=font)

    if not got_image:
        window.close()
        return None

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            if rampart_running:
                chk_stop = sg.popup_yes_no('Do you wish to stop RAMPART while closing', font=font)
                window.close()

                if chk_stop == 'Yes':
                    update_log('stopping RAMPART...')
                    start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    update_log('RAMPART stopped')
                else:
                    update_log('User chose to keep RAMPART running')
            break

        elif event.startswith('-INFOTAB-'):
            run_info, selected_run_title = infotab_event(event, run_info, selected_run_title, hide_archived, font, values, window)

        elif event == '-RUN LIST-':
            try:
                update_log(f'run_info: {run_info}')
                old_run_info = None
                if 'title' in run_info:
                    old_run_info = dict(run_info)

                try:
                    if not old_run_info == None:
                        save_changes(values, old_run_info, window, hide_archived=hide_archived)
                except Exception as err:
                    update_log(traceback.format_exc())
                    sg.popup_error(err)


                selected_run_title = values['-RUN LIST-'][0]
                #run_info = load_run(window, selected_run_title)

                run_info = update_run_list(window, {}, run_to_select=selected_run_title, hide_archived=hide_archived)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-NEW RUN-':
            try:
                selected_run_title = create_run(font)
                if selected_run_title == None:
                    continue

                run_info = update_run_list(window, run_info, run_to_select=selected_run_title, hide_archived=hide_archived)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-SHOW/HIDE ARCHIVED-':
            try:
                if hide_archived:
                    update_log('showing archived runs')
                    hide_archived = False
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived)
                    window['-SHOW/HIDE ARCHIVED-'].update(text='Hide Archived Runs')
                else:
                    update_log('hiding archived runs')
                    hide_archived = True
                    run_info = update_run_list(window, run_info, hide_archived=hide_archived)
                    window['-SHOW/HIDE ARCHIVED-'].update(text='Show All Runs')
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-SHOW/HIDE RUNLIST-':
            if runlist_visible:
                update_log('hiding run list')
                window['-SELECT RUN COLUMN-'].update(visible=False)
                window['-SHOW/HIDE RUNLIST-'].update(text='Show Runs')
                runlist_visible = False
            else:
                update_log('showing run list')
                window['-SELECT RUN COLUMN-'].update(visible=True)
                window['-SHOW/HIDE RUNLIST-'].update(text='Hide Runs')
                runlist_visible = True


        elif event == '-VIEW BARCODES-':
            try:
                view_barcodes_window.check_barcodes(run_info, font=font)

                barcodes = consts.RUNS_DIR+'/'+run_info['title']+'/barcodes.csv'
                barcodes_window, column_headers = view_barcodes_window.create_barcodes_window(barcodes,font=font)
                view_barcodes_window.run_barcodes_window(barcodes_window,barcodes,column_headers)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event == '-START/STOP RAMPART-':
            try:
                if rampart_running:
                    #try:
                        #print(rampart_container.top())
                    #except:
                    #    pass
                    rampart_running = False
                    start_rampart.stop_docker(client=docker_client, container=rampart_container)
                    window['-VIEW RAMPART-'].update(visible=False)
                    window['-START/STOP RAMPART-'].update(text='Start RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is not running')
                else:
                    rampart_container = launch_rampart(run_info, docker_client, firstPort=consts.RAMPART_PORT_1, secondPort=consts.RAMPART_PORT_2, font=font, container=rampart_container)
                    rampart_running = True
                    window['-VIEW RAMPART-'].update(visible=True)
                    window['-START/STOP RAMPART-'].update(text='Stop RAMPART')
                    window['-RAMPART STATUS-'].update('RAMPART is running')

                    #print(rampart_container.logs())
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

        elif event.endswith('-TO RAMPART-'):
            window['-RAMPART TAB-'].select()

        elif event == '-TO INFO-':
            window['-RUN INFO TAB-'].select()

        elif event == '-TO PIRANHA-':
            window['-PIRANHA TAB-'].select()

        elif event == '-VIEW RAMPART-':
            address = 'http://localhost:'+str(consts.RAMPART_PORT_1)
            update_log(f'opening address: "{address}" in browser to view RAMPART')
            try:
                open_new_tab(address)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)

    window.close()

if __name__ == '__main__':
    #print(sg.LOOK_AND_FEEL_TABLE['Dark'])
    font = (consts.FONT, 18)

    window, rampart_running = create_main_window(font=font)
    run_main_window(window, rampart_running=rampart_running, font=font)

    window.close()
