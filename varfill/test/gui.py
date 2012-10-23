import unittest
from tkinter import Tk, E, W, S, N
from gui import Gui
from control import mockControl

class GuiTest(unittest.TestCase):
    @staticmethod
    def create():
        root=Tk()        
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        gui = Gui(mockControl(), root)
        gui.grid(sticky=E+W+S+N)
        return (root, gui)
    def withRoot(self, test):
        root, gui = GuiTest.create()
        try:
            test(root, gui)
            gui.after(2, gui.nametowidget("mainMenu.quit").invoke)
            root.mainloop()
        finally:
            root.destroy()
        
    def test_quit(self):
        def t(root, gui):
            pass
        self.withRoot(t)
    def test_startQuit(self):
        def t(root, gui):
            gui.nametowidget("program.bottom.start").invoke()
        self.withRoot(t)
    def test_upDown(self):
        def t(root, gui):
            gui.nametowidget("motor.up").invoke()
            gui.nametowidget("motor.down").invoke()
            gui.nametowidget("motor.down").invoke()
        self.withRoot(t)
        
        
if __name__ == '__main__':
    unittest.main()
