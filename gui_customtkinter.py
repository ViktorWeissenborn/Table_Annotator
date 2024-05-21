#TESTGELÄNDE
# [["Name", "Age", "Country"], ["Alice", "25", "USA"], ["Bob", "30", "Canada"], ["Charlie", "22", "UK"]]


import customtkinter as ctk
from customtkinter import CTkButton, CTkFrame, StringVar, CTkLabel, CTkSwitch
import sys

import traceback

"""
Global Vars and constants
"""

entry_count = 1

MASTER =                    "master"
BUTTONS =                   "buttons"
TABLE_GRID_BUTTONS =        "table_grid_buttons"
SELECTED_BUTTONS =          "selected_buttons"
COLLECTED_BUTTONS =         "collected_buttons"
DELETE_BUTTONS =            "delete_buttons"
STUB_HEADER_BUTTONS =       "stub_header_buttons"
COL_HEADER_BUTTONS =        "col_header_buttons"
ROW_HEADER_BUTTONS =        "row_header_buttons"
GRID_BUTTONS =              "grid_buttons"

COLOR_LIGHT_BLUE =          "#3B8ED0"   # color code
COLOR_DARK_BLUE =           "#1F6AA5"   # color code

COLLECT =                   "Collect (Press Enter)"
AUTO_COLLECT =              "auto collect"
EXPORT_JSON =               "export json"   # currently "print JSON"

AUTO_MANUAL_SWITCH =        "auto_manual_switch"
STUB_COL_MENU_BUTTON =       "stub_col_menu_button"

MANUAL =                    "manual"
AUTO =                      "auto"
"""
Global Vars
---------------------------------------------
"""

"""
Attributes
"""
select = "select"
collect = "collect"

"""
Attributes
---------------------------------------------
"""


json_data: dict[CTkButton, str] = {}


"""
Button Trackers
"""

button_tracker: dict[str, CTkFrame|None|dict[str, list]] ={
    MASTER:None, 
    BUTTONS:
    {
        TABLE_GRID_BUTTONS:[],     # all buttons from table grid
        SELECTED_BUTTONS:[],       # buttons that are selected (held down)
        COLLECTED_BUTTONS:[],      # buttons that were collected
        DELETE_BUTTONS:[],         # red buttons to delete a line
        COL_HEADER_BUTTONS:[],     # columns headers
        GRID_BUTTONS:[],           # grid buttons that are not, stub, col, row header or delete button
        STUB_COL_MENU_BUTTON:[]    

    }   
}                                                                          

processing_buttons: dict[str, CTkFrame|None|dict[str, str|None]] = {
    MASTER:None,
    BUTTONS:
    {
        COLLECT:None,
        AUTO_COLLECT:None,
        EXPORT_JSON:None,
    }
} # buttons from the processing frame

stringvars: dict[str, None|StringVar] = {
    AUTO_MANUAL_SWITCH:None,
    STUB_COL_MENU_BUTTON:None
}
"""
Button Trackers
---------------------------------------------
"""



"""
Utilities
"""
def clear_buttons(button_tracker: dict[str, list[str]], key: str):
    button_tracker[key].clear()


def destroy_widgets(button_tracker: dict[str, CTkFrame]):
    if type(button_tracker[MASTER]) == CTkFrame:
        button_tracker[MASTER].destroy()
    button_tracker[MASTER] = None


def handle_error(error_message, custom_error_message=""):
    # Create a new window
    error_window = ctk.CTkToplevel()
    error_window.title(type(error_message).__name__)

    if custom_error_message:
        error_message = custom_error_message

    # Display the error message
    error_label = ctk.CTkLabel(error_window, text=error_message)
    error_label.pack(padx=20, pady=10)

    # Button to close the window
    ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
    ok_button.pack(pady=10)


def configure_grid_button_param(button_name: str, **params: dict[str, any]):
        button_tracker[MASTER].children[button_name].configure(**params)


def create_entry_for_button_list(button_name: str, action):
    if action == select:
        button_tracker[BUTTONS][SELECTED_BUTTONS].append(button_name)
    if action == collect:
        button_tracker[BUTTONS][COLLECTED_BUTTONS].append(button_name)

def delete_last_entry_for_button_list(button_name: str, action):
    if action == select:
        button_tracker[BUTTONS][SELECTED_BUTTONS].remove(button_name)
    if action == collect:
        button_tracker[BUTTONS][COLLECTED_BUTTONS].remove(button_name)


def request_grid_button_param(button_name: str, property: str):
    return button_tracker[MASTER].children[button_name].cget(property)

"""
Utilities
---------------------------------------------
"""

widgets: dict = {}



def show_cursor(event):
    input_text_field.configure(state="normal")


def press_return_event(event):
    collect_button_name = processing_buttons[BUTTONS][COLLECT]
    ctk_collect_button: CTkButton = processing_buttons[MASTER].children[collect_button_name]
    ctk_collect_button.invoke()
    

def collect_button_click():
    global entry_count
    entry_key = f"entry_{entry_count}"
    collected_entities = []

    if button_tracker[BUTTONS][SELECTED_BUTTONS]:
        for selected_button in button_tracker[BUTTONS][SELECTED_BUTTONS]:
            # get text parameter from cell
            cell_text = request_grid_button_param(selected_button, "text")
            # append cell text to entity list
            collected_entities.append(cell_text)
            # After a button was collected the button should be disabled to avoid accidental collection of already collected values
            configure_grid_button_param(selected_button, state="disabled")
            # Add button names to collected buttons
            create_entry_for_button_list(selected_button, action=collect)

        # Create entry in json dict for collected entities
        json_data[entry_key] = collected_entities
        
        # clear all collected buttons to get ready for next collection
        button_tracker[BUTTONS][SELECTED_BUTTONS].clear()

        entry_count += 1
    print("enter pressed")


def grid_button_click(button_name: str):
    if request_grid_button_param(button_name, "fg_color") == COLOR_LIGHT_BLUE:
        configure_grid_button_param(button_name, fg_color=COLOR_DARK_BLUE)
        create_entry_for_button_list(button_name, action=select)
    else:
        configure_grid_button_param(button_name, fg_color=COLOR_LIGHT_BLUE)
        delete_last_entry_for_button_list(button_name, action=select)
    input_text_field.configure(state="disabled")    # Deactivate cursor in textfield so pressing enter doesnt move the cursor
    

def export_json():
    global entry_count
    for button in button_tracker[BUTTONS][COLLECTED_BUTTONS]:
        # Return color to light blue
        configure_grid_button_param(button, state="normal", fg_color=COLOR_LIGHT_BLUE)
    
    print(json_data)
    button_tracker[BUTTONS][COLLECTED_BUTTONS].clear()
    json_data.clear()
    entry_count = 1


def generate_table():
    global button_tracker
    input_text = input_text_field.get("1.0", "end-1c")  # Get the text from the input field
    input_text = '[["Name", "Age", "Country"], ["Alice", "25", "USA"], ["Bob", "30", "Canada"], ["Charlie", "22", "UK"]]'
    # Destroy button widgets and Clear all button lists when table is generated
    destroy_widgets(button_tracker)
    for button_list in button_tracker[BUTTONS].values():
        button_list.clear() # its enough to just clear the names in the dict since destruction of frame destroys all slave widgets
    try:
        # Parse the input text as a list of lists
        data = eval(input_text)
        create_table(data)
    except SyntaxError as e:
        custom_error_message = "Wrong table format. Input table as list of lists."
        handle_error(e, custom_error_message)
    except Exception as e:
        custom_error_message = traceback.print_exc()
        handle_error(e, custom_error_message)
        traceback.print_exc()
        print(f"Error parsing input: {e}")



def cell_clicked(row, col):
    print(f"Cell clicked: Row {row}, Column {col}")  # Replace with your logic (e.g., JSON population)


def height_maximizer(tracker, height):
    if tracker < height:
        tracker = height
    else:
        tracker = tracker
    return tracker


def set_max_height_for_table_grid_buttons(tracker: int):
    for button in button_tracker[BUTTONS][TABLE_GRID_BUTTONS]:
        configure_grid_button_param(button, height=tracker)


def update_button_height_tracker(button: ctk.CTkButton, tracker: int):
    """
    """
    root.update_idletasks()
    current_height = button.winfo_height()
    button_height_tracker = height_maximizer(tracker, current_height)
    return button_height_tracker


def create_button_frame():
    # Create an inner frame for the clickable grid
    button_tracker[MASTER] = ctk.CTkFrame(master=outer_frame, corner_radius=0, bg_color="black", fg_color="#DBDBDB")
    button_tracker[MASTER].grid(row=2, column=0, padx=10, pady=10)


def create_manual_auto_switch():
    # Track state of switch
    stringvars[AUTO_MANUAL_SWITCH] = ctk.StringVar(value=MANUAL)
    # Nested function to change text of switch
    def manual_auto_switcher():
        manual_auto_switch.configure(text=stringvars[AUTO_MANUAL_SWITCH].get())
    # Create switch object
    manual_auto_switch = ctk.CTkSwitch(
        width=0,
        text=stringvars[AUTO_MANUAL_SWITCH].get(),
        master=generator_frame, 
        variable = stringvars[AUTO_MANUAL_SWITCH],
        onvalue=AUTO, 
        offvalue=MANUAL,
        command=manual_auto_switcher
    )
    manual_auto_switch.grid(row=0, column=1, padx=10, pady=10)


def create_processing_frame():
    # Button frame for collect and export button
    processing_buttons[MASTER] = ctk.CTkFrame(master=outer_frame)
    processing_buttons[MASTER].grid(row=4, column=0, padx=10, pady=10)

    # Button to add a list with entries to json_dict
    collect_button = ctk.CTkButton(
        master=processing_buttons[MASTER], 
        text="Collect (Press Enter)", 
        command=collect_button_click
    )
    collect_button.grid(row=0, column=0, padx=10, pady=10)
    root.bind("<Return>", press_return_event)   # Button can be pressed via Return key
    processing_buttons[BUTTONS][COLLECT] = collect_button.winfo_name()

    # Button to generate the JSON file
    auto_collect_button = ctk.CTkButton(
        master=processing_buttons[MASTER], 
        text="auto collect", 
        state="disabled"
    )
    auto_collect_button.grid(row=0, column=1, padx=10, pady=10)
    processing_buttons[BUTTONS][AUTO_COLLECT] = auto_collect_button.winfo_name()

    # Button to generate the JSON file
    print_json_button = ctk.CTkButton(
        master=processing_buttons[MASTER], 
        text="Print JSON", 
        command=export_json
    )
    print_json_button.grid(row=0, column=2, padx=10, pady=10)
    processing_buttons[BUTTONS][EXPORT_JSON] = print_json_button.winfo_name()








"""
BAUSTELLE
---------------------------------------------------------------------
---------------------------------------------------------------------
---------------------------------------------------------------------
"""



def option_menu_switch(stub_flag: bool, menu: ctk.CTkOptionMenu, option: list):
        
    for button_name in button_tracker[BUTTONS][STUB_COL_MENU_BUTTON]:

        if menu.winfo_name() != button_name:
            configure_grid_button_param(button_name, values=option)

    return stub_flag



def create_option_menu(seg_list: list[str], column: int):
    stringvars[STUB_COL_MENU_BUTTON] = ctk.StringVar(value="none")
    stub_flag = False
    options_stub_off = seg_list.copy()
    options_stub_on = ["none", "k", "k_O3"]




    def option_menu_command(current_value):

        nonlocal stub_flag
                

        if current_value == "comp":

            menu.configure(fg_color="#e3c75b")

            stub_flag = option_menu_switch(True, menu, options_stub_on)
                
            print("stub")


        elif current_value in options_stub_on:

            if current_value == "k" or current_value == "k_O3":
                menu.configure(fg_color="#96d4d3")
            elif current_value == "none":
                menu.configure(fg_color="#CFCFCF")

            if stub_flag == True:
                print("entered true")
                stub_flag = option_menu_switch(False, menu, options_stub_off)

            print("col and non rel")



    menu = ctk.CTkOptionMenu(
        master=button_tracker[MASTER], 
        values=seg_list, 
        corner_radius=10, 
        anchor="center", 
        width=85, 
        dynamic_resizing=False,
        fg_color="#CFCFCF",
        text_color="#5C5C5C",
        button_color="#CFCFCF",
        button_hover_color="#949BA1",
        variable=stringvars[STUB_COL_MENU_BUTTON],
        command=option_menu_command)
    menu.grid(row=0, column=column, pady=5)
    button_tracker[BUTTONS][STUB_COL_MENU_BUTTON].append(menu.winfo_name())



"""
---------------------------------------------------------------------
---------------------------------------------------------------------
---------------------------------------------------------------------
BAUSTELLE
"""











def create_table(data):

    # Create frame for table
    create_button_frame()

    # Create frame for processing buttons (collect, auto_collect, JSON export)
    create_processing_frame()

    # Create Manual/Auto switch
    create_manual_auto_switch()

    # Running Parameters
    button_height_tracker = 0   # Tracks pixel height of largest cell
    
    # Get row and column size of table
    rows = len(data)
    cols = len(data[0]) if rows > 0 else 0  # Addition of "1" for tick box

    seg_list = ["none", "comp", "k", "k_O3"]

    # parse through table grid
    for row in range(rows):
        for col in range(cols):
            #create seg button to choose between non important col, stub col or data col
            if row == 0:
                create_option_menu(seg_list, col)

            #create buttons for each cell
            cell_value = data[row][col]
            cell_button = ctk.CTkButton(
                master=button_tracker[MASTER], 
                text=cell_value, 
                corner_radius=0, 
                width=140, 
                border_spacing=0,
                fg_color="#3B8ED0",
                border_width=1,
                border_color="black",
                state="disabled"
            )   # Create button for every cell

            # Organize buttons in grid and create JSON entry when clicked
            cell_button.grid(row=row+1, column=col, padx=0, pady=0)
            button_name = cell_button.winfo_name()
            cell_button.configure(command=lambda b = button_name: grid_button_click(b))

            # Configure line break if words exceed 120 pixels
            if len(str(cell_value)) != 0:
                cell_button._text_label.configure(wraplength=120)

            # Create special design for column headers
            if row == 0:
                cell_button.configure(font=('Arial', 14, 'bold'), fg_color="grey", hover_color="#555555")
            
            # Update button_height_tracker to maximize button height
            button_height_tracker = update_button_height_tracker(cell_button, button_height_tracker) #stores highest height
            
            # Collect all button objects in list to apply tracked max height after loop is over
            button_tracker[BUTTONS][TABLE_GRID_BUTTONS].append(button_name)
    """
        # Delete Button --> delete one collection      
        delete_button = ctk.CTkButton(
            master=button_tracker[MASTER],
            text="X",
            text_color="#FAE3DC",
            font=('Arial', 14, 'bold'),
            width=20,
            height=20,
            corner_radius=8,
            fg_color="#E05B4F",  # White text on red background
            hover_color=("darkred", "darkred"),
        )
        delete_button.grid(row=row+1, column=cols, padx=5, pady=0)
        button_tracker[BUTTONS][DELETE_BUTTONS].append(delete_button)
    """
    # Set highest found height for all grid buttons except delete buttons
    set_max_height_for_table_grid_buttons(button_height_tracker)
    
    # Activate Export JSON button
    configure_grid_button_param(processing_buttons[BUTTONS][EXPORT_JSON], state="normal")
    #print_json_button.configure(state="normal") # Activate button after table is created
    configure_grid_button_param(processing_buttons[BUTTONS][COLLECT], state="normal")
    #collect_button.configure(state="normal")
    input_text_field.configure(state="disabled")


def close_app(event=None):
    root.withdraw()  # Hide the window (if you want to bring it back later)
    root.quit()
    root.destroy()



if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Clickable Table Generator")
    root.bind("<Escape>", close_app)

    # Create an outer frame
    outer_frame = ctk.CTkFrame(master=root)
    outer_frame.pack()

    # Text field for input
    input_text_field = ctk.CTkTextbox(master=outer_frame, width=800)
    input_text_field.grid(row=0, column=0, padx=10, pady=10)
    input_text_field.bind("<Button-1>", show_cursor)

    # Frame for generate and 
    generator_frame = ctk.CTkFrame(master=outer_frame)
    generator_frame.grid(row=1, column=0, padx=10, pady=10)

    # Button to generate the table
    generate_button = ctk.CTkButton(master=generator_frame, text="Generate Table", command=generate_table)
    generate_button.grid(row=0, column=0, padx=10, pady=10)

    root.mainloop()