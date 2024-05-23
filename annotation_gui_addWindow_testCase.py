import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkCanvas, CTkScrollbar, CTkScrollableFrame, IntVar, CTkOptionMenu, CTkTextbox, CTkButton, CTkFrame, StringVar, CTkLabel, CTkSwitch
from tabledataextractor import Table
import traceback
from tkinter import scrolledtext
"""
Hint:
To use this app following things have to be added:
- Create folder with document id as name
- when export button is pressed a table should be added
to the folder with document id + table number = table id
- To make this work the text input has to be altered in a way, 
that it includes document id, caption, and table number
"""
class Utilities:

    @staticmethod
    def invoke_button_with_key(event: tk.Event, button: CTkButton):
        print(event.__dict__)
        button.invoke()
    
    @staticmethod
    def center_window(object: ctk.CTkToplevel, parent: None|ctk.CTkToplevel =None):
        object.update_idletasks()

        # Get the window's width and height
        width = object.winfo_width()
        height = object.winfo_height()

        # Get the screen width and height
        screen_width = object.winfo_screenwidth()
        screen_height = object.winfo_screenheight()

        # Calculate the position to center the window
        if parent:
            # Get Parent coordinates
            parent_x_coord = parent.winfo_rootx()
            parent_y_coord = parent.winfo_rooty()
            # Get the width and height of the parent window
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            # Calculate the position to center the window
            x = parent_x_coord + parent_width // 2 - width // 2
            y = parent_y_coord + parent_height // 2 - height // 2
        else:
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2

        # Set the position of the window
        object.geometry(f"+{x}+{y}")
        


class TableWindow(ctk.CTk):
    def __init__(self, tables):
        super().__init__()
        # Hide Window as long as everything is built
        self.withdraw()
        self.title("Table Annotator")
        self.bind("<Escape>", self.close_app)

        # Tables that were given to this top level window by main window
        self.tables_from_main = tables

        self.table_frame = TableFrame(self)

        self.progress_frame = ProgressFrame(self)

        self.caption_frame = CaptionFrame(self)

        self.generator_frame = GeneratorFrame(self)
    
        # Show window when all objects are placed
        self.deiconify()
    
    
    def close_app(self, event=None):
        #self.withdraw()  # Hide the window (if you want to bring it back later)
        self.destroy()


class ProgressFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent)
        self.grid(row=1, column=1, pady=(0, 10), sticky="w")

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
                         width=625,
                         height=74,
                         wrap=ctk.WORD,
                         state="disabled")
    
        self.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="e")
    
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
        # Switch var will give on or off value of switch
        switch_var = self.switch_var.get()
        if switch_var == "on":
            # Create table transposed
            self.parent.generate_table(transpose=True)
        elif switch_var == "off":
            self.parent.generate_table()
        # Disable export button since no column will be selected
        self.parent.export_button.configure(state="disabled")



class GeneratorFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent)
        self.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.parent = parent
        self.table_frame = parent.table_frame

        # Current Table Index
        self.i = 0
        # Length of table list
        self.n = len(self.parent.tables_from_main["tables"]) - 1
        # Tracker if table was annotated (True) or not (False) --> each table gets a true or false statement in list
        self.tab_anno_state = [False for _ in range(self.n + 1)]
        print("This command has been executedThis command has been executedThis command has been executedThis command has been executedThis command has been executedThis command has been executedThis command has been executed")

        # Collected tables (all tables are collected and THEN exported, step by step)
        self.table_collection = [None for _ in range(self.n + 1)]

        self.input_table = None
        # Is table transposed (True) or not (False)
        self.transpose_state = False
        
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
        self.next_table.grid(row=0, column=1, padx=10, pady=10)

        self.transpose_switch = TransposeSwitch(self)

        self.collect_button = CTkButton(self, text="Collect", command=self.collect)
        self.collect_button.grid(row=0, column=3, padx=10, pady=10)

        self.export_button = CTkButton(self, text="Export", state="disabled")
        self.export_button.grid(row=0, column=4, padx=10, pady=10)
        self.parent.bind(
            "<Return>", 
            lambda event, b=self.export_button: Utilities.invoke_button_with_key(event, b)
        )

        # Create first table of list when window is opened.
        self.generate_table()
        self.set_caption()


    def generate_button_action(self, next=False):
        if (next and self.i < self.n) or (not next and self.i > 0):
            if next:
                self.i += 1
            else:
                self.i -= 1
            self.set_caption()
            self.generate_table()
            self.transpose_switch.deselect()
        else:
            print("Can not go back or past further")

        # Disable prev or next button when end of table list is reached
        if self.i == 0:
            self.previous_table.configure(state="disabled")
        elif self.i == self.n:
            self.next_table.configure(state="disabled")
        else:
            self.previous_table.configure(state="normal")
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


    def generate_table(self, event=None, transpose=False):
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

            # Get table from xml selected via ctk_filemenu and create TDE object to pre-clean (delete empty lines and duplicates) table
            tde_table_obj = Table(self.input_table)
            self.table_frame.data = tde_table_obj.pre_cleaned_table.tolist()
            # If transpose is activated table will be generated transposed after switch is clicked
            if transpose:
                self.table_frame.data = tde_table_obj.raw_table.transpose().tolist()
                self.transpose_state = True

        
            # Get label table of each cell in the table as list of lists
            self.table_frame.labels = tde_table_obj.labels
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
            print(self.table_collection)
        else:
            OverwritePopUp(self)
            print("Question PopUp: Warning")

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
    def __init__(self, parent: GeneratorFrame):
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

        self.error_label = ctk.CTkLabel(
            self, 
            text="This table has been annotated already. Are you sure you want to overwrite your annotation?",
            wraplength=300
        )
        self.error_label.pack(padx=20, pady=10)
    
        self.cancel = CTkButton(self, text="Cancel", command=self.destroy)
        self.cancel.pack(side="left", padx=(10, 5), pady=10)

        self.overwrite = CTkButton(self, text="Continue", command=self.overwrite_table)
        self.overwrite.pack(side="right", padx=(5, 10), pady=10)
        # Center PopUp in MainWindow (parent.parent)
        Utilities.center_window(self, self.parent.parent)
        #Show PopUp when everything is loaded
        self.deiconify()


    def overwrite_table(self):
        # Set table annotation state for index back to False
        index = self.parent.i
        self.parent.tab_anno_state[index] = False
        # Call collect function again to add table annotation to table_collection list
        self.parent.collect()
        self.destroy()


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
        self.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.grid_remove()
        self.parent = parent
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
        self.seg_list = ["none", "comp", "k", "k_O3"]
        self.col_header_labels = ["StubHeader", "ColHeader", "TableTitle"]
        # "Note" is something like a lose sentence in a table
        self.row_header_labels = ["StubHeader", "RowHeader", "TableTitle", "Note"]
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
        comp_on = ["none", "k", "k_O3"]
        color_map = {"k": "#96d4d3", 
                     "none": "#CFCFCF", 
                     "comp": "#e3c75b", 
                     "k_O3": "#96d4d3"
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

        if current_value == "comp":
            for index, button in enumerate(self.col_type_dd):
                if index == column:
                    continue
                button.configure(values=comp_on)
            self.stub_col = column
                
   
        elif self.stub_col == column and current_value != "comp":
            for index, button in enumerate(self.col_type_dd):
                if index == column:
                    continue
                button.configure(values=comp_off)
            self.stub_col = None

        if "comp" in self.selected_cols.values() and set(comp_on) & set(self.selected_cols.values()):
            self.parent.generator_frame.export_button.configure(state="normal")
        else:
            self.parent.generator_frame.export_button.configure(state="disabled")

        print(self.selected_cols)
        for x in self.table_cells:
            for y in x:
                print(y.cell_data)
        

    def set_table_header(self, cell_button: TableCell, row, col):
        col_header = False
        row_header = False
        if self.labels[row][col] in self.col_header_labels:
            col_header = True
        if self.labels[row][col] in self.row_header_labels:
            row_header = True
        if col_header:
            cell_button.configure(fg_color="grey", hover_color="#555555")
        cell_button.cell_data["col_header"] = col_header
        cell_button.cell_data["row_header"] = row_header
        return cell_button


    def create_scrollbars(self):
        # Below here is canvas scrollbar logic
        WIDTH = 1080
        HEIGHT = 600
        self.canvas = CTkCanvas(self, width=WIDTH, height=HEIGHT)
        self.canvas.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(event.delta, "units"))
        self.canvas.bind("<Shift MouseWheel>", lambda event: self.canvas.xview_scroll(event.delta, "units"))
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
    tables = {'doc_id': '10_1016__j_chemosphere_2011_08_043', 'tables': [{'caption': 'Fragrance compounds used for ozonation experiments and oxidation by-products.', 'raw_table_data': [['Name', 'Acronym', 'Structure', 'CAS'], ['Galaxolide', 'HHCB', '', '1222-05-5'], ['Tonalide', 'AHTN', '', '1506-02-1'], ['Musk ketone', 'MK', '', '81-14-1'], ['Musk xylene', 'MX', '', '81-15-2'], ['Iso E super', 'OTNE (main constituent)', '', '54464-57-2'], ['', '', '', ''], ['HHCB oxidation by-product', 'HHCB-Lactone', '', '507442-53-7'], ['', '', '', ''], ['Suggested AHTN oxidation by-product', '', '', '']]}, {'caption': 'Non-identified ozonation by-products of AHTN and OTNE listed with their retention times (Rt) and mass spectra.', 'raw_table_data': [['By-product', 'Rt', 'Mass spectrum (relative abundance)'], ['AHTN O1', '13.78', '124 (100), 125 (81), 83 (57), 208 (41), 126 (39)'], ['AHTN O2', '13.87', '163 (100), 83 (86), 154 (81), 70 (81), 135 (72)'], ['AHTN O3', '15.57', '193 (100), 137 (80), 208 (71), 121 (52), 91 (46)'], ['AHTN O4', '15.64', '193 (100), 137 (50), 208 (43), 121 (37), 107 (33)'], ['AHTN O5', '17.32', '223 (100), 177 (43), 192 (41), 149 (38), 224 (27)'], ['AHTN O6', '17.39', '163 (100), 135 (63), 137 (61), 206 (59), 150 (40)'], ['AHTN O7', '17.44', '163 (100), 135 (58), 177 (35), 137 (32), 91 (31)'], ['AHTN O8', '18.94', '243 (100), 258 (27), 159 (24), 187 (18), 244 (17)'], ['AHTN O9', '19.41', '219 (100), 221 (55), 193 (38), 247 (37), 208 (33)'], ['AHTN O10', '19.92', '247 (100), 205 (87), 163 (82), 178 (65), 69 (63)'], ['AHTN O11', '21.18', '205 (100), 247 (26), 206 (21), 220 (21), 163 (21)'], ['AHTN O12', '21.53', '229 (100), 272 (51), 173 (41), 239 (36), 187 (29)'], ['', '', ''], ['AHTN derivative', 'AHTN derivative', '229 (100), 272 (64), 187 (36), 173 (29)'], ['OTNE O1', '17.50', '151 (100), 109 (68), 95 (67), 69 (64), 123 (50)'], ['OTNE O2', '17.75', '119 (100), 175 (79), 95 (59), 105 (52), 190 (44)'], ['OTNE O3', '17.93', '119 (100), 112 (78), 97 (56), 69 (55), 95 (48)'], ['OTNE O4', '18.13', '95 (100), 69 (96), 119 (93), 123 (88), 109 (86)'], ['OTNE O5', '18.37', '119 (100), 95 (77), 189 (62), 69 (60), 207 (59)'], ['OTNE O6', '19.25', '111 (100), 69 (45), 126 (41), 55 (30), 110 (28)'], ['OTNE O7', '20.06', '69 (100), 55 (41), 109 (34), 155 (32), 83 (31)'], ['OTNE O8', '20.39', '69 (100), 81 (97), 168 (92), 125 (75), 83 (72)']]}, {'caption': 'Empirical estimated second order rate constants k concerning the ozonation of fragrance compounds in waste water and the corresponding half-life’s t1/2 having ozone concentrations of 2 mg L−1 and 5 mg L−1.', 'raw_table_data': [['Compound', 'k (M−1\ns−1)', 't1/2 (at 2 mg O3\nL−1) (min)', 't1/2 (at 5 mg O3\nL−1) (min)'], ['OTNE', '94', '4.3', '1.7'], ['HHCB', '67', '6', '2.4'], ['AHTN', '10', '40', '16'], ['HHCB-Lactone', '3', '133', '53']]}]}
    app = TableWindow(tables)
    app.mainloop()