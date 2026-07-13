import PySimpleGUI as sg
import sys

import artifice_core.consts as consts
import artifice_core.window_functions as window_functions
from artifice_core.language import translator, setup_translator
from artifice_core.alt_button import AltButton, AltFolderBrowse
from artifice_core.update_log import log_event, update_log
from artifice_core.window_functions import error_popup
from artifice_core.manage_runs import save_run, save_changes, load_run


def setup_panel():
    sg.theme("PANEL")

    config = consts.retrieve_config()
    translator = setup_translator()

    tooltips = {
        '-REFERENCE SEQUENCES-':translator('Custom reference sequences file.'),
        '-ANALYSIS MODE-':translator('Specify analysis mode to run. Options: `vp1`. Default: `vp1`'),
        '-MEDAKA MODEL-':translator('Medaka model to run analysis using. Default: AUTO'),
        '-MIN MAP QUALITY-':translator('Minimum mapping quality. Default: 50'),
        '-MIN READ LENGTH-':translator('Minimum read length. Default: 1000'),
        '-MAX READ LENGTH-':translator('Maximum read length. Default: 1300'),
        '-MIN READ DEPTH-':translator('Minimum read depth required for consensus generation.'),
        '-MIN READ PCENT-':translator('Minimum percentage of sample required for consensus generation.'),
        '-PRIMER LENGTH-':translator('Length of primer sequences to trim off start and end of reads. Default: 30'),
        '-PUBLISH DIR-':translator('Output publish directory. Default: `analysis-2022-XX-YY`'),
        '-OUTPUT PREFIX-':translator('Prefix of output directory & report name: Default: `analysis`'),
        '-ALL META-':translator('Parse all fields from input barcode.csv file and include in the output fasta headers. Be aware spaces in metadata will disrupt the record id, so avoid these.'),
        '-DATE STAMP-':translator('Append datestamp to directory name when using <-o/--outdir>. Default: <-o/--outdir> without a datestamp'),
        '-OVERWRITE-':translator('Overwrite output directory. Default: append an incrementing number if <-o/--outdir> already exists'),
        '-VERBOSE-':translator('Print lots of stuff to screen'),
        '-NO TEMP-':translator('Publish all intermediate files for debugging'),
        #'-RUN PHYLO-':translator('Trigger the optional phylogenetics module. Additional dependencies may need to be installed.'),
        #'-SUP SEQS-':translator('Supplementary sequence FASTA file to be incorporated into phylogenetic analysis.'),
        #'-SUP METADATA-':translator('Supplementary metadata file associated with the supplementary sequence FASTA file.'),
        #'-PHYLO METADATA COL-':translator(f'Columns in the barcodes.csv file to annotate the phylogeny with. Default:'), #{consts.VALUE_PHYLO_METADATA_COLUMNS}'),
        #'-SUP METADATA COL-':translator('Supplementary sequence FASTA file to be incorporated into phylogenetic analysis.'),
        #'-SUP METADATA ID COL-':translator('Supplementary sequence FASTA file to be incorporated into phylogenetic analysis.'),
        #'-UPDATE DB-':translator('Supplementary sequence FASTA file to be incorporated into phylogenetic analysis.'),
        
    }

    analysis_options_tab = [
        
        [
            sg.Column([
                [
                sg.Sizer(16,32),
                sg.Text(translator('Analysis Mode:'),justification='right',tooltip=tooltips['-ANALYSIS MODE-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Medaka Model:'),justification='right',tooltip=tooltips['-MEDAKA MODEL-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Minimum Mapping Quality:'),justification='right',tooltip=tooltips['-MIN MAP QUALITY-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Minimum Read Length:'),tooltip=tooltips['-MIN READ LENGTH-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Maximum Read Length:'),tooltip=tooltips['-MAX READ LENGTH-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Minimum Read Depth:'),tooltip=tooltips['-MIN READ DEPTH-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Minimum Read Percentage:'),tooltip=tooltips['-MIN READ PCENT-']),
                ],
                [
                sg.Sizer(16,32),
                sg.Text(translator('Primer Length:'),tooltip=tooltips['-PRIMER LENGTH-']),
                ],
            ], element_justification='right'),
            sg.Column([
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_ANALYSIS_MODE,
                      border_width=1,
                      tooltip=tooltips['-ANALYSIS MODE-'], key='-ANALYSIS MODE-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_DEFAULT_MEDAKA_MODEL,
                      border_width=1,
                      tooltip=tooltips['-MEDAKA MODEL-'], key='-MEDAKA MODEL-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_MIN_MAP_QUALITY, 
                      border_width=1,
                      tooltip=tooltips['-MIN MAP QUALITY-'], key='-MIN MAP QUALITY-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_MIN_READ_LENGTH, 
                      border_width=1,
                      tooltip=tooltips['-MIN READ LENGTH-'], key='-MIN READ LENGTH-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_MAX_READ_LENGTH,
                      border_width=1,
                      tooltip=tooltips['-MAX READ LENGTH-'], key='-MAX READ LENGTH-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_MIN_READS,
                      border_width=1,
                      tooltip=tooltips['-MIN READ DEPTH-'], key='-MIN READ DEPTH-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_MIN_PCENT,
                      border_width=1,
                      tooltip=tooltips['-MIN READ PCENT-'], key='-MIN READ PCENT-',),
                ],
                [
                sg.Sizer(16,32),
                sg.In(size=(25,1), enable_events=True,expand_y=False,default_text=consts.VALUE_PRIMER_LENGTH,
                      border_width=1,
                      tooltip=tooltips['-PRIMER LENGTH-'], key='-PRIMER LENGTH-',),
                ],
            ])
        ]]
    

    output_options_tab = [[            
            sg.Column([[
                    sg.Sizer(16,32),sg.Text(translator('Publish Directory:'),tooltip=tooltips['-PUBLISH DIR-']),
                ],
                [
                    sg.Sizer(16,32),sg.Text(translator('Output Prefix:'),tooltip=tooltips['-OUTPUT PREFIX-']),
                ],
                [
                    sg.Sizer(16,32),
                ],
                [
                    sg.Sizer(16,32),
                ],
                [
                    sg.Sizer(16,32),
                ],
                [
                    sg.Sizer(16,32),
                ], 
            ], element_justification='right'),
            sg.Column([[
                    sg.Sizer(16,32), 
                    sg.In(size=(25,1), enable_events=True,expand_y=False, border_width=1,
                         tooltip=tooltips['-PUBLISH DIR-'], key='-PUBLISH DIR-',),
                ],
                [
                    sg.Sizer(16,32), 
                    sg.In(size=(25,1), enable_events=True,expand_y=False,border_width=1,
                        default_text=consts.VALUE_OUTPUT_PREFIX,tooltip=tooltips['-OUTPUT PREFIX-'], key='-OUTPUT PREFIX-',),
                ],
                [
                    sg.Sizer(16,32), sg.Checkbox(translator('Overwrite Output'), default=False, tooltip=tooltips['-OVERWRITE-'], key='-OVERWRITE-')
                ],
                [
                    sg.Sizer(16,32), sg.Checkbox(translator('Output Intermediate Files'), default=False, tooltip=tooltips['-NO TEMP-'], key='-NO TEMP-')
                ],
                [
                    sg.Sizer(16,32), sg.Checkbox(translator('All Metadata to Header'), default=False, tooltip=tooltips['-ALL META-'], key='-ALL META-')
                ],
                [
                    sg.Sizer(16,32), sg.Checkbox(translator('Date Stamp'), default=False, tooltip=tooltips['-DATE STAMP-'], key='-DATE STAMP-')
                ], 
            ])
        ]]
    
    """
        [
        sg.Text(translate_text('Run Name',language,translate_scheme),size=(14,1)),
        sg.In(size=(25,1), enable_events=True,expand_y=False,tooltip=translate_text('Run name to appear in report. Default: Nanopore sequencing',language,translate_scheme), key='-RUN NAME-',),
        ],
        """
    """
     --orientation ORIENTATION
                        Orientation of barcodes in wells on a 96-well plate. If `well` is supplied as a column in the barcode.csv, this default orientation will be overwritten. Default: `horizontal`. Options: `horizontal` or `vertical`.
  -temp TEMPDIR, --tempdir TEMPDIR
                        Specify where you want the temp stuff to go. Default: `$TMPDIR`
  --no-temp             Output all intermediate files. For development/ debugging purposes

                        """
    
    layout = [
        [sg.TabGroup([
        [
        sg.Tab(translator('Output Options'),output_options_tab,key='-OUTPUT OPTIONS TAB-'),
        sg.Tab(translator('Analysis Options'),analysis_options_tab,key='-ANALYSIS OPTIONS TAB-'),
        ]
            ],expand_x=True, expand_y=True)
        ]
    ]
    
    panel = sg.Frame("", layout, expand_x=True, expand_y=True, border_width=0, relief="solid", pad=(0,16))

    return panel

def create_piranha_options_window(window = None):
    update_log('creating add protocol window')

    panel = setup_panel()

    title = f'Piranha{" v" + consts.PIRANHA_VERSION if consts.PIRANHA_VERSION != None else ""}'

    content = window_functions.setup_content(panel, title=title, small=True, button_text='Continue', button_key='-CONFIRM-')

    layout = window_functions.setup_header_footer(content, small=True)

    new_window = sg.Window(title, layout, resizable=False, enable_close_attempted_event=True, finalize=True,
                           modal=True, # keep_on_top=True, <- commented this out for now, creates issues for tooltips not showing correctly on mac, More info: https://github.com/PySimpleGUI/PySimpleGUI/issues/5952
                           font=consts.DEFAULT_FONT, icon=consts.ICON, margins=(0,0), element_padding=(0,0))

    new_window.set_min_size(size=(512,320))

    if window != None:
        window.close()

    AltButton.intialise_buttons(new_window)

    return new_window

def run_piranha_options_window(window, run_info):
    config = consts.retrieve_config()
    selected_run_title = run_info['title']

    element_dict = {
                    '-ANALYSIS MODE-':'-m',
                    '-MEDAKA MODEL-':'--medaka-model',
                    '-MIN MAP QUALITY-':'-q',
                    '-MIN READ LENGTH-':'-n',
                    '-MAX READ LENGTH-':'-x',
                    '-MIN READ DEPTH-':'-d',
                    '-MIN READ PCENT-':'-p',
                    '-PRIMER LENGTH-':'--primer-length',
                    '-PUBLISH DIR-':'-pub',
                    '-OUTPUT PREFIX-':'-pre',
                    '-ALL META-':'--all-metadata-to-header',
                    '-DATE STAMP-':'--datestamp',
                    '-OVERWRITE-':'--overwrite',
                    '-VERBOSE-':'--verbose',
                    '-NO TEMP-':'--no-temp'}
    run_info = load_run(window, selected_run_title, element_dict, runs_dir = config['RUNS_DIR'], update_archive_button=False, clear_previous=False)
    
    while True:
        event, values = window.read()

        if event != None:
            log_event(f'{event} [piranha options window]')

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
