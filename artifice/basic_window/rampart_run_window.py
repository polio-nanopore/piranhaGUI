import PySimpleGUI as sg
import traceback
import docker

from artifice_core.language import translator
import artifice_core.parse_columns_window
import artifice_core.consts as consts
import artifice_core.start_rampart
import artifice_core.run_options_window
import artifice_core.window_functions as window_functions
from artifice_core.window_functions import error_popup
from artifice_core.update_log import log_event, update_log
from artifice_core.manage_runs import save_run, save_changes, load_run
from artifice_core.alt_button import AltButton, AltFolderBrowse, AltFileBrowse
from artifice_core.alt_popup import alt_popup_ok


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
                sg.Sizer(1,y2), sg.Text(translator('MinKnow run:'), pad=(0,12), expand_y=True),
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
                    text_color='#F5F1DF',
                    disabled_readonly_text_color='#F5F1DF', readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-SAMPLES-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFileBrowse(button_text=translator('Select'),file_types=(("CSV Files", "*.csv"),)),
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
                    text_color='#F5F1DF',
                    disabled_readonly_text_color='#F5F1DF', readonly=True, justification="right"),
                #sg.Text(size=35, enable_events=True, expand_y=True, key='-MINKNOW-',font=artifice_core.consts.CONSOLE_FONT, pad=(0,12), background_color='#393938', text_color='#F5F1DF', justification="Right"),
                AltFolderBrowse(button_text=translator('Select')),
                sg.Sizer(consts.BUTTON_SIZE[0], 0),
            ],
            [                
                sg.Sizer(1,16),
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

    panel = setup_panel(window_functions.translator)

    title = f'RAMPARD{" v" + consts.RAMPART_VERSION if consts.RAMPART_VERSION != None else ""}'

    content = window_functions.setup_content(panel, title=title, 
                                             button_text='Continue', button_key='-CONFIRM-',
                                             bottom_left_button_text='Run Options', bottom_left_button_key='-RUN OPTIONS-')

    layout = window_functions.setup_header_footer(content)

    new_window = sg.Window(title, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           font=consts.DEFAULT_FONT, icon=consts.ICON, 
                           margins=(0,0), element_padding=(0,0))
    new_window.set_min_size(size=(512,320))

    if window != None:
        window.close()

    new_window['-SAMPLES-'].bind("<FocusOut>", "FocusOut")
    new_window['-MINKNOW-'].bind("<FocusOut>", "FocusOut")

    AltButton.intialise_buttons(new_window)

    return new_window

def run_edit_window(window):
    config = consts.retrieve_config()
    run_info = {'title': 'TEMP_RUN'}
    selected_run_title = 'TEMP_RUN'
    docker_client = docker.from_env()


    element_dict = {'-SAMPLES-':'samples',
                    '-MINKNOW-':'basecalledPath'}
    try:
        run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], 
                            update_archive_button=False)
    except:
        pass

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT:
            window.close()
            return

        elif event == '-VIEW SAMPLES-':
            try:
                if '-SAMPLES-' not in values:
                    error_popup("Samples not found in values")

                run_info = artifice_core.parse_columns_window.view_samples(run_info, values, '-SAMPLES-')
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
        elif event == '-CONFIRM-':
            try:
                run_info = save_changes(values, run_info, window, element_dict=element_dict, update_list = False)
                if artifice_core.parse_columns_window.check_spaces(run_info['samples'], 0):
                    alt_popup_ok(translator('Warning: there are spaces in samples'))
                window.close()
                return run_info
            except Exception as err:
                error_popup(err)

    window.close()


