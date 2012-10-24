from gui import Gui
from time import sleep
from control import defaultControl, Control, Mover
from traceback import print_exc
import socket
from tkinter import Tk, E, W, S, N, Label
from tkinter.font import nametofont

root=Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
try:
    control=defaultControl()
    gui = Gui(control, root)
    gui.grid(sticky=E+W+S+N)
except (OSError, socket.error) as e:
    print_exc()
    root.configure(width=200, height=200)
    root.bind("<Escape>", lambda x: root.quit())
    l=Label(root, text="Нет связи")
    l.grid()
    nametofont(l["font"]).config(size=80)

root.mainloop() 
