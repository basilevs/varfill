from gui import Gui
from time import sleep
from tkinter import Tk, E, W, S, N
from control import mockControl, Control, Mover

root=Tk()

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

gui = Gui(mockControl(), root)
gui.grid(sticky=E+W+S+N)
root.mainloop() 
