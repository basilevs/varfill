from gui import Gui
from time import sleep
from tkinter import Tk, E, W, S, N
from control import defaultControl, Control, Mover

root=Tk()

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

control = Control()

class MoverMock(Mover):
    def setSpeed(self, speed):
        print("Speed",speed)
    def start(self):
        print("Mover start")
    def stop(self):
        print("Mover stop")
        
control.mover = MoverMock()
def pump1(value):
    sleep(0.5)
    print("Pump1: "+str(value))
def pump2(value):
    sleep(0.5)
    print("Pump2: "+str(value))
    
control.pumps=[pump1, pump2]

gui = Gui(control, root)
gui.grid(sticky=E+W+S+N)
root.mainloop() 
