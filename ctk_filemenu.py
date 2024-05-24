import customtkinter as ctk
from customtkinter import CTkButton, filedialog, CTkLabel, CTkFrame
import tkinter as tk
from tkinter import ttk, Listbox
import os
import xml.etree.ElementTree as ET
# Selfmade table annotator app
from annotation_gui_addWindow import TableWindow
from utils import Utilities


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
            table_annotate_window = TableWindow(self.listbox_frame)
            table_annotate_window.focus_set()
        else:
            print("Error: Table either not recognised, no tables found, or no document selected.")













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
                print("KeyError: Filename not in self.xml_paths")
    
    
    
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
        files = os.listdir(folder_path)
        for file in files:
            if str(file).endswith(".xml"):
                self.document_listbox.listbox.insert(tk.END, file)
                self.xml_paths[file] = os.path.join(folder_path, file)
        self.refresh_processed_docs(self.document_listbox.listbox)
        print(self.xml_paths)


    def refresh_table_browser(self):
        self.table_listbox.listbox.delete(0, tk.END)
        captions = [(f"Table {n+1}:", table["caption"]) for n, table in enumerate(self.tables["tables"])]      
        self.table_listbox.listbox.insert(tk.END, *captions)
    

    def refresh_processed_docs(self, xml_listbox: Listbox):
        xml_listbox = self.document_listbox.listbox
        anno_tab_dir = "./annotated_tables/"

        if os.path.exists(anno_tab_dir):
            files = [os.path.splitext(fname)[0] for fname in os.listdir(anno_tab_dir)]
            num_items = xml_listbox.size()
            # Get rid of filextension (.xml) and "_bioc" string in filename for comparison
            all_items = []

            for i in range(num_items):
                # Get rid of file extension
                fname: str = os.path.splitext(xml_listbox.get(i))[0]
                # Get rid of bioc filename ending if present
                if fname.endswith("_bioc"):
                    fname = fname.replace("_bioc", "")
                all_items.append(fname)

            for index, item in enumerate(all_items):
                if item in files:
                    # Change color of processed items to green
                    xml_listbox.itemconfig(index, {'bg': 'lightgreen'})
                    xml_listbox.update()



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


if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()