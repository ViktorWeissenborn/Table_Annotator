import tkinter as tk
import json

class TableEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Table Editor")

        # Input area
        self.input_text = tk.Text(self.root, height=10, width=30)
        self.input_text.pack()

        # Display table button
        display_button = tk.Button(self.root, text="Display Table", command=self.display_table)
        display_button.pack()

        # Table display area
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack()

        # Export button
        export_button = tk.Button(self.root, text="Export JSON", command=self.export_json)
        export_button.pack()

        # Initialize table data
        self.table_data = []

    def display_table(self):
        # Clear previous table data
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Get input and create table data
        input_text = self.input_text.get("1.0", tk.END)
        self.table_data = [list(map(str.strip, line.split())) for line in input_text.splitlines()]

        # Display the table
        for i, row in enumerate(self.table_data):
            for j, cell in enumerate(row):
                cell_label = tk.Label(self.table_frame, text=cell, borderwidth=1, relief="solid", padx=10, pady=5)
                cell_label.grid(row=i, column=j)
                cell_label.bind("<Button-1>", lambda event, i=i, j=j: self.on_cell_click(i, j))

    def on_cell_click(self, row, col):
        # You can customize this function to handle the click event
        # For now, let's print the cell coordinates and content
        print(f"Clicked on cell: ({row}, {col}) - Content: {self.table_data[row][col]}")

    def export_json(self):
        # You can customize this function to create a JSON file with the desired information
        # For now, let's print the JSON data
        json_data = {"table_data": self.table_data}
        json_filename = "exported_data.json"
        with open(json_filename, "w") as json_file:
            json.dump(json_data, json_file)

        print(f"JSON exported to {json_filename}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TableEditorApp(root)
    root.mainloop()
