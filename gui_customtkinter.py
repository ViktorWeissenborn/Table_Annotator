import customtkinter as ctk

def generate_table():
    input_text = input_text_field.get("1.0", "end-1c")  # Get the text from the input field
    try:
        # Parse the input text as a list of lists
        data = eval(input_text)
        create_table(data)
    except Exception as e:
        print(f"Error parsing input: {e}")

def cell_clicked(row, col):
    print(f"Cell clicked: Row {row}, Column {col}")  # Replace with your logic (e.g., JSON population)

def create_table(data):
    rows = len(data)
    cols = len(data[0]) if rows > 0 else 0

    for row in range(rows):
        for col in range(cols):
            cell_value = data[row][col]
            cell_button = ctk.CTkButton(master=root, text=cell_value)
            cell_button.grid(row=row, column=col)
            cell_button.configure(command=lambda r=row, c=col: cell_clicked(r, c))

if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Clickable Table Generator")

    # Text field for input
    input_text_field = ctk.CTkTextbox(master=root, height=10, width=40)
    input_text_field.grid(row=0, column=0, padx=10, pady=10)

    # Button to generate the table
    generate_button = ctk.CTkButton(master=root, text="Generate Table", command=generate_table)
    generate_button.grid(row=1, column=0, padx=10, pady=10)

    root.mainloop()