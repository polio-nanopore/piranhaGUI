import PySimpleGUI as sg
import traceback
import docker

from artifice_core.language import translator,setup_translator
import artifice_core.parse_columns_window
import artifice_core.consts as consts
import artifice_core.start_rampart
import artifice_core.run_options_window
import artifice_core.window_functions as window_functions
from artifice_core.window_functions import error_popup
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run, rename_run, look_for_barcodes, set_options_from_excel, load_default_run_options
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok
from artifice_core.persistent_run_options_window import create_persistent_run_options_window, run_persistent_run_options_window


def setup_panel(translator):
    sg.theme("PANEL")

    y1 = 24
    y2 = 48

    column1 = [
            [
                sg.Sizer(1,y1),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('Samples:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y1),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('MinKnow Run:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('Run Name:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('User Name:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('Institute:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('Notes:'), pad=(0,12), expand_y=True),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y1),
            ],
            [
                sg.Sizer(1,y2), sg.Text(translator('Output Folder:'), pad=(0,12), expand_y=True),
            ]]
    column2 = [
            [                
                sg.Sizer(1,y1),
                sg.Text(translator('Select a CSV file containing the IDs and barcodes for each sample:'),font=consts.CAPTION_FONT),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-SAMPLES-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), disabled_readonly_background_color='#393938', expand_x=True,
                    disabled_readonly_text_color='#F5F1DF', text_color='#F5F1DF', readonly=True, justification="left"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-SAMPLES-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFileBrowse(button_text=translator('Select'),key='-SELECT SAMPLES-'),#file_types=(("CSV Files", "*.csv"),)),
                AltButton(button_text=translator('View'),key='-VIEW SAMPLES-'),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [                
                sg.Sizer(1,y1),
                sg.Text(translator('Select the folder containing sequencing reads from MinKnow:'),font=consts.CAPTION_FONT),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-MINKNOW-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), disabled_readonly_background_color='#393938', expand_x=True,
                    disabled_readonly_text_color='#F5F1DF', text_color='#F5F1DF', readonly=True, justification="left"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-MINKNOW-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFolderBrowse(button_text=translator('Select')),
                sg.Sizer(consts.BUTTON_SIZE[0], 0),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-RUN NAME-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), background_color='#393938', #expand_x=True,
                    text_color='#F5F1DF', justification="left"),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-USER NAME-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), background_color='#393938', #expand_x=True,
                    text_color='#F5F1DF', justification="left"),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-INSTITUTE-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), background_color='#393938', #expand_x=True,
                    text_color='#F5F1DF', justification="left"),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-NOTES-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), background_color='#393938', #expand_x=True,
                    text_color='#F5F1DF', justification="left"),
            ],
            [                
                sg.Sizer(1,16),
            ],
            [                
                sg.Sizer(1,y1),
                sg.Text(translator('Select a folder for the output of Piranha analysis:'),font=consts.CAPTION_FONT),
            ],
            [
                sg.Sizer(1,y2),
                sg.In(enable_events=True,expand_y=True, key='-OUTDIR-',font=consts.CONSOLE_FONT, 
                    pad=(0,12), disabled_readonly_background_color='#393938', expand_x=True,
                    disabled_readonly_text_color='#F5F1DF', text_color='#F5F1DF', readonly=True, justification="left"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-OUTDIR-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFolderBrowse(button_text=translator('Select'),),
                sg.Sizer(consts.BUTTON_SIZE[0], 0),
            ]]

    panel = sg.Column([[
        sg.Sizer(16,16),
        sg.Frame(translator("Sequencing Run:"), [
            [
                sg.Sizer(32,0),
                sg.Column(column1, element_justification='Right'),
                sg.Column(column2, expand_x=True),
            ]], border_width=0, relief="solid", pad=(16,8), expand_x=True, expand_y=True)]],  expand_x=True, expand_y=True)

    return panel

def create_edit_window(window = None):
    update_log('creating main window')
    translator = setup_translator()

    panel = setup_panel(translator)

    title = f'Piranha{" v" + consts.PIRANHA_VERSION if consts.PIRANHA_VERSION != None else ""}'

    content = window_functions.setup_content(panel, title=title, 
                                             button_text='Continue', button_key='-CONFIRM-', button_disabled=True,
                                             top_left_button_text='Persistent Run Options', top_left_button_key='-PERSISTENT RUN OPTIONS-',
                                             bottom_left_button_text='Set options for this run', bottom_left_button_key='-RUN OPTIONS-')

    layout = window_functions.setup_header_footer(content)

    new_window = sg.Window(title, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           font=consts.DEFAULT_FONT, icon=consts.ICON, 
                           margins=(0,0), element_padding=(0,0))
    new_window.set_min_size(size=(512,320))

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")
    new_window['-OUTDIR-'].bind("<FocusOut>", "FocusOut")

    AltButton.intialise_buttons(new_window)

    return new_window

def run_edit_window(window, run_info, selected_run_title, reset_run = True):
    config = consts.retrieve_config()
    docker_client = docker.from_env()
    translator = setup_translator()

    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath',
                    '-OUTDIR-':'outputPath',
                    '-RUN NAME-':'--runname',
                    '-INSTITUTE-':'--institute',
                    '-USER NAME-':'--username',
                    '-NOTES-':'--notes'}

    element_config_dict = {'-POSITIVE CONTROL-':'VALUE_POSITIVE',
                    '-NEGATIVE CONTROL-':'VALUE_NEGATIVE',
                    '-SAMPLE TYPE-':'VALUE_SAMPLE_TYPE',
                    '-ORIENTATION-':'VALUE_ORIENTATION',
                    '-OUTDIR-':'OUTDIR',
                    '-INSTITUTE-':'INSTITUTE',
                    '-USER NAME-':'USERNAME',}
    
    # dictionary used to try to match options from excel to elements in window, case insensitive
    el_string_dict = {'-MINKNOW-':['basecalledPath','minknow run','-i','--readdir','readdir','read dir','MINKNOW'],
                      '-OUTDIR-':['outputPath','output path','Output Path','-o','--outdir','outdir'],
                      '-RUN NAME-':['--runname','run name','Run Name','Title'],
                      '-INSTITUTE-':['--institute','institute','Institute','institution','Institution'],
                      '-USER NAME-':['--username','username','Username','User Name','User'],
                      '-NOTES-':['--notes', 'notes', 'Notes', 'note', 'Note']}
    
    try:
        event, values = window.read()
        run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], 
                            update_archive_button=False)
        
        if reset_run == True:
            save_run(run_info, title = 'PREVIOUS_RUN', runs_dir = config['RUNS_DIR'], overwrite = True,)
            run_info = {'title': 'TEMP_RUN'}
            for elem in element_dict:
                window[elem].update('')
            
            for element in ['-USER NAME-','-INSTITUTE-','-OUTDIR-']:
                if element_config_dict[element] in config:
                    window[element].update(value=config[element_config_dict[element]])
                        
    except Exception as err:
        update_log(traceback.format_exc())

    while True:
        event, values = window.read()
        continue_disabled = False
        for key in ['-SAMPLES-','-MINKNOW-','-OUTDIR-']:
            if len(values[key]) == 0:
                continue_disabled = True
        window['-CONFIRM-'].update(disabled=continue_disabled)

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return
        
        elif event == '-SAMPLES-':
            try:
                if values['-SAMPLES-'].endswith('.xls') or values['-SAMPLES-'].endswith('.xlsx'):
                    #samples_list, column_headers, options = excel_to_list(values['-SAMPLES-'])
                    #print(options)
                    set_options_from_excel(values['-SAMPLES-'], el_string_dict, window)
            except Exception as err:
                error_popup(err)

        elif event == '-VIEW SAMPLES-':
            try:
                if '-SAMPLES-' not in values:
                    error_popup("Samples not found in values")
                
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                new_run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-')
                if new_run_info != None:
                    run_info = new_run_info
                    selected_run_title = save_run(run_info, title=selected_run_title, overwrite=True)
            except Exception as err:
                error_popup(err)
                """
        elif event in {'-SAMPLES-FocusOut','-MINKNOW-FocusOut','-OUTDIR-FocusOut'}:
            try:
                if 'title' in run_info:
                    run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                else:
                    clear_selected_run(window)
            except Exception as err:
                update_log(traceback.format_exc())
                sg.popup_error(err)
                try:
                    run_info = load_run(window, run_info['title'])
                except Exception as err:
                    update_log(traceback.format_exc())
                    sg.popup_error(err)
        """
        elif event == '-RUN OPTIONS-':
            try:
                run_options_window = artifice_core.run_options_window.create_run_options_window()
                run_info = artifice_core.run_options_window.run_run_options_window(run_options_window, run_info)
  
            except Exception as err:
                error_popup(err)
        
        elif event == '-PERSISTENT RUN OPTIONS-':
            try:
                run_options_window = create_persistent_run_options_window()
                run_info = run_persistent_run_options_window(run_options_window, run_info)
                for element in ['-USER NAME-','-INSTITUTE-','-OUTDIR-']:
                    if element_dict[element] in run_info:
                        window[element].update(value=run_info[element_dict[element]])
  
            except Exception as err:
                error_popup(err)

        elif event == '-CONFIRM-':
            try:
                if 'PHYLO_ENABLED' in config:
                    if config['PHYLO_ENABLED']:
                        run_info['-rp'] = True
                        if 'PHYLO_DIR' in config:
                            run_info['PHYLO_DIR'] = config['PHYLO_DIR']
                    else:
                        run_info['-rp'] = False
                        run_info['PHYLO_DIR'] = ''
                if len(values['-MINKNOW-']) > 0:
                    new_minknow, run_name = look_for_barcodes(values['-MINKNOW-'])
                    if values['-RUN NAME-'] == '':
                        window['-RUN NAME-'].update(value=run_name)
                        values['-RUN NAME-'] = run_name
                        
                    if new_minknow != None:
                        #if alt_popup_yes_no(translator('Detected ')):
                        #minknow_base_dir = os.path.basename(new_minknow)                     
                        window['-MINKNOW-'].update(value=new_minknow)
                        values['-MINKNOW-'] = new_minknow
                    #print(new_minknow)
                
                print(run_info)
                run_info = load_default_run_options(run_info)
                print(run_info)
                
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)

                if artifice_core.parse_columns_window.check_spaces(run_info['samples'], 0):
                    alt_popup_ok(translator('Warning: there are spaces in samples'))
                window.close()
                return run_info
            except Exception as err:
                error_popup(err)

    window.close()


