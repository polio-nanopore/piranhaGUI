from pydoc import doc
from turtle import update
import PySimpleGUI as sg
import docker
import traceback
import os.path
import sys
import os
import subprocess
import requests
from os import system, mkdir
from webbrowser import open_new_tab
from PIL import Image
from time import sleep
from shutil import unpack_archive

import artifice_core.start_rampart
import artifice_core.consts as consts
import artifice_core.window_functions as window_functions
from artifice_core.language import setup_translator
from artifice_core.update_log import log_event, update_log
from artifice_core.options_window import create_options_window, run_options_window
from basic_window.about_window import create_about_window, run_about_window
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.alt_popup import alt_popup
from artifice_core.window_functions import error_popup
from artifice_core.manage_runs import check_supp_datadir

PASS_TEXT_COLOUR = '#1E707E' #blueish '#00bd00'<-green
FAIL_TEXT_COLOUR = '#FF0000' #'#db4325' #red

def check_installation_required(usesRAMPART = True, usesPiranha = True):
    config = artifice_core.consts.retrieve_config()
    docker_client = None

    docker_installed = artifice_core.start_rampart.check_for_docker(popup=False) #check docker is installed    
    if usesRAMPART:
        got_rampart_image, docker_client, rampart_update_available, rampart_image_status, \
            rampart_pull_text, rampart_text_color, consts.RAMPART_VERSION = \
                set_image_status('RAMPART',consts.RAMPART_IMAGE,check_for_updates=True,docker_client=docker_client)

    if usesPiranha:
        got_piranha_image, docker_client, piranha_update_available, piranha_image_status, \
            piranha_pull_text, piranha_text_color, consts.PIRANHA_VERSION = \
                set_image_status('PIRANHA',consts.PIRANHA_IMAGE,docker_client=docker_client)

    piranha_update = usesPiranha and (not got_piranha_image or piranha_update_available)
    rampart_update = usesRAMPART and (not got_rampart_image or rampart_update_available)
    
    return not docker_installed or piranha_update or rampart_update

def setup_panel(usesRAMPART, usesPiranha):
    translator = setup_translator()
    sg.theme("PANEL")
    config = artifice_core.consts.retrieve_config()
    docker_client = None

    gui_update_available, latest_gui_version = check_for_gui_updates()

    is_piranhaGUI = True

    docker_installed = artifice_core.start_rampart.check_for_docker(popup=False) #check docker is installed
    if docker_installed:
        docker_status = translator('Docker software installed')
        docker_text_color =  PASS_TEXT_COLOUR
    else:
        docker_status = translator('Docker not installed/not running')
        docker_text_color = FAIL_TEXT_COLOUR
    
    if usesRAMPART:
        got_rampart_image, docker_client, rampart_update_available, rampart_image_status, \
            rampart_pull_text, rampart_text_color, consts.RAMPART_VERSION = \
                set_image_status('RAMPART',consts.RAMPART_IMAGE,check_for_updates=True,docker_client=docker_client, docker_installed=docker_installed)

    piranha_image_incompatible = True
    if usesPiranha:
        got_piranha_image, docker_client, piranha_update_available, piranha_image_status, \
            piranha_pull_text, piranha_text_color, consts.PIRANHA_VERSION = \
                set_image_status('PIRANHA',consts.PIRANHA_IMAGE,docker_client=docker_client,docker_installed=docker_installed)
        piranha_image_incompatible =  not check_image_compatible(consts.PIRANHA_VERSION, consts.PIRANHA_IMAGE)

        if not got_piranha_image and docker_installed:
            # attempt to install piranha image from file
            if sys.platform.startswith('win'):
                image_file_path = str(artifice_core.consts.get_datadir() / 'piranha.tar')
            elif sys.platform.startswith('darwin'):
                #image_file_path = str(consts.get_datadir() / 'piranha.tar')
                image_file_path = str(consts.get_resource('./resources/piranha.tar'))
            else:
                image_file_path = '/usr/local/ARTIFICE/piranha.tar'

            # attempt to uncompress in case piranha imahe file is compressed
            #zipped_file = f'{image_file_path}.zip'
            #if os.path.exists(zipped_file): 
            #    unpack_archive(zipped_file, artifice_core.consts.get_datadir())

            #image_file_path = str(artifice_core.consts.get_datadir() / 'piranha.tar')
            
            if os.path.exists(image_file_path):
                update_log(f'loading {image_file_path}')
                try:
                    filepath = str(artifice_core.consts.get_datadir() / artifice_core.consts.LOGFILE)
                    with open(image_file_path, 'rb') as image_file:
                        docker_client.images.load(image_file)
                        os.remove(image_file_path) # delete image file now that we're done with it
                except Exception as err:
                    update_log(traceback.format_exc())
                    update_log('unable to load PIRANHA image from file')
                
                
                got_piranha_image, docker_client, piranha_update_available, piranha_image_status, \
                piranha_pull_text, piranha_text_color, consts.PIRANHA_VERSION = \
                set_image_status('PIRANHA',consts.PIRANHA_IMAGE,docker_client=docker_client,translator=translator)

    got_rampart_image, docker_client, rampart_update_available, rampart_image_status, \
    rampart_pull_text, rampart_text_color, consts.RAMPART_VERSION = \
    set_image_status('RAMPART',consts.RAMPART_IMAGE,check_for_updates=False,docker_client=docker_client,translator=translator, docker_installed=docker_installed)
    
    image_info_text = translator('An internet connection and a Docker install is required to install or update software')

    show_piranha_button = usesPiranha and (not got_piranha_image or piranha_update_available) and not piranha_image_incompatible and docker_installed

    show_rampart_button = usesRAMPART and (not got_rampart_image or rampart_update_available) and docker_installed

    if 'SHOW_RAMPART' in config:
        SHOW_RAMPART = config['SHOW_RAMPART']
    else:
        SHOW_RAMPART = usesRAMPART

        consts.edit_config('SHOW_RAMPART', SHOW_RAMPART)
    
    show_rampart_text = SHOW_RAMPART
    if SHOW_RAMPART == False:
        show_rampart_button = True

    install_buttons_size = (396,32)
    layout = []
    if gui_update_available:
        gui_update_text = f'{consts.APPLICATION_NAME} update available to {latest_gui_version}'
        layout.append([
            sg.Sizer(16,56),
            sg.Column([[
                sg.Text(gui_update_text,text_color=FAIL_TEXT_COLOUR,
                        size=(32,1), font=consts.TITLE_FONT),
                AltButton(button_text=translator('Open Github download page in browser'),key='-GUI DOWNLOADS-', 
                        size=install_buttons_size),
            ]])
        ])
    layout.append([
            sg.Sizer(16,56), 
            sg.Column([[
                sg.Text(docker_status,text_color=docker_text_color, key='-DOCKER STATUS-',
                        size=(32,1), font=consts.TITLE_FONT),
                AltButton(button_text=translator('Open Docker Site in Browser'),key='-DOCKER INSTALL-', 
                        size=install_buttons_size,visible=not docker_installed),
            ],[
                sg.Sizer(32,0), 
                sg.Text(translator('Docker is free software used to install and run the analysis pipelines.'),font=consts.CAPTION_FONT),
            ]])
        ])
    
    if SHOW_RAMPART:
        layout.append([
            sg.Sizer(16,56), 
            sg.Column([[
                sg.Text(rampart_image_status, key='-RAMPART IMAGE STATUS-',
                        size=(50,1), text_color=rampart_text_color,visible=show_rampart_text,font=consts.TITLE_FONT),
                AltButton(button_text=rampart_pull_text,size=install_buttons_size,visible=show_rampart_button,
                          key='-RAMPART INSTALL-'),
            ],[
                sg.Sizer(32,0), 
                sg.Text(translator('RAMPART is optional software used to monitor Nanopore sequencing in real-time.'),font=consts.CAPTION_FONT),
            ]])
            ])
    
    if consts.PHYLO_ENABLED:
        phylo_button_text = 'Disable Phylogenetics module'
    else:
        phylo_button_text = 'Enable Phylogenetics module'
    if usesPiranha:
        layout.append([
            sg.Sizer(16,56), 
            sg.Column([[
                sg.Text(piranha_image_status,key='-PIRANHA IMAGE STATUS-',
                        size=(60,1), text_color=piranha_text_color,visible=is_piranhaGUI,font=consts.TITLE_FONT),
                AltButton(button_text=piranha_pull_text,size=install_buttons_size,visible=show_piranha_button,key='-PIRANHA INSTALL-'),
            ],
            [
                sg.Text(f'Please install the latest {consts.APPLICATION_NAME} version to use it',
                        size=(50,1), text_color=piranha_text_color,visible=piranha_image_incompatible and docker_installed,font=consts.TITLE_FONT), 
            ],[
                sg.Sizer(32,0),
                sg.Text(translator('Piranha is the primary analysis pipeline for the DDNS polio detection platform.'),font=consts.CAPTION_FONT),
            ],
            [sg.Sizer(16,28)],[
            sg.Sizer(16,0),
            AltButton(translator(phylo_button_text),size=(396,32),key='-ENABLE PHYLO-'),
            ],
            [sg.Frame(title='',size=(1150,65), layout=[
            [
                sg.Sizer(16,56),
                sg.Text(translator('Supplementary directory for phylogenetic module:'),
                        size=(42,1),justification='left'),
                sg.In(default_text=consts.PHYLO_DIR, enable_events=True,expand_y=True,font=consts.CONSOLE_FONT, 
                    pad=(0,5), disabled_readonly_background_color='#393938', expand_x=True,
                    disabled_readonly_text_color='#F5F1DF', readonly=True, 
                    tooltip='Path to directory containing supplementary sequence FASTA file and optional metadata to be incorporated into phylogenetic analysis.', 
                    justification="left",  key='-PHYLO DIR-'),
                AltFolderBrowse(button_text=translator('Select')),
                AltButton(button_text=translator('Clear'), key='-CLEAR PHYLO DIR-'),
                sg.Push()
            ],],
            visible=(got_piranha_image and consts.PHYLO_ENABLED),
            key = '-PHYLO FRAME-')]
            ]),
        ])

    layout.append([
        sg.Sizer(0,32), 
        sg.Push(),
        sg.Text(image_info_text, font=(None, 12)),
        sg.Push()]
        )

    return sg.Frame("", layout, border_width=0, relief="solid", expand_x=True, pad=(0,8))

def create_startup_window(usesRAMPART = True, usesPiranha = True, window = None):
    update_log('creating startup window')

    panel = setup_panel(usesRAMPART, usesPiranha)

    if usesPiranha:
        content = window_functions.setup_content(panel, title = consts.WINDOW_TITLE, button_text='Continue', button_key='-LAUNCH-',
                                            top_left_button_text='About', top_left_button_key='-ABOUT-', 
                                            top_right_button_text='Options', top_right_button_key='-OPTIONS-')
    else:
        content = window_functions.setup_content(panel, title = consts.WINDOW_TITLE, button_text='Continue', button_key='-LAUNCH-')

    layout = window_functions.setup_header_footer(content)
        
    new_window = sg.Window(consts.WINDOW_TITLE, layout, resizable=False, enable_close_attempted_event=True, 
                           finalize=True,use_custom_titlebar=False,icon=consts.ICON,font=consts.DEFAULT_FONT,
                           margins=(0,0), element_padding=(0,0))
    new_window.set_min_size(size=(512,380))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

# popup to show user while pulling image
def create_install_popup(name):
    sg.theme('CONTENT')
    inst_frame = sg.Frame('', [[sg.Text(f'Pulling {name} image...')],],size=(250,50))
    install_popup = sg.Window('', [[inst_frame]], disable_close=True, finalize=True,
                                resizable=False, no_titlebar=True,)
    install_popup.read(timeout=100)
    return install_popup

# creates an alternate config file for docker. Used as a workaround for issue #16
def create_alt_docker_config():
    if sys.platform.startswith("darwin"):
        filepath = f"{os.getenv('HOME')}/.docker/config.json"
        with open(filepath, mode='r') as file:
            file_data = file.read()
        replace_data = file_data.replace('credsStore','credStore')

        docker_data_dir = consts.get_datadir() / 'docker'
        try:
            mkdir(docker_data_dir)
        except FileExistsError:
            print('y')

        alt_config_filepath = docker_data_dir / 'config.json'
        update_log('creating alternate fixed Docker config')
        with open(alt_config_filepath, mode='w') as file:
            file.write(replace_data)

# set up image status text and button after checking if image is installed/up to date
def set_image_status(name, image, check_for_updates = True, docker_client = None, translator = None, docker_installed = True):
    if translator == None:
        translator = setup_translator()
    if docker_installed:
        got_image, docker_client = artifice_core.start_rampart.check_for_image(docker_client, image, popup=False)
    else:
        got_image = False
    update_available = False
    latest_version = None
    if got_image:
        if check_for_updates:
            update_available, latest_version = artifice_core.start_rampart.check_for_image_updates(docker_client, image)
        if update_available:
            image_compatible = check_image_compatible(latest_version, image)
            if image_compatible:
                image_status = translator(f'Update available for {name} software to version {latest_version}')
                pull_text = translator(f'Install update to {name} software')
            else:
                image_status = translator(f'Major update available for {name} software to version {latest_version}')
            text_color = FAIL_TEXT_COLOUR
        else:
            image_status = translator(f'{name} software version {latest_version} installed')
            pull_text = translator(f'Check for updates to {name} software')
            text_color = PASS_TEXT_COLOUR
    else:
        image_status = translator(f'{name} software not installed')
        pull_text = translator(f'Install {name} software')
        text_color = FAIL_TEXT_COLOUR

    return got_image, docker_client, update_available, image_status, pull_text, text_color, latest_version

def check_image_compatible(latest_version, image):
    try:
        if image in consts.COMPATIBLE_VERSIONS:
            latest_major_version = '.'.join(str(latest_version).split('.')[0:2])
            compatible_major_version = '.'.join(str(consts.COMPATIBLE_VERSIONS[image]).split('.')[0:2])
            if latest_major_version != compatible_major_version:
                return False
    except:
        pass
    return True

def check_for_gui_updates(owner='polio-nanopore',repo='piranhaGUI'):
    update_available = False
    latest_gui_version = 'v' + consts.PIRANHA_GUI_VERSION
    try:
        api_url =  f'https://api.github.com/repos/{owner}/{repo}/releases'

        response = requests.get(api_url)
        releases = response.json()
        latest_gui_version = releases[0]['tag_name']
        installed_gui_version = 'v' + consts.PIRANHA_GUI_VERSION
        if installed_gui_version != latest_gui_version:
            update_available = True
    except:
        pass
    
    return update_available, latest_gui_version
    

def install_image(name, image_repo, window, client, translator = None):
    if translator == None:
        translator = setup_translator()
    client = docker.from_env()
    install_popup = create_install_popup(name)
    old_images = client.images.list('polionanopore/piranha')

    #remove any old tags
    for image in old_images:
        for tag in image.tags:
            client.images.remove(tag)
    if ":" in image_repo:
        image_tag = image_repo
    else:
        image_tag = f'{image_repo}:latest'
    print(image_tag)
    #client.images.remove
    
    try:
        client.images.pull(image_tag)
    except Exception as err: #docker.credentials.errors.InitializationError as err:
        update_log(err)
        update_log('Probably credential initialisation error (on MacOS), attempting fix...')
        create_alt_docker_config()
        docker_data_dir = consts.get_datadir() / 'docker'
        docker_data_dir = str(docker_data_dir).replace(' ', '\\ ')
        update_log(f'pulling {name} image using alternate config')

        command = ["/usr/local/bin/docker", "--config",docker_data_dir,"pull", image_tag]
        update_log(command)
        ret = subprocess.run(command, shell=False, text=True, capture_output=True)
        update_log(ret.stdout)
        update_log(ret.stderr)

    try:
        client.images.get(image_tag)
    except:
        err_text = translator('Docker was unable to download software')
        raise Exception(err_text)

    image_status = f'{name} software installed'
    image_status = translator(image_status)
    pull_text = f'Check for updates to {name} software'
    pull_text = translator(pull_text)
    text_color = PASS_TEXT_COLOUR
    window[f'-{name} INSTALL-'].update(text=pull_text, visible=False)
    window[f'-{name} IMAGE STATUS-'].update(image_status, text_color=text_color)
    install_popup.close()
        

def run_startup_window(window, translator = None):
    #client = docker.from_env(credstore_env={'credStore':'desktop'})
    #print(client.configs())
    docker_installed = artifice_core.start_rampart.check_for_docker(popup=False) #check docker is installed
    if docker_installed:
        try:
            client = docker.from_env()
        except:
            client = None
    else:
        client = None

    if translator == None:
        translator = setup_translator()

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == '-EXIT-':
            window.close()
            break
            return
        
        elif event == '-GUI DOWNLOADS-':
            try:
                open_new_tab('https://github.com/polio-nanopore/piranhaGUI/releases')
            except Exception as err:
                error_popup(err)

        elif event == '-DOCKER INSTALL-':
            try:
                open_new_tab('https://docs.docker.com/get-docker/')
            except Exception as err:
                error_popup(err)

        elif event == '-RAMPART INSTALL-':
            try:
                install_image('RAMPART', consts.RAMPART_IMAGE,window,client,translator=translator)
                client = docker.from_env()
            except Exception as err:
                error_popup(err)

        elif event == '-PIRANHA INSTALL-':
            try:
                install_image('PIRANHA', consts.PIRANHA_IMAGE,window,client,translator=translator)
                client = docker.from_env()
            except Exception as err:
                error_popup(err)

        elif event == '-ENABLE PHYLO-':
            try:
                if consts.PHYLO_ENABLED:
                    consts.edit_config('PHYLO_ENABLED', False)
                    consts.PHYLO_ENABLED = False
                    window['-ENABLE PHYLO-'].update(text = translator('Enable Phylogenetics module'))
                    window['-PHYLO FRAME-'].update(visible=False)
                else:
                    consts.edit_config('PHYLO_ENABLED', True)
                    consts.PHYLO_ENABLED = True
                    window['-ENABLE PHYLO-'].update(text = translator('Disable Phylogenetics module'))
                    window['-PHYLO FRAME-'].update(visible=True)
            except Exception as err:
                error_popup(err)
        
        elif event == '-CLEAR PHYLO DIR-':
            window['-PHYLO DIR-'].update('')

        elif event == '-ABOUT-':
            try:
                about_window = create_about_window()
                run_about_window(about_window)
                about_window.close()
                window = create_startup_window(window=window)

            except Exception as err:
                """
                update_log(traceback.format_exc())
                sg.popup_error(err)
                """
                error_popup(err)

        elif event == '-OPTIONS-':
            try:
                options_window = create_options_window()
                run_options_window(options_window)
                options_window.close()
                window = create_startup_window(window=window)

                config = consts.retrieve_config()
                try:
                    language = config['LANGUAGE']
                except:
                    language = 'English'

            except Exception as err:
                """
                update_log(traceback.format_exc())
                sg.popup_error(err)
                """
                error_popup(err)


        elif event == '-LAUNCH-':
            try:
                if consts.PHYLO_ENABLED:
                    if len(values['-PHYLO DIR-']):
                        if check_supp_datadir(values['-PHYLO DIR-']):
                            print('checked')
                            consts.edit_config('PHYLO_DIR', values['-PHYLO DIR-'])
                        else:
                            raise Exception(translator('No valid fasta file in supplementary directory for phylogenetic module. You may want to check for non utf-8 special characters'))
                window.close()
                return False
            except Exception as err:
                error_popup(err)
            
