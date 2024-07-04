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

import os
import tkinter as tk
from tkinter import Listbox
import customtkinter as ctk
from customtkinter import CTkButton


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
    

    @staticmethod
    def refresh_processed_docs(xml_listbox: Listbox):
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