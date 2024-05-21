#import required libraries
from tkinter import *
from tkinter import ttk

#Create an instance of Tkinter frame
win= Tk()

#Set the geometry of the window
win.geometry("750x250")

#Create a LabelFrame
frame= Frame(win, width= 400, height= 400, background= "green")
frame.pack(fill=None, expand=False)

#Configure the Frame
frame.place(relx=0.3, rely=.3, anchor= "c")

#Create Button widget in Frame
ttk.Button(frame, text= "Button").pack()

win.mainloop()