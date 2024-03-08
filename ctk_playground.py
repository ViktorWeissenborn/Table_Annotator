import customtkinter
import json

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

app = customtkinter.CTk()  # create CTk window like you do with the Tk window
app.geometry("800x480")

def button_function():
    example_json = {
        "table_data": 
        [
            ["Name", "Age", "Country"], 
            ["Alice", "25", "USA"], 
            ["Bob", "30", "Canada"], 
            ["Charlie", "22", "UK"]
        ]
    }
    dumped = json.dumps(example_json)
    with open("./json_example.json", "w") as f:
        f.write(dumped)
    print("Exported json.")

# Use CTkButton instead of tkinter Button
button = customtkinter.CTkButton(master=app, text="CTkButton", command=button_function)
button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

def main():
    app.mainloop()


if __name__ == "__main__":
    main()