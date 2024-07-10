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


import customtkinter as ctk
from customtkinter import CTkButton, filedialog, CTkLabel, CTkFrame
import tkinter as tk
from tkinter import ttk, Listbox
import os
import xml.etree.ElementTree as ET
# Selfmade table annotator app
from ctk_annotationWindow import TableWindow
from utils import Utilities
import json


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Hide Window as long as everything is built
        self.withdraw()
        # Set title
        self.title("Table Annotator")
        # Quit window with escape button
        self.bind("<Escape>", self.quick_quit)
        
        self.listbox_frame = ListboxFrame(self)
        self.listbox_frame.grid(row=0, column=0, pady=5, padx=10)

        self.button_frame = CTkFrame(self)
        self.button_frame.grid(row=1, column=0, pady=5, padx=10)

        self.explore = CTkButton(
            self.button_frame, 
            text="Select folder", 
            command=self.listbox_frame.choose_folder
            )
        self.explore.grid(row=0, column=0, pady=10, padx=5)

        self.annotate = CTkButton(
            self.button_frame, 
            text="Annotate Batch",
            command=self.open_table_annotate_window
            )
        self.annotate.grid(row=0, column=1, pady=10, padx=5)
         
        # Bring window to center
        Utilities.center_window(self)
        # Show window when all objects are placed
        self.deiconify()


    def quick_quit(self, event=None):
        """
        Quit application with escape button
        """
        self.quit()

    def open_table_annotate_window(self):
        if self.listbox_frame.tables:
            doc_id = self.listbox_frame.tables["doc_id"]
            tables = self.listbox_frame.tables["tables"]
            if tables:
                table_annotate_window = TableWindow(self.listbox_frame)
                table_annotate_window.focus_set()
            else: # This part was added in case a bioC document does not contain any table
                self.export_empty_annotations(doc_id, tables)
                print("It is possible that this document does not contain any table, but is read correctly. An empty json-annotation file will be created in annotated_tables folder as placeholder.")
            # Refresh after table annotate button was pressed
            Utilities.refresh_processed_docs(self.listbox_frame.document_listbox.listbox)
        else:
            print("Error: Table either not recognised, or no document selected. This error might indicate that no BioC XML folder has been chosen yet via the select folder button.")


    """
    The following functions:
    - write_anno_tab_to_json
    - export_empty_annotations

    and the class
    - OverwritePopUp

    are code duplications from the ctk_annotationWindow. For time reasons those have just been duplicated and customized into this
    .py file since unfortunately they are deeply connected to the other classes in ctk_annotationWindow and thus are harder
    to seperate into seperate files, as it would be needed here. To fix the code duplication some more extensive refactoring 
    of ctk_annotationWindow.py is needed, to detangle class interdependencies a bit.
    """
    def write_anno_tab_to_json(self, file_path, data):
        with open(file_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        print(f"Data has been written to '{file_path}'.")


    def export_empty_annotations(self, doc_id, tables):
        folder_path = "./annotated_tables/"
        filename = doc_id + ".json"
        data = {"doc_id":doc_id, "tables":tables}


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
            OverwritePopUp(self, file_path=file_path, data=data)
        else:
            self.write_anno_tab_to_json(file_path, data)




class OverwritePopUp(ctk.CTkToplevel):
    def __init__(self, parent: MainWindow, file_path=None, data=None):
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
        Utilities.center_window(self, self.parent)
        #Show PopUp when everything is loaded
        self.deiconify()
        self.update()

        # Ensure the window stays on top
        self.keep_on_top()

    def overwrite_file(self, file_path, data):
        self.parent.write_anno_tab_to_json(file_path, data)
        self.destroy()
    
    def keep_on_top(self):
        # Keep the window on top
        self.attributes("-topmost", True)
        self.lift()
        # Repeat after 200 milliseconds
        self.after(200, self.keep_on_top)









class ListboxFrame(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.xml_paths = {}
        #currently selected tables from one document
        self.tables = {}

        xml_examples = ["xml1", "xml2", "xml3"]
        table_examples = ["tab1", "tab2", "tab3"]

        self.label_folder = CTkLabel(self, text="File Browser")
        self.label_folder.grid(row=0, column=0, padx=5)
        self.label_tables = CTkLabel(self, text="Table Browser")
        self.label_tables.grid(row=0, column=1, pady=0, padx=5)
        # Document listbox with xml filenames
        self.document_listbox = ScrollableListbox(
            self,
            elements=xml_examples
        )
        self.document_listbox.listbox.bind("<<ListboxSelect>>", self.doc_listbox_select)
        self.document_listbox.grid(row=1, column=0, pady=10, padx=10)

        # Table listbox with Table names
        self.table_listbox = ScrollableListbox(
            self,
            elements=table_examples)
        self.table_listbox.listbox.bind("<<ListboxSelect>>", self.tab_listbox_select)
        self.table_listbox.grid(row=1, column=1, pady=10, padx=10)

    def tab_listbox_select(self, event=None):
        index = self.table_listbox.listbox.curselection()
        # If statement important because a deselect triggers an empty index
        if index:
            selected_item = self.table_listbox.listbox.get(index)
            print(selected_item)


    def doc_listbox_select(self, event=None):
        index = self.document_listbox.listbox.curselection()
        # If statement important because a deselect triggers an empty index
        if index:
            selected_item = self.document_listbox.listbox.get(index)
            # Catch error when example "XML1" is clicked
            if selected_item in self.xml_paths:
                xml_path = self.xml_paths[selected_item]
                print("Listbox event:", xml_path)

                # Get tables from XML path

                self.tables = self.extract_tables_from_xml(xml_path)
                print(self.tables)

                self.refresh_table_browser()
            else:
                print("KeyError: Filename not in self.xml_paths. This is just an example list, please choose a folder containing BioC XML files first.")
    
    
    
    def extract_tables_from_xml(self, path):

        # Parse BioC XML document
        tree = ET.parse(path)
        root = tree.getroot()

        # ID consists of DOI of publication, each dot is replaced by a underscore
        pub_id: str = root.find(".//id").text
        pub_id_cleaned = pub_id.replace(".", "_").replace("/", "__")
        tables = {"doc_id": pub_id_cleaned, "tables": []}

        for passage in root.findall(".//passage"):
            # Look for passage with section_type TABLE_CAPTION
            section_type = passage.find("./infon[@key='section_type']")
            if section_type is not None and section_type.text == "TABLE_CAPTION":
                # Look for raw_table infon
                raw_table = passage.find("./infon[@key='raw_table']")
                if raw_table is not None:
                    # Extract the table caption
                    caption = passage.find("./text").text.strip()
                    # Extract the raw table data
                    raw_table_data = eval(raw_table.text.strip())
                    # Append table information
                    tables["tables"].append({"caption": caption, "raw_table_data": raw_table_data})
        
        return tables


    def choose_folder(self):
        folder_path = filedialog.askdirectory(initialdir=".")
        if folder_path:
            self.list_files(folder_path)


    def list_files(self, folder_path):
        self.document_listbox.listbox.delete(0, tk.END)
        files: list = os.listdir(folder_path)
        files.sort()
        for file in files:
            if str(file).endswith(".xml"):
                self.document_listbox.listbox.insert(tk.END, file)
                self.xml_paths[file] = os.path.join(folder_path, file)
        Utilities.refresh_processed_docs(self.document_listbox.listbox)
        print(self.xml_paths)


    def refresh_table_browser(self):
        self.table_listbox.listbox.delete(0, tk.END)
        captions = [(f"Table {n+1}:", table["caption"]) for n, table in enumerate(self.tables["tables"])]      
        self.table_listbox.listbox.insert(tk.END, *captions)


class ScrollableListbox(CTkFrame):
    def __init__(self, parent, elements:list=None, **kwargs):
        super().__init__(
            parent,
            border_width=0,
            corner_radius=0,
            **kwargs
        )

        self.v_s = ctk.CTkScrollbar(
            self,
            orientation="vertical",
            fg_color="transparent",
            bg_color="transparent",
            height=180
        )
        self.v_s.grid(row=0, column=1, padx=0, pady=0)
        self.h_s = ctk.CTkScrollbar(
            self, 
            orientation="horizontal",
            fg_color="transparent",
            bg_color="transparent",
            width=190
        )
        self.h_s.grid(row=1, column=0, padx=0, pady=0)
        
        self.listbox = Listbox(
            self, 
            yscrollcommand=self.v_s.set,
            xscrollcommand=self.h_s.set,
            borderwidth=1,
            foreground="#262626"
            )
        for el in elements:
            self.listbox.insert(tk.END, el)
        self.listbox.grid(row=0, column=0, ipadx=0, ipady=0)

        self.v_s.configure(command=self.listbox.yview)
        self.h_s.configure(command=self.listbox.xview)

def refresh_listbox_constantly(root: MainWindow):
    """
    Function makes sure that whenever an annotated table file is deleted,
    the document listbox gets refreshed every second, so an exidental
    skip of a document which is falsely marked as processed will be avoided.
    """
    if root.listbox_frame.document_listbox.listbox.winfo_exists():
        Utilities.refresh_processed_docs(root.listbox_frame.document_listbox.listbox)
        root.after(1000, lambda r=root: refresh_listbox_constantly(r))

if __name__ == "__main__":
    app = MainWindow()
    refresh_listbox_constantly(app)
    app.mainloop()