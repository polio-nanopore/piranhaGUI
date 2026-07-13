import PySimpleGUI as sg
import sys

import artifice_core.consts as consts
import artifice_core.window_functions as window_functions
from artifice_core.language import translator, setup_translator
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import error_popup
from artifice_core.manage_runs import save_run, save_changes, load_run, check_supp_datadir

def setup_panel():
    sg.theme("PANEL")
    translator = setup_translator()

    config = consts.retrieve_config()

    button_size=(120,36)

    sample_type_list = ['stool', 'environmental','isolate']
    orientation_list = ['vertical','horizontal']

    tooltips = {
        '-USER NAME-':translator('Username to appear in report. Default: no user name'),
        '-INSTITUTE NAME-':translator('Institute name to appear in report. Default: no institute name'),
        '-ORIENTATION-':translator('Orientation of barcodes in wells on a 96-well plate. If `well` is supplied as a column in the barcode.csv, this default orientation will be overwritten. Default: `vertical`. Options: `horizontal` or `vertical`.'),
        '-SAMPLE TYPE-':f'{translator("Specify sample type. Options: `stool`, `environmental`, `isolate`. Default:")} `{consts.VALUE_SAMPLE_TYPE}`',
        '-POSITIVE CONTROL-':f'{translator("Sample name of positive control. Default:")} `{consts.VALUE_POSITIVE}`',
        '-NEGATIVE CONTROL-':translator('Sample name of negative control. Default: `negative`'),
    }

    if consts.PHYLO_ENABLED:
        phylo_button_text = 'Disable Piranha Phylogenetics module'
    else:
        phylo_button_text = 'Enable Piranha Phylogenetics module'
    
    if 'USERNAME' in config:
        default_username = config['USERNAME']
    else:
        default_username = ''
    
    if 'INSTITUTE' in config:
        default_institute = config['INSTITUTE']
    else:
        default_institute = ''
    
    if 'OUTDIR' in config:
        default_outdir = config['OUTDIR']
    else:
        default_outdir = ''

    layout = [
        [
            #sg.Push(),
            AltButton(translator(phylo_button_text),size=(396,32),key='-ENABLE PHYLO-'),
            ],
            [
            #sg.Push(),
            sg.Frame(title='',size=(1150,65), expand_x = True, layout=[
            [
                sg.Sizer(16,56),
                sg.Text(translator('Supplementary directory for phylogenetic module:'),
                        size=(42,1),justification='left'),
                sg.In(default_text=consts.PHYLO_DIR, enable_events=True,expand_y=True,font=consts.CONSOLE_FONT, 
                    pad=(0,5), disabled_readonly_background_color='#393938', expand_x=True,
                    text_color='#F5F1DF',
                    disabled_readonly_text_color='#F5F1DF', readonly=True, 
                    tooltip='Path to directory containing supplementary sequence FASTA file and optional metadata to be incorporated into phylogenetic analysis.', 
                    justification="left",  key='-PHYLO DIR-'),
                AltFolderBrowse(button_text=translator('Select')),
                AltButton(button_text=translator('Clear'), key='-CLEAR PHYLO DIR-'),
                #sg.Push()
            ],],
            visible=(consts.PHYLO_ENABLED),
            key = '-PHYLO FRAME-')],
        [
        sg.Column([ 
            [sg.Sizer(128,0)],
            [
            sg.Sizer(16,32),sg.Text(translator('User Name:'),tooltip=tooltips['-USER NAME-'], pad=(0,12), expand_y=True),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Institute:'),tooltip=tooltips['-INSTITUTE NAME-'], pad=(0,12), expand_y=True),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Output Folder:'), pad=(0,12), expand_y=True),
            ],
            [sg.Sizer(0,8)],
            [
            sg.Sizer(16,32),sg.Text(translator('Orientation:'),tooltip=tooltips['-ORIENTATION-'], pad=(0,12), expand_y=True),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Protocol:'),tooltip=tooltips['-SAMPLE TYPE-'], pad=(0,12), expand_y=True),
            ],
            [sg.Sizer(0,8)],
            [
            sg.Sizer(16,32),sg.Text(translator('Positive Control:'),tooltip=tooltips['-POSITIVE CONTROL-'], pad=(0,12), expand_y=True),
            ],
            [
            sg.Sizer(16,32),sg.Text(translator('Negative Control:'),tooltip=tooltips['-NEGATIVE CONTROL-'], pad=(0,12), expand_y=True),
            ],
        ],element_justification='right',pad=(0,0)),
        sg.Column([ 
            [sg.Sizer(256,0)],
            [
                sg.Sizer(16,32),
                sg.In(size=(42,1), enable_events=True,expand_y=True, border_width=1,
                      background_color='#393938', font=consts.CONSOLE_FONT, text_color='#F5F1DF', pad=(0,12),
                      default_text=default_username,tooltip=tooltips['-USER NAME-'], key='-USER NAME-',),
            ],
            [
                sg.Sizer(16,32),
                sg.In(size=(42,1), enable_events=True,expand_y=True,border_width=1,
                      background_color='#393938', font=consts.CONSOLE_FONT, text_color='#F5F1DF', 
                      default_text=default_institute,tooltip=tooltips['-INSTITUTE NAME-'],pad=(0,12), key='-INSTITUTE-',),
            ],
            [
                sg.Sizer(16,32),
                sg.In(size=(42,1), enable_events=True,expand_y=True, key='-OUTDIR-',font=consts.CONSOLE_FONT, 
                    disabled_readonly_background_color='#393938', expand_x=True,
                    text_color='#F5F1DF',
                    disabled_readonly_text_color='#F5F1DF',pad=(0,12), readonly=True),
                AltFolderBrowse(button_text=translator('Select'),),
                sg.Sizer(consts.BUTTON_SIZE[0], 0),
            ],
            [sg.Sizer(0,8)],
            [
                sg.Sizer(16,32),
                sg.OptionMenu(orientation_list, default_value=set_option_in_list('VALUE_ORIENTATION',orientation_list,config),tooltip=tooltips['-ORIENTATION-'], pad=(0,12), expand_y=True,key='-ORIENTATION-'),
            ],
            [
                sg.Sizer(16,32),
                sg.OptionMenu(sample_type_list, default_value=set_option_in_list('VALUE_SAMPLE_TYPE',sample_type_list,config),tooltip=tooltips['-SAMPLE TYPE-'], pad=(0,12), expand_y=True,key='-SAMPLE TYPE-'),
            ],
            [sg.Sizer(0,8)],
            [
                sg.Sizer(16,32),
                sg.In(size=(42,1), enable_events=True,expand_y=True,border_width=1,
                      background_color='#393938', font=consts.CONSOLE_FONT, text_color='#F5F1DF',
                      default_text=config['VALUE_POSITIVE'],tooltip=tooltips['-POSITIVE CONTROL-'], pad=(0,12), key='-POSITIVE CONTROL-',),
            ],
            [
                sg.Sizer(16,32),
                sg.In(size=(42,1), enable_events=True,expand_y=True,border_width=1,
                      background_color='#393938', font=consts.CONSOLE_FONT, text_color='#F5F1DF',
                      default_text=config['VALUE_NEGATIVE'],tooltip=tooltips['-NEGATIVE CONTROL-'], pad=(0,12), key='-NEGATIVE CONTROL-',),
            ]
        ],pad=(0,0))
    ]]

    panel = sg.Frame("", layout, border_width=0, relief="solid", pad=(0,0))

    return panel

def set_option_in_list(option_key, option_list, config):
    list_pos = 0
    try:
        list_pos = option_list.index(config[option_key])
    except:
        pass

    return option_list[list_pos]

#edits the value in config and for this run
def update_config_options(element_config_dict, element_option_dict, values, config, run_info):
    
    for element_key in element_config_dict:
        if len(values[element_key]) > 0: 
            if element_config_dict[element_key] in config:
                if values[element_key] != config[element_config_dict[element_key]]:
                    consts.edit_config(element_config_dict[element_key], values[element_key])
                    run_info[element_option_dict[element_key]] = values[element_key]
            else:
                consts.edit_config(element_config_dict[element_key], values[element_key])
                run_info[element_option_dict[element_key]] = values[element_key]
    
    return run_info
     

def create_persistent_run_options_window(window = None):
    update_log('creating run options window')

    panel = setup_panel()

    title = f'Piranha{" v" + consts.PIRANHA_VERSION if consts.PIRANHA_VERSION != None else ""}'

    content = window_functions.setup_content(panel, title=title, small=True, button_text='Continue', button_key='-CONFIRM-')

    layout = window_functions.setup_header_footer(content, small=True)

    new_window = sg.Window(title, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           modal=True, # keep_on_top=True, <- commented this out for now, creates issues for tooltips not showing correctly on mac, More info: https://github.com/PySimpleGUI/PySimpleGUI/issues/5952
                           font=consts.DEFAULT_FONT, icon=consts.ICON, margins=(0,0), element_padding=(0,0))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_persistent_run_options_window(window, run_info, version = 'ARTIFICE'):
    config = consts.retrieve_config()
    selected_run_title = run_info['title']

    element_config_dict = {'-POSITIVE CONTROL-':'VALUE_POSITIVE',
                    '-NEGATIVE CONTROL-':'VALUE_NEGATIVE',
                    '-SAMPLE TYPE-':'VALUE_SAMPLE_TYPE',
                    '-ORIENTATION-':'VALUE_ORIENTATION',
                    '-OUTDIR-':'OUTDIR',
                    '-INSTITUTE-':'INSTITUTE',
                    '-USER NAME-':'USERNAME',}
    
    element_option_dict = {'-POSITIVE CONTROL-':'-pc',
                    '-NEGATIVE CONTROL-':'-nc',
                    '-SAMPLE TYPE-':'-s', 
                    '-USER NAME-':'--username',
                    '-OUTDIR-':'outputPath',
                    '-INSTITUTE-':'--institute',
                    '-ORIENTATION-':'--orientation'}

    
    window['-SAMPLE TYPE-'].update(size=(100,100))
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [run options window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return run_info
        
        elif event == '-ENABLE PHYLO-':
            try:
                if consts.PHYLO_ENABLED:
                    consts.edit_config('PHYLO_ENABLED', False)
                    consts.PHYLO_ENABLED = False
                    window['-ENABLE PHYLO-'].update(text = translator('Enable Piranha Phylogenetics module'))
                    window['-PHYLO FRAME-'].update(visible=False)
                else:
                    consts.edit_config('PHYLO_ENABLED', True)
                    consts.PHYLO_ENABLED = True
                    window['-ENABLE PHYLO-'].update(text = translator('Disable Piranha Phylogenetics module'))
                    window['-PHYLO FRAME-'].update(visible=True)
            except Exception as err:
                error_popup(err)
        elif event == '-PHYLO DIR':
            pass
        
        elif event == '-CLEAR PHYLO DIR-':
            window['-PHYLO DIR-'].update('')
       
        elif event == '-CONFIRM-':
            try:
                if consts.PHYLO_ENABLED:
                    if len(values['-PHYLO DIR-']):
                        if check_supp_datadir(values['-PHYLO DIR-']):
                            print('checked')
                            consts.edit_config('PHYLO_DIR', values['-PHYLO DIR-'])
                        else:
                            raise Exception(translator('No valid fasta file in supplementary directory for phylogenetic module. You may want to check for non utf-8 special characters'))
                        
                run_info = update_config_options(element_config_dict, element_option_dict, values, config, run_info)
                window.close()
                return run_info
            except Exception as err:
                error_popup(err)

    window.close()
