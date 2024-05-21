import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkCanvas, CTkScrollbar, CTkScrollableFrame, IntVar, CTkOptionMenu, CTkTextbox, CTkButton, CTkFrame, StringVar, CTkLabel, CTkSwitch
from tabledataextractor import Table
import traceback

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
        


class TableWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Table Annotator")
        self.bind("<Escape>", self.close_app)

        self.table_input_field = TableInputField(self)

        self.table_frame = TableFrame(self)

        self.generator_frame = GeneratorFrame(self)

        self.caption_frame = CaptionFrame(self)

        self.mainloop()
    
    
    def close_app(self, event=None):
        self.withdraw()  # Hide the window (if you want to bring it back later)
        self.quit()
        self.destroy()


class CaptionFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent)

        self.grid(row=2, column=0)
        caption_example = """Machine learning is having a substantial effect on many areas of technology and science; examples of recent applied success stories include robotics and autonomous vehicle control (top left), speech processing and natural language processing (top right), neuroscience research (middle), and applications in computer vision (bottom). [The middle panel is adapted from (29). The images in the bottom panel are from the ImageNet database; object recognition annotation is by R. Girshick.]"""
        
        self.heading = CTkLabel(self, text="Caption").grid(row=0, column=0, pady=0)
        self.caption = CTkLabel(
            self, 
            text=caption_example, 
            wraplength=800, 
            justify="left"
            ).grid(row=1, column=0, pady=5, padx=5)
        
        self.grid_remove()


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
        
        self.grid(row=0, column=1, padx=10, pady=10)

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



class TableInputField(CTkTextbox):
    def __init__(self, parent):
        super().__init__(master=parent, width=800)
        self.grid(row=0, column=0, padx=10, pady=10)
        self.bind("<Button-1>", self.show_cursor)

    def show_cursor(self, event):
        self.configure(state="normal")




class GeneratorFrame(CTkFrame):
    def __init__(self, parent: TableWindow):
        super().__init__(parent)
        self.grid(row=1, column=0, padx=10, pady=10)
        
        self.parent = parent
        self.table_frame = parent.table_frame

        self.input_text = None
        # Is table transposed (True) or not (False)
        self.transpose_state = False
        
        self.generate_table_button = CTkButton(
            self, text="Generate Table", 
            command=self.generate_button_action
        )
        self.generate_table_button.grid(row=0, column=0, padx=10, pady=10)

        self.transpose_switch = TransposeSwitch(self)

        self.export_button = CTkButton(self, text="Collect and Export (Enter)", command=self.export, state="disabled")
        self.export_button.grid(row=0, column=2, padx=10, pady=10)
        self.parent.bind(
            "<Return>", 
            lambda event, b=self.export_button: Utilities.invoke_button_with_key(event, b)
        )


    def generate_button_action(self):
        self.generate_table()
        self.transpose_switch.deselect()

    def generate_table(self, event=None, transpose=False):
        # Parse the input text as a list of lists
        try:
            self.transpose_state = False
            # Clear list of table cell buttons
            self.table_frame.init_attributes()
            # Destroy table before creating new one‚
            for child in self.table_frame.winfo_children():
                child.destroy()
            
            self.input_text = self.parent.table_input_field.get("1.0", "end-1c")
            #self.input_text = """[['No.', '', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33'], ['Molecule', '', 'm-Trihydroxybenzene', 'Isatin', '2-Nitrophenol', '1,10-Phenanthroline monohydrate', 'Nitrobenzene', '2,4-Dichlorophenol', 'Phenol', '3,4-Dichloroaniline', 'o-Chlorophenol', 'Aniline', 'o-Cresol', '5-Chloro-2-methylbenzylamine', 'o-Nitroaniline', '2-Nitroso-1-naphthol', 'Orange G', 'p-Aminobenzene sulfonic acid', 'p-Phthalic acid', 'Chromotropic acid', 'm-Cresol purple', 'Metanil yellow', 'Bromophenol blue', 'Cresol red', 'Eriochrome blue black R', 'p-Dimethylaminobenzaldehyde', 'Methyl orange', 'Fuchsin basic', 'Methylene blue trihydrate', 'Azure I', 'Crystal violet', 'Methyl red', 'Rhodamine B', 'Bromocresol green', 'Indigo'], ['CAS no.', '', '6099-90-7', '91-56-5', '88-75-5', '5144-89-8', '98-95-3', '120-83-2', '108-95-2', '95-76-1', '95-57-8', '62-53-3', '95-48-7', '27917-13-1', '88-74-4', '132-53-6', '1934-20-9', '121-57-3', '100-21-0', '148-25-4', '62625-31-4', '4005-68-9', '115-39-9', '1733-12-6', '2538-85-4', '100-10-7', '547-58-0', '569-61-9', '7220-79-3', '531-53-3', '548-62-9', '493-52-7', '81-88-9', '76-60-8', '482-89-3'], ['Exp.', '', '−3.912', '−2.333', '−1.833', '−1.585', '−1.580', '−1.542', '−1.519', '−1.492', '−1.423', '−1.363', '−0.986', '−0.715', '−0.574', '−0.555', '−0.378', '−0.345', '−0.079', '−0.079', '0.049', '0.573', '0.665', '0.691', '0.696', '0.714', '0.739', '0.822', '0.907', '0.994', '1.062', '1.077', '1.234', '1.836', '2.428'], ['1', 'Pred.', '−1.862', '−1.580', '−1.250', '−0.026', '−0.685', '−1.392', '−2.051', '−1.297', '−1.721', '−1.721', '−1.533', '−1.062', '−0.215', '0.115', '0.350', '−0.780', '0.680', '0.021', '0.303', '0.962', '0.445', '−1.533', '0.774', '−1.533', '1.151', '0.303', '1.245', '1.386', '0.539', '0.492', '0.021', '0.303', '0.868'], ['1', 'Diff.', '2.050', '0.753', '0.583', '1.558', '0.894', '0.150', '−0.532', '0.194', '−0.298', '−0.358', '−0.547', '−0.347', '0.360', '0.670', '0.729', '−0.434', '0.759', '0.100', '0.254', '0.389', '−0.220', '−2.223', '0.078', '−2.247', '0.412', '−0.519', '0.338', '0.392', '−0.523', '−0.585', '−1.213', '−1.533', '−1.560'], ['2', 'Pred.', '−1.658', '−1.880', '−1.549', '−0.331', '−1.161', '−1.721', '−2.246', '−1.506', '−2.072', '−1.987', '−0.735', '−1.223', '−0.467', '−0.310', '0.153', '−0.793', '0.583', '−0.522', '0.969', '0.731', '0.224', '−0.676', '0.611', '−1.514', '1.053', '1.171', '1.409', '1.326', '0.734', '0.581', '0.846', '1.194', '0.663'], ['2', 'Diff.', '2.254', '0.453', '0.284', '1.253', '0.419', '−0.179', '−0.727', '−0.014', '−0.649', '−0.624', '0.251', '−0.508', '0.107', '0.246', '0.532', '−0.448', '0.662', '−0.443', '0.920', '0.158', '−0.440', '−1.367', '−0.084', '−2.228', '0.314', '0.349', '0.503', '0.332', '−0.327', '−0.496', '−0.388', '−0.642', '−1.765'], ['3', 'Pred.', '−2.945', '−1.790', '−2.507', '−0.266', '−1.142', '−1.445', '−2.315', '−1.362', '−2.008', '−1.845', '−0.534', '−0.692', '−0.435', '−0.489', '0.022', '−0.781', '0.513', '−0.759', '0.925', '0.633', '1.409', '−0.473', '0.251', '−0.452', '1.069', '1.401', '1.180', '1.118', '0.417', '0.329', '0.412', '1.348', '0.854'], ['3', 'Diff.', '0.967', '0.543', '−0.674', '1.319', '0.438', '0.097', '−0.796', '0.129', '−0.585', '−0.482', '0.453', '0.024', '0.140', '0.066', '0.400', '−0.436', '0.592', '−0.680', '0.877', '0.059', '0.744', '−1.164', '−0.444', '−1.166', '0.330', '0.578', '0.274', '0.124', '−0.645', '−0.748', '−0.822', '−0.488', '−1.574'], ['4', 'Pred.', '−2.905', '−2.379', '−2.997', '−0.367', '−1.620', '−1.176', '−2.121', '−1.286', '−1.864', '−1.055', '−0.829', '−0.963', '−0.103', '−0.598', '−0.266', '−0.342', '0.553', '−0.515', '0.622', '0.522', '1.423', '0.064', '0.092', '−0.757', '1.335', '1.390', '1.392', '1.357', '0.230', '0.168', '−0.188', '1.193', '1.063'], ['4', 'Diff.', '1.007', '−0.046', '−1.164', '1.218', '−0.040', '0.366', '−0.602', '0.205', '−0.441', '0.308', '0.157', '−0.247', '0.472', '−0.043', '0.112', '0.003', '0.632', '−0.436', '0.573', '−0.051', '0.759', '−0.626', '−0.604', '−1.471', '0.596', '0.568', '0.486', '0.363', '−0.831', '−0.909', '−1.422', '−0.643', '−1.365']]"""
            
            # Get table from text field as list of lists
            self.table_frame.data = eval(self.input_text)
            # If transpose is activated table will be generated transposed after switch is clicked
            if transpose:
                self.table_frame.data = Table(self.table_frame.data).raw_table.transpose().tolist()
                self.transpose_state = True

        
            # Get label table of each cell in the table as list of lists
            self.table_frame.labels = Table(self.table_frame.data).labels
            self.table_frame.create_table()
            # Activate transpose switch after table is created
            self.transpose_switch.configure(state="normal")
        except Exception as e:
            error_message = traceback.format_exc()
            ErrorPopUp(e, error_message)
            print(error_message)


    def export(self):
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
        print(entry)

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
        self.grid(row=3, column=0, padx=10, pady=10)
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
        self.col_header_labels = ["StubHeader", "ColHeader"]
        self.row_header_labels = ["StubHeader", "RowHeader"]
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
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(event.delta, "units"))
        self.canvas.bind_all("<Shift MouseWheel>", lambda event: self.canvas.xview_scroll(event.delta, "units"))
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
     TableWindow()