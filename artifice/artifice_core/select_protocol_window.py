from tkinter import W
import PySimpleGUI as sg
import traceback
import json
import os.path
from os import listdir, mkdir
from pathlib import Path
from shutil import rmtree, copytree

from artifice_core.language import translator,setup_translator
import artifice_core.parse_columns_window
import artifice_core.consts as consts
import artifice_core.start_rampart
import artifice_core.add_protocol_window
import artifice_core.window_functions as window_functions
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.window_functions import error_popup

# makes sure builtin protocols are installed
def setup_config():
    config_path = str(consts.get_datadir() / 'builtin_protocols')
    if os.path.isfile(config_path):
        return True
    else:
        builtin_path = consts.get_resource('builtin_protocols')
        copytree(builtin_path, config_path)

def setup_panel():
    sg.theme("PANEL")
    translator = setup_translator()

    config = consts.retrieve_config()

    try:
        mkdir(config['PROTOCOLS_DIR'])
    except:
        pass

    try:
        add_protocol('ARTIC Poliovirus protocol v1.1', str(consts.get_datadir() / 'builtin_protocols' / 'rampart'), config)
    except:
        pass

    try:
        add_protocol('default RAMPART protocol', str(consts.get_datadir() / 'builtin_protocols' / 'default_protocol'), config)
    except:
        pass

    #button_size=(140,36)

    protocols = listdir(config['PROTOCOLS_DIR'])
    if config['PROTOCOL'] in protocols:
        selected_protocol = config['PROTOCOL']
    else:
        selected_protocol = protocols[0]

    view_protocol_column = [
        [
            sg.Listbox(
                values=protocols, default_values=[selected_protocol], enable_events = True, size=(40,20), select_mode = sg.LISTBOX_SELECT_MODE_BROWSE, key ='-PROTOCOL LIST-',
            )
        ],
    ]

    protocol_dir, protocol_desc = get_protocol_info(config['PROTOCOLS_DIR'], config['PROTOCOL'])

    protocol_info_column = [
    [sg.Text(translator('Directory:'),size=(14,1)),],
    [sg.Text(protocol_dir,font=(None,12),size=(80,1),key='-PROTOCOL DIR-'),],
    [sg.VPush()],
    [sg.Text(translator('Description:'),size=(14,1)),],
    [sg.Text(protocol_desc,font=(None,12),size=(80,1),key='-PROTOCOL DESC-'),],
    [sg.VPush()],
    [
        AltButton(button_text=translator('Add Protocol'),key='-ADD PROTOCOL-'),
        sg.Push(),
        AltButton(button_text=translator('Remove Protocol'),key='-REMOVE PROTOCOL-'),
        # sg.Push(),
        # AltButton(button_text=translator('Confirm'),size=button_size,key='-CONFIRM-'),
    ]]

    panel = sg.Frame("", [[sg.Column([
            [
                sg.Column(view_protocol_column),
                sg.Column(protocol_info_column, expand_y=True),
            ]], pad=(16,16))]], border_width=0, relief="solid", pad=(0,16))

    return panel

def get_protocol_dir(art_protocol_path):
    try:
        with open(art_protocol_path / 'info.json','r') as file:
            protocol_info = json.loads(file.read())
            dir = protocol_info["directory"]
    except:
        dir = None

    return dir

def get_protocol_desc(protocol_dir):
    return get_protocol_details(protocol_dir, "description")

def get_protocol_details(protocol_dir, key):
    try: 
        with open(protocol_dir + '/protocol.json','r') as file:
            protocol_json = json.loads(file.read())
            value = protocol_json[key]
    except:
        value = ""

    return value


def create_protocol_window(window = None):
    update_log('creating protocol window')

    panel = setup_panel()

    title = f'RAMPART{" v" + consts.RAMPART_VERSION if consts.RAMPART_VERSION != None else ""}'

    content = window_functions.setup_content(panel, title=title, small=True, button_text='Confirm', button_key='-CONFIRM-')

    layout = window_functions.setup_header_footer(content, small=True,)

    new_window = sg.Window(title, layout, resizable=False, enable_close_attempted_event=True, 
                           finalize=True,icon=consts.ICON,font=consts.DEFAULT_FONT, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window


def get_protocol_info(protocols_dir, protcol):
    try:
        art_protocol_path = protocols_dir / protcol
    except:
        art_protocol_path = None

    protocol_dir = get_protocol_dir(art_protocol_path)
    if protocol_dir == None:
        protcol_descr = ""
    else:
        protcol_descr = get_protocol_desc(protocol_dir)

    return protocol_dir, protcol_descr

def add_protocol(protocol_name, protocol_dir, config):
    art_protocol_path = config['PROTOCOLS_DIR'] / protocol_name
    
    mkdir(art_protocol_path)
    
    protocol_info = {"directory":protocol_dir}
    
    with open(art_protocol_path / 'info.json', 'w') as file:
        json.dump(protocol_info, file)

    update_log(f'created protocol: {protocol_name}')

def remove_protocol(protocol_name, config, clear_selected = True,):
    update_log(f'removing protocol: "{protocol_name}"')

    art_protocol_path = config['PROTOCOLS_DIR'] / protocol_name

    if os.path.isdir(art_protocol_path):
        rmtree(art_protocol_path)

    #if clear_selected:
     #   clear_selected_run(window)

def update_protocols_list(protocol_to_select, window, config):
    protocols = listdir(config['PROTOCOLS_DIR'])
    window['-PROTOCOL LIST-'].update(values=protocols)

    for i in range(len(protocols)):
        print(protocols[i])
        if protocols[i] == protocol_to_select:
            update_log(f'selecting run: {protocol_to_select}')
            window['-PROTOCOL LIST-'].update(set_to_index=i)

def select_protocol(config, values, window):
    protocol_dir, protocol_desc = get_protocol_info(config['PROTOCOLS_DIR'], values['-PROTOCOL LIST-'][0])
    window['-PROTOCOL DIR-'].update(protocol_dir)
    window['-PROTOCOL DESC-'].update(protocol_desc)
    

def run_protocol_window(window, version = 'ARTIFICE'):
    config = consts.retrieve_config()
    translator = setup_translator()
    
    
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [select protocol window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return
        
        elif event == '-PROTOCOL LIST-':
            try:
                select_protocol(config,values,window)
            except Exception as err:
                error_popup(err)
    
        elif event == '-ADD PROTOCOL-':
            try:
                add_protocol_window = artifice_core.add_protocol_window.create_add_protocol_window(version=version)
                added_protocol_dir = artifice_core.add_protocol_window.run_add_protocol_window(add_protocol_window, version=version)
                print(added_protocol_dir)
                if added_protocol_dir != None:
                    protocol_name = get_protocol_details(added_protocol_dir, "name")
                    if protocol_name == "":
                        raise Exception(translator('Error parsing protocol'))

                    try:
                        add_protocol(protocol_name, added_protocol_dir, config)
                    except FileExistsError:
                        raise Exception(translator('a protocol with that name already exists, please change the name in protocol.json and try again'))
                    
                    update_protocols_list(protocol_name, window, config)
                    
            except Exception as err:
                error_popup(err)

        elif event == '-REMOVE PROTOCOL-':
            try:
                protocol = values['-PROTOCOL LIST-'][0]
                remove_protocol(protocol, config)
                if protocol == config['PROTOCOL']:
                    consts.edit_config('PROTOCOL', 'None')
                
                update_protocols_list(None, window, config)
                select_protocol(config,values,window)
                
            except Exception as err:
                error_popup(err)


        elif event == '-CONFIRM-':
            try:
                if len(values['-PROTOCOL LIST-']) > 0:
                    protocol = values['-PROTOCOL LIST-'][0]
                else:
                    protocol = None
                consts.edit_config('PROTOCOL', protocol)
                update_log(f'selected protocol: {protocol}')
                window.close()
                return protocol
            except Exception as err:
                error_popup(err)

    window.close()
