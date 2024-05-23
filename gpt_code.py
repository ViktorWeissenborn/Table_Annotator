import tkinter as tk
from tkinter import scrolledtext

# Create the main window
root = tk.Tk()
root.title("Pre-populated Textbox Example")
root.geometry("400x200")

# Create a scrolled text widget
textbox = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)

# Insert some initial text into the textbox
initial_text = "This is some pre-populated text in the textbox."
textbox.insert(tk.INSERT, initial_text)

# Pack the textbox into the window
textbox.pack(padx=10, pady=10)

# Run the application
root.mainloop()