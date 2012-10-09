from gui import Gui
from tkinter import Tk, E, W, S, N
from control import defaultControl

root=Tk()

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

gui = Gui(defaultControl(), root)
gui.grid(sticky=E+W+S+N)
root.mainloop() 
