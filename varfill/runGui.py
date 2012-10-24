from gui import Gui
from time import sleep
from tkinter import Tk, E, W, S, N, Label
from control import defaultControl, Control, Mover
from traceback import print_exc

root=Tk()

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

try:
    gui = Gui(defaultControl(), root)
    gui.grid(sticky=E+W+S+N)
except OSError as e:
    print_exc()
    root.configure(width=200, height=200)
    Label(root, text="Нет связи").grid()
root.mainloop() 
