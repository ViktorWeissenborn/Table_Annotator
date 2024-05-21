import customtkinter as ctk
from customtkinter import CTkButton


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Test Window")
        
        # Quit window with escape button


        self.explore = CTkButton(
            self, 
            text="Select folder", 
            command=self.warning
            )
        self.explore.grid(row=0, column=0, pady=10, padx=5)

        self.center_window()
        self.mainloop()

    def warning(self):
        QuestionPopUp()

    def center_window(self):
        self.update_idletasks()
        # Get the window's width and height
        width = self.winfo_width()
        height = self.winfo_height()

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position to center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the position of the window
        self.geometry(f"+{x}+{y}")



class QuestionPopUp(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.title("Warning!")
        self.center_window()

        self.error_label = ctk.CTkLabel(
            self, 
            text="""This table has been annotated already. Are you sure you want to overwrite your annotation?""",
            wraplength=300
        )
        self.error_label.pack(padx=20, pady=10)
    
        self.cancel = CTkButton(self, text="Cancel")
        self.cancel.pack(side="left", padx=(10, 5), pady=10)

        self.overwrite = CTkButton(self, text="Continue")
        self.overwrite.pack(side="right", padx=(5, 10), pady=10)

        self.center_window()
    

    def center_window(self):
        self.update_idletasks()
        # Get the window's width and height
        width = self.winfo_width()
        height = self.winfo_height()

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the position to center the window
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # Set the position of the window
        self.geometry(f"+{x}+{y}")

    
if __name__ == "__main__":
    MainWindow()