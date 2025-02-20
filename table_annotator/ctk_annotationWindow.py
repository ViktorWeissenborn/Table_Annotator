"""
MIT License

Copyright (c) 2024 Viktor Weißenborn (viktor.kurt.weissenborn@uni-jena.de)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



import tkinter as tk
from tkinter import Event
import customtkinter as ctk
from customtkinter import CTkEntry, CTkCanvas, CTkScrollbar, CTkOptionMenu, CTkTextbox, CTkButton, CTkFrame, StringVar, CTkLabel, CTkSwitch
from tabledataextractor import Table
import traceback
import os
import json
from utils import Utilities
import numpy as np
"""
Hint:
To use this app following things have to be added:
- Create folder with document id as name
- when export button is pressed a table should be added
to the folder with document id + table number = table id
- To make this work the text input has to be altered in a way, 
that it includes document id, caption, and table number
"""


class TableWindow(ctk.CTkToplevel):
    def __init__(self, listbox_instance: CTkFrame):
        super().__init__()
        # Hide Window as long as everything is built
        self.withdraw()
        self.title("Table Annotator")
        self.bind("<Escape>", self.close_app)

        self.listbox_instance = listbox_instance

        # Tables that were given to this top level window by main window
        self.tables_from_main = listbox_instance.tables

        self.table_frame = TableFrame(self)

        self.progress_frame = ProgressFrame(self)

        self.caption_frame = CaptionFrame(self)

        self.generator_frame = GeneratorFrame(self)

        self.header_assign_frame = HeaderAssignFrame(self)
    
        # Show window when all objects are placed
        self.deiconify()
    
    
    def close_app(self, event=None):
        #self.withdraw()  # Hide the window (if you want to bring it back later)
        self.destroy()


class HeaderAssignFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent,
                         width=20,
                         )
        self.grid(row=1, column=0, pady=(0, 10), sticky="nes")

        self.parent = parent

        self.col_row_heads_label = CTkLabel(self, text="Col_Row_heads:", padx=5, pady=5)
        self.col_row_heads_label.grid(row=0, column=0, padx=(5,0), pady=5)

        self.col_row_heads = CTkEntry(self, width=50)
        self.col_row_heads.insert(0, "[c,r]")
        self.col_row_heads.grid(row=0, column=1, pady=5, padx=(0,5))

        self.col_row_assign = CTkButton(self, text="Assign heads", command=self.col_row_assign_func)
        self.col_row_assign.grid(row=1, column=0, columnspan=2)
    
    @property # Use property decorator here to always get updated class attribute from generator frame
    def input_table(self):
        return self.parent.generator_frame.input_table

    def col_row_assign_func(self, transp = False):
        try:
            self.parent.generator_frame.transpose_switch.deselect()
            entry: list = eval(self.col_row_heads.get())
            if len(entry)==2:
                col_head_num = entry[0]
                row_head_num = entry[1]
                # For creating labels the raw input table is used since a table created by TDE can be pre processed
                # In this case it is important to not take the TDE pre processed table
                np_labels = np.array(self.input_table, dtype='object')
                ####print(f"before: {np_labels}")
                np_labels[:] = "Data"
                np_labels[:, :row_head_num] = "RowHeader"
                np_labels[:col_head_num, :] = "ColHeader"
                for x in range(col_head_num):
                    for y in range(row_head_num):
                        np_labels[x, y] = "StubHeader"
                
                ####print(f"after: {np_labels}")
                self.parent.generator_frame.col_row_manual_heads = np_labels.tolist()
                self.parent.generator_frame.generate_table(user=True)

            else:
                print("Eval Error: Make sure to pass correct input format: [col_headers, row_headers].")
        except Exception as e:
            error_message = traceback.format_exc()
            print(error_message)
            print("Eval Error: Make sure to pass correct input format: [col_headers, row_headers].")




class ProgressFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent)
        self.grid(row=1, column=2, pady=(0, 10), sticky="w")

        self.current_table_status = CTkLabel(self)
        self.current_table_status.grid(row=0, column=0)

        self.heading = CTkLabel(self)
        self.heading.grid(row=1, column=0)

        self.progressbar = ctk.CTkProgressBar(self, width=130)
        self.progressbar.grid(row=2, column=0, padx=5, pady=5)
        self.progressbar.set(0)


class CaptionFrame(CTkTextbox):
    def __init__(self, parent: TableWindow):
        super().__init__(parent,
                         width=265,
                         height=74,
                         wrap=ctk.WORD,
                         state="disabled")
    
        self.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="nesw")
    
        #self.heading = CTkLabel(self)
        #self.heading.grid(row=0, column=0, pady=0)
        """
        self.caption = CTkLabel(
            self,  
            wraplength=600, 
            justify="left"
            )
        self.caption.grid(row=1, column=0, pady=5, padx=5)
        """
        self.grid_remove()
    
    def insert_caption(self, heading, caption):
        self.configure(state="normal")
        self.delete("1.0", ctk.END)
        self.insert("1.0", text=heading + " " + caption)
        self.configure(state="disabled")


class TransposeSwitch(CTkSwitch):
    def __init__(self, parent):
        self.switch_var = StringVar(value="off")

        super().__init__(
            master=parent,
            text="Transpose",
            state="disabled",
            command=self.transpose,
            variable=self.switch_var,
            onvalue="on",
            offvalue="off")
        
        self.grid(row=0, column=2, padx=10, pady=10)

        self.parent: GeneratorFrame = parent

        
    def transpose(self):

        # self assigned labels have to be transposed according to user
        manual_labels = self.parent.col_row_manual_heads
        ####print(f"manual_labels: {manual_labels}")
        if manual_labels != None:
            #Change RowHeader and ColHeader
            self.parent.col_row_manual_heads = self.label_transpose(manual_labels)
            user=True
        else:
            user=False

        # Switch var will give on or off value of switch
        switch_var = self.switch_var.get()
        ####print(f"switch_var: {switch_var}")
        if switch_var == "on":
            # Create table transposed
            self.parent.generate_table(transpose=True, user=user)
        elif switch_var == "off":
            self.parent.generate_table(user=user)
        # Disable export button since no column will be selected
        #self.parent.export_button.configure(state="disabled")


    def label_transpose(self, label_table:list[list]):
        #Swap RowHeader and ColHeader and transpose table
        swap_transp_labels = [
                [
                    'RowHeader' if item == 'ColHeader' 
                    else 'ColHeader' if item == 'RowHeader' 
                    else item for item in sublist
                ]
            for sublist in np.array(label_table).T.tolist()
        ]
        return swap_transp_labels


class GeneratorFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent)
        self.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.parent = parent
        self.table_frame = parent.table_frame

        # Current Table Index
        self.i = 0
        # Length of table list --> starts with zero so it can be used as index similar to self.i
        if len(self.parent.tables_from_main["tables"]):
            self.n = len(self.parent.tables_from_main["tables"]) - 1

        # Tracker if table was annotated (True) or not (False) --> each table gets a true or false statement in list
        self.tab_anno_state = [False for _ in range(self.n + 1)]

        # Collected tables (all tables are collected and THEN exported, step by step)
        self.table_collection = [None for _ in range(self.n + 1)]

        self.input_table = None
        # Is table transposed (True) or not (False)
        self.transpose_state = False

        # Holds None of no manual header assignment took place; holds labels vice versa
        self.col_row_manual_heads = None
        
        # Buttons
        self.previous_table = CTkButton(
            self, text="Previous", 
            command=self.generate_button_action,
            state="disabled"
        )
        self.previous_table.grid(row=0, column=0, padx=10, pady=10)

        self.next_table = CTkButton(
            self, text="Next", 
            command=lambda: self.generate_button_action(next=True)
        )
        # Disable next button when only one table is present
        if self.n == 0:
            self.next_table.configure(state="disabled")
        self.next_table.grid(row=0, column=1, padx=10, pady=10)

        self.transpose_switch = TransposeSwitch(self)

        self.collect_button = CTkButton(self, text="Collect", command=self.collect)
        self.collect_button.grid(row=0, column=3, padx=10, pady=10)

        self.export_button = CTkButton(self, text="Export", state="disabled", command=self.export_button_command)
        self.export_button.grid(row=0, column=4, padx=10, pady=10)
        self.parent.bind(
            "<Return>", 
            lambda event, b=self.export_button: Utilities.invoke_button_with_key(event, b)
        )

        # Create first table of list when window is opened.
        self.generate_table()
        self.set_caption()


    def export_annotations(self):
        folder_path = "./annotated_tables/"
        # Document identifier related to doi
        doc_id = self.parent.tables_from_main["doc_id"]
        filename = doc_id + ".json"
        data = {"doc_id":doc_id, "tables":self.table_collection}

        if not os.path.exists(folder_path):
            # Create the folder if it does not exist
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created.")
        else:
            print(f"Folder '{folder_path}' already exists.")
        
        # Construct the full file path
        file_path = os.path.join(folder_path, filename)
        
        # Check if the file already exists in the folder
        if os.path.exists(file_path):
            # Raise a warning if the file already exists
            print(f"The file '{filename}' already exists in the folder '{folder_path}'.")
            OverwritePopUp(self, specifier="file_overwrite", file_path=file_path, data=data)
        else:
            self.write_anno_tab_to_json(file_path, data)


    def write_anno_tab_to_json(self, file_path, data):
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data has been written to '{file_path}'.")


    def refresh_document_listbox_progress(self):
        Utilities.refresh_processed_docs(self.parent.listbox_instance.document_listbox.listbox)


    def export_button_command(self):
        self.export_annotations()
        self.refresh_document_listbox_progress()


    def generate_button_action(self, next=False):
        
        if (next and self.i < self.n) or (not next and self.i > 0):
            if next:
                self.i += 1
            else:
                self.i -= 1
            self.set_caption()
            self.generate_table()
            self.transpose_switch.deselect()
            # Reset manually selected row and col headers
            self.col_row_manual_heads = None
        else:
            print("Can not go back or past further")
        ####print(f"self.i: {self.i}, self.n :{self.n}")
        # Disable prev or next button when end of table list is reached
        if self.i == 0:
            self.previous_table.configure(state="disabled")
        else:
            self.previous_table.configure(state="normal")
        
        if self.i == self.n:
            self.next_table.configure(state="disabled")
        else:
            self.next_table.configure(state="normal")



    # Change (Is Table completed or not? --> change caption_frame to progress_frame)
    def set_caption(self):
        # Set count for tables which have been annotated
        annotated_tables_amount = sum(1 for state in self.tab_anno_state if state)
        #update progress window (bar and label)
        self.parent.progress_frame.heading.configure(text=f"Total: {annotated_tables_amount}/{self.n + 1} Tables")
        self.parent.progress_frame.progressbar.set(int(annotated_tables_amount)/int(self.n + 1))
        # Count Tables according to order from paper and set header in caption frame
        heading = f"Table {self.i + 1}: "
        if self.tab_anno_state[self.i]:
            self.parent.progress_frame.current_table_status.configure(text="Current: Completed")
        else:
            self.parent.progress_frame.current_table_status.configure(text="Current: None") 
        # Get extracted caption and caption in caption frame
        caption = self.parent.tables_from_main["tables"][self.i]["caption"]
        # This function handles the insertion of the caption in a way that the user cant change text via cursor
        self.parent.caption_frame.insert_caption(heading, caption)


    def mips_error_catcher(self, table: list[list]):
        try:
            tab = Table(table)
            return False
        except:
            return True


    def generate_table(self, event=None, transpose=False, user=False):
        # Parse the input text as a list of lists
        try:
            self.transpose_state = False
            # Clear list of table cell buttons
            self.table_frame.init_attributes()
            # Destroy table before creating new one‚
            for child in self.table_frame.winfo_children():
                child.destroy()
            
            #self.input_table = self.parent.table_input_field.get("1.0", "end-1c")
            self.input_table = self.parent.tables_from_main["tables"][self.i]["raw_table_data"]
            mips_error = self.mips_error_catcher(self.input_table)

            #if block to catch MIPS error, so user can define col and row header
            print("\n\nCurrent Table:\n")
            print(f"mips_error: {mips_error}")
            print(f"user: {user}")
            print(f"transpose: {transpose}\n")
            ####print(self.parent.table_frame.labels)
            if mips_error == False and user == False: 

                # Get table from xml selected via ctk_filemenu and create TDE object to pre-clean (delete empty lines and duplicates) table
                tde_table_obj = Table(self.input_table)
                
                # If transpose is activated table will be generated transposed after switch is clicked
                if transpose:
                    self.table_frame.data = tde_table_obj.pre_cleaned_table.transpose().tolist()
                    self.table_frame.labels = Table(self.table_frame.data).labels.tolist()
                    self.transpose_state = True
                else:
                    self.table_frame.data = tde_table_obj.pre_cleaned_table.tolist()
                    # Get label table of each cell in the table as list of lists
                    self.table_frame.labels = tde_table_obj.labels.tolist()
                
            else:
                # Block is called when MIPS failed or user did manual input
                if transpose:
                    self.table_frame.data = np.array(self.input_table).T.tolist()
                    self.transpose_state = True

                else:
                    self.table_frame.data = self.input_table

                if mips_error == False and user == True:
    
                    # When transpose = True col_row_manual_heads (manual labels) are transposed by label_transpose function
                    self.table_frame.labels = self.col_row_manual_heads
                
                else:

                    if self.col_row_manual_heads == None:
                        print("MIPS failed: Col and Row header need to be assigned manually")
                        # Turn all cell labels to "data" so table can be depicted without headers, then user decides which cols and rows are headers
                        all_cells_data: np.ndarray = np.array(self.table_frame.data)
                        all_cells_data[:] = "Data"
                        self.table_frame.labels = all_cells_data.tolist()
                        self.col_row_manual_heads = all_cells_data.tolist()

                    else:
                        self.table_frame.labels = self.col_row_manual_heads


            ####print(self.col_row_manual_heads)
            print(f"table:\n{np.array(self.table_frame.data)}\n")
            print(f"labels:\n{np.array(self.table_frame.labels)}")
            self.table_frame.create_table()
            # Activate transpose switch after table is created
            self.transpose_switch.configure(state="normal")
        except Exception as e:
            error_message = traceback.format_exc()
            ErrorPopUp(e, error_message)
            print(error_message)




    def collect(self):
        if not self.tab_anno_state[self.i]:
            # This variable tells how many top rows are column headers (top down)
            selected_cols = self.table_frame.selected_cols
            # Dict holds fully annotated table data
            entry = {}
            entry["#-cols"] = self.table_frame.cols
            entry["#-rows"] = self.table_frame.rows
            entry["transposed"] = self.transpose_state
            entry["data"] = []
            entry["entities"] = {"headers": {}, "data_points": []}

            for row in self.table_frame.table_cells:

                entry["data"].append([])
                # one data point conssists of at least compound and rate constant
                data_points = entry["entities"]["data_points"]
                data_point = []

                for col in row:
                    # Add cell_data dict of every button to data, which acts as representation of whole annotated table
                    entry["data"][-1].append(col.cell_data)
                    # Define all variables
                    text = col.cell_data["text"]
                    entity_type = col.cell_data["type"]
                    headers = entry["entities"]["headers"]
                    
                    # Check if col_header is true --> is cell col_header?
                    if col.cell_data["col_header"] and entity_type:
                        if entity_type not in headers:
                            headers[entity_type] = []
                        headers[entity_type].append(text)
                    # Check if col_header is false if type has an annotated_table_data --> is cell entity?
                    elif entity_type:
                        data_point.append({entity_type: text})
                
                if data_point:
                    data_points.append(data_point)
            # Add an annotated table as dictionary to table collection in order
            self.table_collection[self.i] = entry
            # Change state of index for currently annotated table to True --> annotated
            self.tab_anno_state[self.i] = True
            # Refresh annotated table counter
            self.set_caption()
            ####print(self.table_collection)
        else:
            OverwritePopUp(self, specifier="tab_overwrite")
            print("Question PopUp: Warning")

        if all(self.tab_anno_state):
            self.parent.generator_frame.export_button.configure(state="normal")
        else:
            self.parent.generator_frame.export_button.configure(state="disabled")
        """
        Data format of Dreams:
       {
        "table_id":"",
        "#-cols": 3,
        "#-rows": 3,
        "data": [
            [
            {
                "col": 0,
                "col-header": false,
                "row": 0,
                "row-header": false,
                "text": "Stub",
                "type": ""  #entity type: "comp", "k", "k_O3", "comp_col_header", "k_col_header", "k_O3_col_header"
            },...
            ]
        ],
        "entities": {"headers":{}, entries:[{"comp":""},{"k":""},{"k_O3":""}]},
        "caption": ""
        }
        """


class OverwritePopUp(ctk.CTkToplevel):
    def __init__(self, parent: GeneratorFrame, specifier, file_path=None, data=None):
        super().__init__(parent)
        # Hide PopUp until its loaded
        self.withdraw()
        self.title("WARNING!")
        Utilities.center_window(self)
        self.parent = parent
        # Avoid interaction with other windows
        self.grab_set()
        # Put window on top of others no matter where you click on screen
        self.attributes("-topmost", True)
        self.update()

        if specifier == "tab_overwrite":
            error_message = "This table has been annotated already. Are you sure you want to overwrite your annotation?"
            overwrite_func = self.overwrite_table
        elif specifier == "file_overwrite":
            error_message = f"The filepath {file_path} already exists. Overwrite?"
            overwrite_func = lambda: self.overwrite_file(file_path, data)

        self.error_label = ctk.CTkLabel(
            self, 
            text=error_message,
            wraplength=300
        )
        self.error_label.pack(padx=20, pady=10)
    
        self.cancel = CTkButton(self, text="Cancel", command=self.destroy)
        self.cancel.pack(side="left", padx=(10, 5), pady=10)

        self.overwrite = CTkButton(self, text="Continue", command=overwrite_func)
        self.overwrite.pack(side="right", padx=(5, 10), pady=10)
        # Center PopUp in MainWindow (parent.parent)
        Utilities.center_window(self, self.parent.parent)
        #Show PopUp when everything is loaded
        self.deiconify()
        self.update()

        # Ensure the window stays on top
        self.keep_on_top()

    def overwrite_file(self, file_path, data):
        self.parent.write_anno_tab_to_json(file_path, data)
        self.destroy()

    def overwrite_table(self):
        # Set table annotation state for index back to False
        index = self.parent.i
        self.parent.tab_anno_state[index] = False
        # Call collect function again to add table annotation to table_collection list
        self.parent.collect()
        self.destroy()
    
    def keep_on_top(self):
        # Keep the window on top
        self.attributes("-topmost", True)
        self.lift()
        # Repeat after 200 milliseconds
        self.after(200, self.keep_on_top)


class ErrorPopUp(ctk.CTkToplevel):
    def __init__(self, error_object, error_message):
        super().__init__()
        self.title(type(error_object).__name__)

        self.error_label = ctk.CTkLabel(self, text=error_message)
        self.error_label.pack(padx=20, pady=10)



class TableCell(CTkButton):
    def __init__(self, text: str, col: int, row: int, col_header: bool = False, row_header: bool = False, **kwargs):
        super().__init__(**kwargs, text=text)

        self.col_header = col_header
        self.row_header = row_header

        self.cell_data = {
                "col": col,
                "col_header": self.col_header,
                "row": row,
                "row_header": self.row_header,
                "text": text,
                "type": ""
            }



class TableFrame(CTkFrame):

    def __init__(self, parent: TableWindow):
        super().__init__(
            parent,
            corner_radius=0,  
            fg_color="#EBEBEB",
            #height=1080,
            #width=1920
        )
        self.grid(row=3, column=0, columnspan=3, padx=10, pady=10)
        self.grid_remove()

        self.parent = parent

        self.PRIMARY = "comp"   # Dependent table entity --> This entity can only be assigned once
        self.SEC1 = "k_total"   # For each dependent table entity one or more of the secondary table entities can be annotated
        self.SEC2 = "k_O3"
        self.SEC3 = "log_k_O3"
        self.SEC4 = "k_OH"
        self.SEC5 = "log_k_OH"
        self.SEC6 = "ref"        # Column with references for rate constants
        self.SEC7 = "pH"
        self.SEC8 = "comp_conc"
        self.SEC9 = "matrix"        # WW characteristics
        self.SEC10 = "TOC"           # WW characteristics
        self.SEC11 = "DOC"           # WW characteristics (Further Chars to add: Alkalinity, UV absorbance, Turbidity, COD (chemical oxygen demand))
        self.SEC12 = "temp"
        self.SEC13 = "conc_O3"
        self.SEC14 = "conc_comp"

        self.init_attributes()

    def init_attributes(self):
        self.data = None
        self.labels = None
        self.rows = None
        self.cols = None
        self.selected_cols = {}
        self.table_cells: list[list[TableCell]] = []
        self.col_type_dd: list[CTkOptionMenu] = []
        self.extraction_length = []
        self.seg_list = ["none", self.PRIMARY, self.SEC1, self.SEC2, self.SEC3, self.SEC4, self.SEC5, self.SEC6, self.SEC7, self.SEC8, self.SEC9, self.SEC10, self.SEC11, self.SEC12, self.SEC13, self.SEC14]
        self.col_header_labels = ["StubHeader", "ColHeader"]
        self.row_header_labels = ["StubHeader", "RowHeader"]
        # "Note" is something like a lose sentence in a table
        self.wrong_labels = ["TableTitle", "Note", "/"]
        self.stub_col = None
        self.canvas = None
        self.button_frame = None

    def create_col_type_menu(self, column):
        menu = CTkOptionMenu(
            master=self.button_frame, 
            values=self.seg_list, 
            corner_radius=10, 
            anchor="center", 
            width=85, 
            dynamic_resizing=False,
            fg_color="#CFCFCF",
            text_color="#5C5C5C",
            button_color="#CFCFCF",
            button_hover_color="#949BA1",
            command=lambda event, c=column:self.col_type_command(event,c))
        menu.grid(row=0, column=column, pady=5) 
        self.col_type_dd.append(menu)

    def col_type_command(self, current_value, column: int):
        comp_off = self.seg_list
        comp_on = ["none", self.PRIMARY, self.SEC1, self.SEC2, self.SEC3, self.SEC4, self.SEC5, self.SEC6, self.SEC7, self.SEC8, self.SEC9, self.SEC10, self.SEC11, self.SEC12, self.SEC13, self.SEC14]
        color_map = {"none": "#CFCFCF", 
                    self.PRIMARY: "#e3c75b",
                    self.SEC1: "#96d4d3", 
                    self.SEC2: "#96d4d3",
                    self.SEC3: "#96d4d3",
                    self.SEC4: "#96d4d3",
                    self.SEC5: "#96d4d3",
                    self.SEC6: "#96d4d3",
                    self.SEC7: "#96d4d3",
                    self.SEC8: "#96d4d3",
                    self.SEC9: "#96d4d3",        # WW characteristics
                    self.SEC10: "#96d4d3",       # WW characteristics 
                    self.SEC11: "#96d4d3",
                    self.SEC12: "#96d4d3",
                    self.SEC13: "#96d4d3",
                    self.SEC14: "#96d4d3"
        }
        if current_value in color_map:
            self.col_type_dd[column].configure(fg_color=color_map[current_value])
            # Activate column
            if current_value != "none":
                for row in self.table_cells:
                    cell = row[column]
                    col_header = cell.cell_data["col_header"]
                    cell.configure(state="normal")

                    cell.cell_data["type"] = current_value

                    if col_header:
                        cell.cell_data["type"] += "_col_header"

                self.selected_cols[column] = current_value
            # Disable column
            else:
                for row in self.table_cells:
                    cell = row[column]
                    cell.configure(state="disabled")

                    cell.cell_data["type"] = ""

                if column in self.selected_cols:
                    del self.selected_cols[column]

        if current_value == self.PRIMARY:
            for index, button in enumerate(self.col_type_dd):
                if index == column:
                    continue
                button.configure(values=comp_on)
            self.stub_col = column
                
        elif self.stub_col == column and current_value != self.PRIMARY:
            for index, button in enumerate(self.col_type_dd):
                if index == column:
                    continue
                button.configure(values=comp_off)
            self.stub_col = None
        

    def set_table_header(self, cell_button: TableCell, row, col):
        col_header = False
        row_header = False
        ####print(f"self.labels : {self.labels}\nrow :{row}; col: {col}")
        if self.labels[row][col] in self.col_header_labels:
            cell_button.configure(fg_color="grey", hover_color="#555555")
            col_header = True
        if self.labels[row][col] in self.row_header_labels:
            if not col_header:
                cell_button.configure(fg_color="#1E8449", hover_color="#145A32")
            row_header = True
        if self.labels[row][col] in self.wrong_labels:
            cell_button.configure(fg_color="#922B21", hover_color="#641E16")
        ####print(f"col_header: {col_header}, row_header: {row_header}")
        cell_button.cell_data["col_header"] = col_header
        cell_button.cell_data["row_header"] = row_header
        return cell_button
    


    def create_scrollbars(self):
        # Below here is canvas scrollbar logic
        WIDTH = 1080
        HEIGHT = 600
        self.canvas = CTkCanvas(self, width=WIDTH, height=HEIGHT)

        # Following two inner functions bind scrolling to all widgets as soon as canvas is entered with mouse
        # Scrolling for all is deactivated when mouse leaves canvas
        def enable_scroll(event: Event):
            # Bind the mouse wheel event to the canvas when the mouse enters
            self.canvas.bind_all("<MouseWheel>", lambda e=event: self.canvas.yview_scroll(e.delta, "units"))
            self.canvas.bind_all("<Shift MouseWheel>", lambda e=event: self.canvas.xview_scroll(e.delta, "units"))

        def disable_scroll():
            # Unbind the mouse wheel event from the canvas when the mouse leaves
            self.canvas.unbind_all("<MouseWheel>")
            self.canvas.unbind_all("<Shift MouseWheel>")

        self.canvas.bind("<Enter>", lambda event: enable_scroll(event))
        self.canvas.bind("<Leave>", lambda event: disable_scroll())
        self.button_frame = CTkFrame(self.canvas)

        self.v_s = CTkScrollbar(
            self, 
            orientation="vertical", 
            command=self.canvas.yview,
            height=HEIGHT
            )

        self.h_s = CTkScrollbar(
            self, 
            minimum_pixel_length=1,
            orientation="horizontal", 
            command=self.canvas.xview,
            width=WIDTH
            )
        self.v_s.grid(row=0, column=1, sticky="ns")
        self.h_s.grid(row=1, column=0, sticky="ew")
        self.canvas.grid(row=0, column=0)
        self.canvas.create_window((0, 0), window=self.button_frame, anchor="nw")
        

    def update_canvas(self):
        # Update the scroll region of the canvas
        
        self.canvas.update_idletasks()
        self.canvas.config(
            scrollregion=self.canvas.bbox("all"), 
            yscrollcommand=self.v_s.set, 
            xscrollcommand=self.h_s.set
            )
        

    def create_table(self):
        # Make table visible with options that were defined before
        self.grid()
        self.parent.caption_frame.grid()

        self.create_scrollbars()

        self.button_height_tracker = 0
        self.rows = len(self.data)
        self.cols = len(self.data[0]) if self.rows > 0 else 0 

        ####print(f"self.rows: {self.rows}\n\n")
        ####print(f"Stored in self.data: {self.data}\nself.rows: {self.rows}\n\n")
        ####print(f"Stored in self.labels : \n{self.labels}\n\n")
        for row in range(self.rows):
            self.table_cells.append([])
            for col in range(self.cols):

                if row == 0:
                    self.create_col_type_menu(col)

                cell_value = self.data[row][col]
                cell_button = TableCell(
                    master=self.button_frame, 
                    text=cell_value, 
                    corner_radius=0, 
                    width=140, 
                    border_spacing=0,
                    fg_color="#3B8ED0",
                    border_width=1,
                    border_color="black",
                    state="disabled",
                    col=col,
                    row=row
                )

                # Change Cell style for column and row headers
                cell_button = self.set_table_header(cell_button, row, col)
                cell_button.grid(row=row+1, column=col, padx=0, pady=0)

                if len(str(cell_value)) != 0:
                    cell_button._text_label.configure(wraplength=120)
                
                self.button_height_equalizer(cell_button)
   
                #Add cell to list of table cells to have access to them later on
                self.table_cells[-1].append(cell_button)

        for row_ in self.table_cells:
            for col_ in row_:
                col_: CTkButton
                col_.configure(height=self.button_height_tracker)

        self.update_canvas()


    def button_height_equalizer(self, button: CTkButton, ):
        self.update_idletasks()
        current_height = button.winfo_height()
        if self.button_height_tracker < current_height:
            self.button_height_tracker = current_height



if __name__ == "__main__":
    TableWindow()