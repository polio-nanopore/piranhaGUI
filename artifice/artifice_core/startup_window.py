import PySimpleGUI as sg
import docker
import traceback
import os.path
from os import mkdir
from webbrowser import open_new_tab
from PIL import Image
from time import sleep

import artifice_core.start_rampart
import artifice_core.consts
from artifice_core.update_log import log_event, update_log
from artifice_core.options_window import create_options_window, run_options_window
from artifice_core.alt_button import AltButton
from artifice_core.window_functions import error_popup, translate_text, get_translate_scheme, scale_image


#create layout
def setup_layout(theme='Dark', version='ARTIFICE', font = None, scale = 1):
    sg.theme(theme)
    config = artifice_core.consts.retrieve_config()

    translate_scheme = get_translate_scheme()
    try:
        language = config['LANGUAGE']
    except:
        language = 'English'

    is_piranhaGUI = version.startswith('piranhaGUI')

    docker_installed = artifice_core.start_rampart.check_for_docker(popup=False) #check docker is installed
    if docker_installed:
        docker_status = translate_text('Docker installed',language,translate_scheme)
        docker_text_color = '#00bd00' #green
    else:
        docker_status = translate_text('Docker not installed',language,translate_scheme)
        docker_text_color = '#db4325' #red

    got_rampart_image, docker_client = artifice_core.start_rampart.check_for_image(None, artifice_core.consts.RAMPART_IMAGE, font=font, popup=False)

    if got_rampart_image:
        rampart_image_status = translate_text('RAMPART image installed', language, translate_scheme)
        rampart_pull_text = translate_text('Check for updates to RAMPART image', language, translate_scheme)
        rampart_text_color = '#00bd00'
    else:
        rampart_image_status = translate_text('RAMPART image not installed',language,translate_scheme)
        rampart_pull_text = translate_text('Install RAMPART image',language,translate_scheme)
        rampart_text_color = '#db4325' #red

    got_piranha_image, docker_client = artifice_core.start_rampart.check_for_image(docker_client, artifice_core.consts.PIRANHA_IMAGE, font=font, popup=False)

    if got_piranha_image:
        piranha_image_status = translate_text('PIRANHA image installed',language,translate_scheme)
        piranha_pull_text = translate_text('Check for updates to PIRANHA image',language,translate_scheme)
        piranha_text_color = '#00bd00'
    else:
        piranha_image_status = translate_text('PIRANHA image not installed',language,translate_scheme)
        piranha_pull_text = translate_text('Install PIRANHA image',language,translate_scheme)
        piranha_text_color = '#db4325' #red

    # Resize PNG file to appropiate size
    poseqco_scaled = scale_image('poseqco_logo_cropped.png',scale,(150,68))
    if is_piranhaGUI:
        main_logo_scaled = scale_image('piranha.png',scale,(150,150))
        image_info_text = 'An internet connection and a Docker install is required to install RAMPART and PIRANHA images'
    else:
        main_logo_scaled = scale_image('a_logo.png',scale,(100,120))
        image_info_text = 'An internet connection and a Docker install is required to install RAMPART image'

    logo_column = [
        [sg.Image(source = poseqco_scaled, visible=is_piranhaGUI)],
        [sg.Image(source = main_logo_scaled)],
    ]

    install_buttons_size = (480,36)
    info_column = [
    [sg.Text(translate_text(image_info_text,language,translate_scheme))],
    [
    sg.Text(docker_status,size=(30,1),text_color=docker_text_color, key='-DOCKER STATUS-'),
    AltButton(button_text=translate_text('Open Docker Site in Browser',language,translate_scheme),font=font,size=install_buttons_size,key='-DOCKER INSTALL-', visible=not docker_installed),
    ],
    [
    sg.Text(rampart_image_status,size=(30,1),text_color=rampart_text_color,key='-RAMPART IMAGE STATUS-'),
    AltButton(button_text=rampart_pull_text,size=install_buttons_size,font=font,key='-RAMPART INSTALL-'),
    ],

    [
    sg.Text(piranha_image_status,size=(30,1),text_color=piranha_text_color, visible=is_piranhaGUI,key='-PIRANHA IMAGE STATUS-'),
    AltButton(button_text=piranha_pull_text,size=install_buttons_size,font=font, visible=is_piranhaGUI,key='-PIRANHA INSTALL-'),
    ],
    [
    AltButton(button_text=translate_text('Continue',language,translate_scheme),font=font,key='-LAUNCH-'),
    sg.Push(),
    AltButton(button_text=translate_text('Options',language,translate_scheme),font=font,key='-OPTIONS-')
    ],
    ]

    #if is_piranhaGUI:
    logo_bg = sg.LOOK_AND_FEEL_TABLE['Artifice']['INPUT']

    layout = [
        [
        sg.Column(logo_column, visible=is_piranhaGUI),
        sg.Column(info_column),
        ],
    ]
    return layout

def create_startup_window(theme = 'Artifice', version = 'ARTIFICE', font = None, window = None, scale = 1):
    update_log('creating startup window')
    layout = setup_layout(theme=theme, font=font, scale=scale)
    if version == 'piranhaGUI':
        icon_scaled = scale_image('piranha.png',scale,(64,64))
    else:
        icon_scaled = scale_image('placeholder_artifice2.ico',scale,(64,64))
        
    new_window = sg.Window(version, layout, font=font, resizable=False, enable_close_attempted_event=True, finalize=True,use_custom_titlebar=False,icon=icon_scaled)

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

# popup to show user while pulling image
def create_install_popup(name, font):
    sg.theme('Artifice')
    inst_frame = sg.Frame('', [[sg.Text(f'Pulling {name} image...')],],size=(250,50))
    install_popup = sg.Window('', [[inst_frame]], disable_close=True, finalize=True,
                                font=font, resizable=False, no_titlebar=True,)
    install_popup.read(timeout=100)
    return install_popup

def install_image(name, image_tag, window, font, client):
    install_popup = create_install_popup(name, font)
    client.images.pull(image_tag)
    install_popup.close()
    image_status = f'{name} image installed'
    pull_text = f'Check for updates to {name} image'
    text_color = '#00bd00'
    window[f'-{name} INSTALL-'].update(text=pull_text)
    window[f'-{name} IMAGE STATUS-'].update(image_status, text_color=text_color)

def run_startup_window(window, font=None, scale=1, version='ARTIFICE'):
    client = docker.from_env()

    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [main window]')

        if event == 'Exit' or event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or event == '-EXIT-':
            window.close()
            break
            return

        elif event == '-DOCKER INSTALL-':
            try:
                open_new_tab('https://docs.docker.com/get-docker/')
            except Exception as err:
                error_popup(err, font)

        elif event == '-RAMPART INSTALL-':
            try:
                install_image('RAMPART',artifice_core.consts.RAMPART_IMAGE,window,font,client)
            except Exception as err:
                error_popup(err, font)

        elif event == '-PIRANHA INSTALL-':
            try:
                install_image('PIRANHA',artifice_core.consts.PIRANHA_IMAGE,window,font,client)
            except Exception as err:
                error_popup(err, font)

        elif event == '-OPTIONS-':
            try:
                options_window = create_options_window(font=font, scale=scale, version=version)
                run_options_window(options_window, font)
                options_window.close()
                window = create_startup_window(window=window,font=font)
            except Exception as err:
                """
                update_log(traceback.format_exc())
                sg.popup_error(err)
                """
                error_popup(err, font)


        elif event == '-LAUNCH-':
            window.close()
            return False
