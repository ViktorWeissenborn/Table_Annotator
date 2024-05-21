import tkinter as tk

# Create the main window
root = tk.Tk()
root.geometry("400x400")



# Create the first bottom frame
bottom_frame_1 = tk.Frame(root, bg="red", height=150)
bottom_frame_1.grid(row=1, column=0)

# Create the second bottom frame
bottom_frame_2 = tk.Frame(root, bg="green", height=150)
bottom_frame_2.grid(row=1, column=1)

# Create the top frame
top_frame = tk.Frame(root, bg="blue", height=100)
top_frame.grid(row=0, column=0, columnspan=2)

# Configure row and column weights to make the frames resize properly
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Run the application
root.mainloop()