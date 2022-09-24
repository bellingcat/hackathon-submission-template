from distutils.dir_util import copy_tree
from email.policy import default
import json
import os
import pandas as pd
import numpy as np
import time
from datetime import datetime
import PySimpleGUI as sg
import re

import scrape as TANV

global name_of_tool
name_of_tool = 'TANV (Working title)'

menu_txt_font_size = 16
menu_font = 'Arial'
menu_color = 'black'

def main():
    """Main call of py script
    """    
    # call up the gui

    run_gui()

    return

def generate_secondary_window_analysis(project_name_:str= f'{name_of_tool} project', **kwargs):
    return sg.Window(f'{name_of_tool} - Analysis Mode', 
                    generate_secondary_window_analysis_layout(project_name_,**kwargs))

def generate_intro_window(project_name_:str = f'{name_of_tool} project', **kwargs):
    return sg.Window(name_of_tool, 
                    generate_intro_window_layout(project_name_, **kwargs))

def generate_secondary_window_analysis_layout(project_name_ = f'{name_of_tool} project', **kwargs) -> list:
    """Fn declares and returns a list of lists where each sub-list is a row in the PySG Intro GUI menu.
    Returns:
        list: menu layout

    ``` Title:

    Options:
    1. Enter the name of your analysis project
    2. Enter filepath to your user info file
    3. Enter filepath to your edge info file
    5. Run Analysis

    ```

    """    

    font_tuple = (menu_font, menu_txt_font_size)
    intro_row = [sg.Text(f"""To rerun analysis on previous data, follow the steps below:
    """, 
                font=font_tuple )]
                    
    # 1. Enter project name;
    # 2. Select the user information file;
    # 3. Select the edge list file;
    # 4. Click on 'RUN ANALYSIS'.


    close_button_row = [sg.Button('Close', key='CLOSE'),]


    layout = [intro_row,
            get_simple_str_input_w_key("1. Enter the name of your analysis project (for your own record-keeping purposes)", '-PROJECT-NAME-', project_name_, font_tuple, **kwargs),
            get_file_browse_input_w_key('2. Select the user information file:', '-USER-INFO-FILE-', font_tuple),
            get_file_browse_input_w_key('3. Select the edge list file:', '-EDGE-LIST-FILE-', font_tuple),
            [*get_simple_button_w_key("RUN ANALYSIS", "-RUN-ANALYSIS-"), *get_simple_button_w_key('Go back', '-BACK-TO-MAIN-'), *close_button_row],
                    ]

    return layout


def generate_intro_window_layout(project_name_ = f'{name_of_tool} project', **kwargs) -> list:
    """Fn declares and returns a list of lists where each sub-list is a row in the PySG Intro GUI menu.
    Returns:
        list: menu layout

    ``` Title:
    Welcome statement

    Enter Project name: ... 
    Options:
    1. Enter the name of your analysis project (for your own record-keeping purposes)
    2. Enter your Twitter search term:
    3. Enter the maximum recursive depth* you'd like to explore to: 
    4. Enter the maximum number of Tweets you'd like to retrieve:
    5. Run App

    ```

    """    

    font_tuple = (menu_font, menu_txt_font_size)
    intro_row = [sg.Text(f"""Welcome to the {name_of_tool} Tool!
    To get data and analysis for a single query, go to section A.
    To do so for multiple queries, go to section B.
    If you wish to re-run analysis on data you've stored locally, 
    please click on 'RERUN ANALYSIS' to open separate menu.""", 
                font=font_tuple )]


    close_button_row = [sg.Button('Close', key='CLOSE'),]


    layout = [intro_row,
            [sg.Text('A.', font=(menu_font, 20)), sg.HorizontalSeparator(key='sep')],
            get_simple_str_input_w_key("1. Enter the name of your analysis project (for your own record-keeping purposes)", '-PROJECT-NAME-', project_name_, font_tuple, **kwargs),
            get_simple_str_input_w_key("2. Enter your Twitter user to search:", '-TWITTER-SEARCH-USER-', '', font_tuple, **kwargs),
            get_simple_str_input_w_key("3. Enter the maximum recursive depth* you'd like to explore to: ", '-MAX-REC-DEPTH-', 2 , font_tuple, **kwargs),
            get_simple_str_input_w_key("4. Enter the maximum number of Tweets you'd like to retrieve:", "-MAX-N-TWEETS-", 10, font_tuple, **kwargs),
            [sg.Text('B.', font=(menu_font, 20)), sg.HorizontalSeparator(key='sep')],
            get_simple_str_display('If you want to perform multiple searches, select an Excel/CSV file.\nIt *must* have following columns present:\n\nSEARCH_TERM, MAX_DEPTH, MAX_NUMBER_TWEETS\n',), 
            get_file_browse_input_w_key('Select your queries file:', '-PARAMS-FILE-', font_tuple),
            [sg.HorizontalSeparator(key='sep')],
            [*get_simple_button_w_key("RUN TOOL", "-RUN-APP-"), *get_simple_button_w_key('RERUN ANALYSIS', '-RERUN-ANALYSIS-'), *close_button_row],
            # close_button_row,
                    ]
    return layout   

def add_progress_bar_into_layout(layout:list, loc:int=-2, key:str='-PROG-BAR-', max_val:int=100)->list:
    """Adds an empty progress bar to the menu, in the 2nd from last position (Default)

    Args:
        layout (list): current layout
        loc (int, optional): location of progress bar in rows. Defaults to -2.

    Returns:
        layout: list
    """    

    # insert the progress bar itself
    prog_bar = [sg.ProgressBar(max_value=max_val, size=(60, 20), border_width=4, key=key,bar_color=['Green', 'Grey'])]
    layout.insert(loc, prog_bar)

    #add display text
    start_txt = "Initiating Snscrape queries (you may need to click 'RUN APP' again) ..."
    prog_bar_disp = [sg.Text(start_txt, font=(menu_font, menu_txt_font_size), key='-PROG-BAR-DISPLAY-')]
    
    layout.insert(loc-1, prog_bar_disp)
    return layout

def generate_intro_window_w_prog_bar(project_name_, **kwargs):
    """Generates the intro menu window but with a progress bar showing how many queries have been completed

    Args:
        layout (list): _description_
    """    
    layout = generate_intro_window_layout(project_name_, **kwargs)
    layout = add_progress_bar_into_layout(layout)
    return sg.Window(project_name_, layout, finalize=True)


def get_simple_str_input_w_key(input_str:str, key:str, default_txt:str='', font:tuple = (menu_font, menu_txt_font_size), **kwargs)->list:
    if key in kwargs:
        default_txt = kwargs[key]

    return [sg.Text(input_str, font=font), 
                    sg.Input(default_txt, key=key),]


def get_file_browse_input_w_key(disp_str:str, key:str, font:tuple=(menu_font, menu_txt_font_size),)->list:
    return [sg.Text(disp_str, font=font), sg.FileBrowse('Select file', file_types=(('.csv', '.xlsx'),), initial_folder='.', key=key)]


def get_simple_button_w_key(button_label:str, key:str, font:tuple=(menu_font, menu_txt_font_size))->list:
    return [sg.Button(button_label,
                    key=key,
                    font=font,)
                             ]

def run_gui():

    #set the GUI theme
    
    sg.theme('BlueMono')
    project_name_ = f'{name_of_tool} project'
    #init intro window
    current_window = generate_intro_window(project_name_)
    
    while True:

        #read the user inputs

        event, values = current_window.read()

        #get user project name from value entered
        project_name_ = values['-PROJECT-NAME-']

        try:
            # if-elif-else statements that trigger actions
            if event=='-RUN-APP-':

                # check if a file has been selected in section B
                # if it has, then load and iterate over those values
                filepath_selected = values['-PARAMS-FILE-']
                if len(filepath_selected)>0:
                    # if there is an actual filepath, pass it through the error checking function
                    handle_key_error_return = try_out_params_file_cols_and_types(filepath_selected)
                    error_status = handle_key_error_return[0]
                    if error_status==True:
                        error_msg = handle_key_error_return[1]
                        # include a trigger for an erroneous trigger/event/input
                        current_window.close()
                        current_window = generate_post_error_intro_window(project_name_, error_msg, **values)
                        # event, values = current_window.read()
                        continue

                
                    else:
                        # no errors for the file returned
                        # add the progress bar to the menu
                        current_window.close()
                        current_window = generate_intro_window_w_prog_bar(project_name_, **values)
                        event, values = current_window.read()

                        # so pass forward
                        results = []
                        query_df = get_query_df(filepath_selected)
                        for i, row in query_df.iterrows():
                            #  pass each row over to the wrapper_fn for TANV.main()
                            # which should call and store the results, then aggregate them all
                            # results.append(run_network_analysis(row))
                            print(i)
                            time.sleep(1)
                            update_val = 100*(i+1)/len(query_df)
                            text_update = f"Executed {i+1} out of {len(query_df)} queries"
                            current_window['-PROG-BAR-DISPLAY-'].update(text_update)
                            current_window['-PROG-BAR-'].update(update_val)
                            current_window.refresh()


                        # concatenate the results
                        results_df = pd.concat(results, ignore_index=True)

                        # and output them to a useful location

                else:
                    # in the case where they use section A instead and just do a single query
                    #first check the inputs and display an error msg in case any are wrong
                    handle_key_error_return = try_out_kwarg_values_and_types(**values)
                    error_status = handle_key_error_return[0]
                    if error_status==True:
                        error_msg = handle_key_error_return[1]
                        # include a trigger for an erroneous trigger/event/input
                        current_window.close()
                        current_window = generate_post_error_intro_window(project_name_, error_msg, **values)
                        # event, values = current_window.read()
                        continue
                    else:
                        # if no error returned then now do the network analysis
                        print("Running single query ...")
                        run_network_analysis(**values)

            # NOTE: here I am just adding suggestions for other things to implement
            # e.g. if a user wants to run the analysis component again on data that was already stored,
            # especially if a user has multiple data files unmerged in a location
            elif event=='-RERUN-ANALYSIS-':
                
                current_window.close()
                #open the rerun analysis menu
                current_window = generate_secondary_window_analysis(project_name_)
                # event, values = current_window.read()
                continue


            elif event=='-RUN-ANALYSIS-':
                #trigger events for rerunning the analysis component of scrape
                # get the user file and the edge list
                error_status, error_msg = test_filepaths(values['-USER-INFO-FILE-'], values['-USER-INFO-FILE-'])
                if error_status==True:
                    # include a trigger for an erroneous trigger/event/input
                    current_window.close()
                    current_window = generate_post_error_analysis_window(project_name_, error_msg, **values)
                    continue

                fpath_users = values['-USER-INFO-FILE-']
                fpath_users = values['-USER-INFO-FILE-']
                #pass to analysis function

                # rerun_analysis_on_data_stored_locally(**values)
                continue

            # event for going back to main
            elif event=='-BACK-TO-MAIN-':
                current_window.close()
                current_window = generate_intro_window(project_name_)
                continue

            # final event-trigger for closing GUI
            elif event=='Close' or event=='CLOSE' or event==sg.WIN_CLOSED:
                current_window.close()
                break

        except Exception as E:
            error_msg = '\n'.join(['Error in code (please reach out to admin: ', str(E.__class__), str(E.__str__())])
            # raise E
            current_window.close()
            current_window = generate_post_error_intro_window(project_name_, error_msg, **values)
            # event, values = current_window.read()
            continue



    return

def test_filepaths(file_ends:tuple = ('.csv', '.xlsx'), *args):

    for fpath in args:
        error_status, error_msg = check_file_ends(fpath, file_ends)

    return error_status, error_msg

def check_fpath_and_return_error_msg(fpath:str, error_status:bool=False, error_msg:str='')->tuple:
    
    if os.path.exists(fpath)==False:
        error_status=True
        error_msg += f'\n--File could not be found'
        return error_status, error_msg

    return error_status, error_msg

def check_file_ends(fpath:str, file_endings:tuple, error_status:bool=False, error_msg:str='')->tuple:

    for ending in file_endings:
        error_status, error_msg = check_file_ending(fpath, ending, error_status, error_msg)

    return error_status, error_msg

def check_file_ending(fpath:str, ending:str, error_status:bool=False, error_msg:str='')->tuple:

    if fpath.endswith(ending)==False:
        error_status=True
        error_msg += f'\n--Query not of expected file type ({ending}).'
        return error_status, error_msg

    return error_status, error_msg

def try_out_params_file_cols_and_types(filepath:str)->tuple:
    """Function checks the input file of search parameters and 
    1. Checks for file existence
    2. Checks that it is tabular (csv/xlsx) and can be read by pandas
    3. Checks that the correct columns are present
    4. Checks that each row of the table contains usable, correctly specified parameters

    Params:
    filepath - path to table of query params

    Returns:
        tuple: (error status : True if an error has occurred, error_message : blank if no error present)
    """    
    error_status, error_msg = False, 'ERROR : '

    error_status, error_msg = check_fpath_and_return_error_msg(filepath, error_status, error_msg)
    # if os.path.exists(filepath)==False:
    #     error_status=True
    #     error_msg += f'\n--File could not be found'
    #     return error_status, error_msg

    error_status, error_msg = check_file_ends(filepath, ('.csv', '.xlsx'), error_status, error_msg)
    # if (filepath.endswith('csv') or filepath.endswith('xlsx'))==False:
    #     error_status=True
    #     error_msg += f'\n--Query file needs to be either a CSV or XLSX file'
    #     return error_status, error_msg


    try:
        df = get_query_df(filepath)
    except:
        error_status=True
        error_msg += f'\n--File is not readable - it is possibly corrupted'
        return error_status, error_msg


    # check columns

    df_cols = list(df.columns)
    necessary_cols = ['SEARCH_TERM', 'MAX_DEPTH', 'MAX_NUMBER_TWEETS']
    if len(set(df_cols).intersection(set(necessary_cols)))!=len(necessary_cols):
        error_status=True
        missing_cols = [x for x in necessary_cols if x not in df_cols]
        error_msg += f'\n--File is missing the following columns: {missing_cols}'
        return error_status, error_msg

    # at this point we iterate over rows and check for errors:
    row_error_status, row_error_msg = False, ''
    for i, row in df.iterrows():
        #unpack the values
        search = row['SEARCH_TERM']
        max_rec_dep = row['MAX_DEPTH']
        max_n_tweets = row['MAX_NUMBER_TWEETS']

        #get the results for that row
        # print(search, max_rec_dep, max_n_tweets)
        row_status, row_error_msg = try_out_query_params_values_and_types(search, max_rec_dep, max_n_tweets, '')

        if row_status:
            row_error_status = True
            error_msg += f'\nTable row {i} : {row_error_msg}'
            print(i, error_msg)
        else:
            continue

    # if either level of error is True, then set overall to True
    if (error_status==True or row_error_status==True):
        error_status = True
    
    # controlling error msg length
    max_error_msg_len = 300
    if len(error_msg)>max_error_msg_len:
        error_msg = error_msg[:max_error_msg_len-5] + ' ... (error message truncated due to length)' 

    return error_status, error_msg

def get_query_df(fpath:str):

    if fpath.endswith('csv'):
        df = pd.read_csv(fpath)
    elif fpath.endswith('xlsx'):
        df = pd.read_excel(fpath)

    return df


def try_out_kwarg_values_and_types(**kwargs)->tuple:
    """Functions takes the tool input parameters and determines if any of them are incorrect/missing

    Returns:
        tuple: (error_status, error_message)
    """    
    

    #unpack the values
    search = kwargs['-TWITTER-SEARCH-USER-']
    max_rec_dep = kwargs['-MAX-REC-DEPTH-']
    max_n_tweets = kwargs['-MAX-N-TWEETS-']

    return try_out_query_params_values_and_types(search, max_rec_dep, max_n_tweets)

def try_out_query_params_values_and_types(search, max_rec_dep, max_n_tweets, error_msg_start:str='ERROR : ')->tuple:
    
    error_status, error_msg = False, error_msg_start
    
    minimum_search_len = 3

    # now iterate through the inputs and see if an error will be thrown
    try:
        int(max_n_tweets)
    except:
        error_status=True
        error_msg += f'\n--Maximum number of tweets ("{max_n_tweets}") is not a whole number'

    try: 
        int(max_rec_dep)
    except:
        error_status=True
        error_msg += f'\n--Maximum recursion ("{max_rec_dep}") is not a whole number'
    # NOTE: here we should add some 
    if len(search)<minimum_search_len:
        error_status=True
        error_msg+=f'\n--User search term ("{search}") is too short'

    return error_status, error_msg

def generate_post_error_intro_window(project_name_:str = f'{name_of_tool} project', key_error_msg:str='Insufficient/Incorrect type of value entered', **kwargs):
    layout = generate_post_error_intro_window_layout(project_name_, key_error_msg, **kwargs)
    return sg.Window(name_of_tool, layout)

def generate_post_error_intro_window_layout(project_name_:str = f'{name_of_tool} project', key_error_msg:str='Insufficient/Incorrect type of value entered', **kwargs)->list:

    layout = generate_intro_window_layout(project_name_, **kwargs )
    error_msg = get_simple_str_display(key_error_msg, text_colour='red')

    layout.insert(1, error_msg)

    return layout

def get_simple_str_display(disp_str:str, font:tuple=(menu_font, menu_txt_font_size), text_colour = menu_color)->list:
    return [sg.Text(disp_str, font= font, text_color=text_colour)]

def run_network_analysis(**kwargs):    
    """Wrapper function that unpacks the query arguments for a single SnScrape Query and then passes them to the main fn
    of multi_scrape.py
    """    

    # now pass the arguments forward to the TANV tool
    main_user = kwargs['-TWITTER-SEARCH-USER-']
    max_rec_dep = int(kwargs['-MAX-REC-DEPTH-'])
    max_n_tweets = int(kwargs['-MAX-N-TWEETS-'])
    
    project_name = process_filename(kwargs['-PROJECT-NAME-'])
    
    print(f'Search: {main_user}; Depth: {max_rec_dep}, Max tweets: {max_n_tweets}')
    df = TANV.main(main_user, max_rec_dep, max_n_tweets, project_name)

    return df

def process_filename(x:str)->str:
    """Checks a filename for special characters and the like that would cause an error in filesaving and removes them, as well as spaces

    Args:
        x (str): proposed filename

    Returns:
        str: cleaned version
    """    
    x = x.strip()
    x = re.subn(r'[`$&+,:;=?@#|\'<>.^*()%!\-]', '', x)[0]
    x = x.replace(' ', '')

    return x


if __name__=='__main__':
    main()