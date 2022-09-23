import json
import os
from turtle import color
import pandas as pd
import numpy as np
import time
from datetime import datetime
import PySimpleGUI as sg

import multi_scrape as TANV

global name_of_tool
name_of_tool = 'TANV (Working title)'

menu_txt_font_size = 12
menu_font = 'Arial'
menu_color = 'blue'

def main():
    """Main call of py script
    """    
    # call up the gui

    run_gui()

    return

def generate_intro_window(project_name_:str = f'{name_of_tool} project'):
    return sg.Window(name_of_tool, 
                    generate_intro_window_layout(project_name_))

def generate_intro_window_layout(project_name_ = f'{name_of_tool} project') -> list:
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

    intro_row = [sg.Text(f"""Welcome to the {name_of_tool} Tool\n""", 
                font=(menu_font, menu_txt_font_size) )]


    close_button_row = [sg.Button('Close', key='CLOSE'),]

    layout = [intro_row,
            get_simple_str_input_w_key("1. Enter the name of your analysis project (for your own record-keeping purposes)", '-PROJECT_NAME-', project_name_),
            get_simple_str_input_w_key("2. Enter your Twitter search term:", '-TWITTER-SEARCH-TERM-'),
            get_simple_str_input_w_key("3. Enter the maximum recursive depth* you'd like to explore to: ", '-MAX_REC-DEPTH-'),
            get_simple_str_input_w_key("4. Enter the maximum number of Tweets you'd like to retrieve:", "-MAX-N-TWEETS-"),
            get_simple_button_w_key("5. Run App", "-RUN-APP-"),
            close_button_row,
                    ]
    return layout   

def get_simple_str_input_w_key(input_str:str, key:str, default_txt:str='', font:tuple = (menu_font, menu_txt_font_size))->list:
    return [sg.Text(input_str, font=font), 
                    sg.Input(default_txt, key=key),]


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

        #get user project name
        project_name_ = values['-PROJECT_NAME-']


        # if-elif-else statements that trigger actions
        if event=='-RUN-APP-':
            # do the network analysis
            handle_key_error_return = try_out_kwarg_values_and_types(**values)

            if handle_key_error_return[0]==KeyError:

                # include a trigger for an erroneous trigger/event/input
                current_window.close()
                current_window = generate_post_error_intro_window(project_name_)
                event, values = current_window.read()
            else:
                run_network_analysis(**values)




        # final event-trigger for closing GUI
        elif event=='Close' or event=='CLOSE' or event==sg.WIN_CLOSED:
            current_window.close()
            break


    return

def try_out_kwarg_values_and_types(**kwargs)->tuple:

    return

def generate_post_error_intro_window(project_name_:str = f'{name_of_tool} project', key_error_msg:str='Insufficient/Incorrect type of value entered'):
    layout = generate_post_error_intro_window_layout(project_name_, key_error_msg)
    return sg.Window(name_of_tool, layout)

def generate_post_error_intro_window_layout(project_name_:str = f'{name_of_tool} project', key_error_msg:str='Insufficient/Incorrect type of value entered')->list:

    layout = generate_intro_window_layout(project_name_ )
    error_msg = get_simple_str_display(key_error_msg, text_colour='red')

    layout.insert(1, error_msg)

    return layout

def get_simple_str_display(disp_str:str, font:tuple=(menu_font, menu_txt_font_size), text_colour = menu_color)->list:
    return [sg.Text(disp_str, font= font, text_color=text_colour)]

def run_network_analysis(**kwargs):    
    

    # now pass the arguments forward to the TANV tool

    return


if __name__=='__main__':
    main()