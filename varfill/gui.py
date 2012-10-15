from tkinter import Frame, Button, Entry, StringVar, Canvas, E, W, BOTH, N, S, LAST, NORMAL, DISABLED, Tk
from threading import Thread
from queue import Queue
import unittest
from control import mockControl

class Axis(object):
    def __init__(self, start=0, end = 100, size = 100, direction = 1, margin = 10):
        self.start = start
        self.end = end
        self.size = size
        self.direction = direction
        self.margin = margin
    def __shift__(self):
        if self.direction > 0:
            return self.margin
        else:
            return self.size - self.margin 
    def validate(self):
        assert(self.end - self.start > 0)
        assert(self.size > 0)
        assert(self.direction in (1,-1))
        assert(self.margin > 0)
    def toExternal(self, x):
        self.validate()
        clientSize =self.size - 2*self.margin
        if clientSize < 0:
            return 0        
        scale = clientSize / float(self.end - self.start) * self.direction
        return x*scale + self.__shift__()
    def generateMarks(self):
        self.validate()
        step = 10
        while  int(self.end - self.start)/step > 10:
            step *= 10
        x =  self.start - (self.start % step)
        while  x < self.end-1:
            x += step 
            yield (x, self.toExternal(x))

class GraphCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.graphs=[]
        self.x=Axis()
        self.y=Axis()
        self.y.direction=-1
        self.bind("<Configure>", lambda ev: self.after_idle(self.__onConfigure__))        
    def drawLine(self, x1, y1, x2, y2, **kwargs):
        y1 = self.y.toExternal(y1)
        coord = (self.x.toExternal(x1), y1,
                 self.x.toExternal(x2), self.y.toExternal(y2))
        self.create_line(*coord, **kwargs)
    def clear(self):
        for i in self.find_all():
            self.delete(i)
        self.__drawAxises__()
    def update(self):
        self.clear()
        for g in self.graphs:
            g.draw()
    def __onConfigure__(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w in [-1, 1]:
            return
        if h in [-1, 1]:
            return
        self.x.size = w
        self.y.size = h        
        self.update()       
    def __drawAxises__(self):
        y0 = self.y.toExternal(0)
        y1 = self.y.toExternal(self.y.end) 
        x0 = self.x.toExternal(0)
        x1 = self.x.toExternal(self.x.end)
        self.create_line(x0, y0, x1, y0, width = 2, arrow=LAST)
        self.create_line(x0, y0, x0, y1, width = 2, arrow=LAST)
        for t,m in self.x.generateMarks():
            self.create_line(m, y0, m, y0-4, width=3)
            self.create_text(m, y0-10, text=str(t))
        for t,m in self.y.generateMarks():
            self.create_line(x0, m, x0+4, m, width=3)
            self.create_text(x0+15, m, text=str(t))
        
class Graph(object):
    def __init__(self, canvas):
        assert(isinstance(canvas, Canvas))
        self.points = []
        self.pointToDraw = 0
        canvas.graphs.append(self)
        self.canvas = canvas
    def draw(self):
        prev = None
        self.pointToDraw = len(self.points)
        for p in self.points:
            if prev:
                self.__drawStep__(prev, p)
            prev = p
    @staticmethod 
    def __checkPoint__(point):
        assert(len(point)==2)
        assert(isinstance(point[0], float))
        assert(isinstance(point[1], float))
    def __drawStep__(self, prevPoint, currentPoint):
        Graph.__checkPoint__(prevPoint)
        Graph.__checkPoint__(currentPoint)  
        self.canvas.drawLine(prevPoint[0], prevPoint[1], currentPoint[0], prevPoint[1])
        self.canvas.drawLine(currentPoint[0], prevPoint[1], currentPoint[0], currentPoint[1])    
    def addPoint(self, x, y):
        self.points.append((float(x),float(y)))
        if len(self.points)>=2:
            self.__drawStep__(*self.points[-2:])

class ShcheduleOnce(object):
    def __init__(self, action, scheduler):
        self.action = action
        self.scheduled = None
        self.updateScheduler = scheduler
    def __runWithCancel__(self):
        try:
            self.action()
        finally:
            self.scheduled = None
    def schedule(self):
        if self.scheduled:
            self.updateScheduler.after_cancel(self.scheduled)
        self.scheduled = self.updateScheduler.after_idle(self.__runWithCancel__)

def run_repeating(widget, predicate, delay = 1000):
    def torun():
        if predicate():
            return
        widget.after(delay, torun)
    torun()
    
        
class Gui(Frame):
    def __init__(self, control, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.queue = Queue()
        self.control = control
        self.columnconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.disabledWhileRunning = []
        self.createWidgets()
        self.control.stepCallback = self.__addPoint__
        self.thread=None
                
    def compileFormulae(self):
        rv = []
        for f in self.formulae:
            body = "def formula5480750923(x):\n  return "+f.get()
            l = {}
            try:
                exec(body, {}, l)
            except:
                rv.append(None)
                continue
            compiled = l["formula5480750923"]
            compiled(0)
            rv.append(compiled)
        return rv
    def plotFormulae(self):
        try:
            compiled = self.compileFormulae()
        except:
            return
        for g in self.graphs:
            g.points=[]
        for x in range(self.canvas.x.start, self.canvas.x.end):        
            point = []
            for c in range(len(compiled)):
                v = None
                if compiled[c]:
                    v = compiled[c](x)
                point.append(v)
            self.__addPoint__(x, point)
        self.canvas.update()
    def __start__(self):
        time = float(self.canvas.x.end - self.canvas.x.start)        
        pumps = self.compileFormulae()
        def calcPumpValues(time):
            return list(map(lambda x: x(time), pumps))
        def thFunc():
            try:
                for g in self.graphs:
                    g.points=[]
                self.control.executeProgram(time, 200, calcPumpValues)
            finally:
                self.invoke(self.__enableControls__)
        self.__disableControls__()
        self.canvas.clear()
        self.thread = Thread(target=thFunc, name="Control")
        self.thread.start()
    def __enableControls__(self):
        for e in self.disabledWhileRunning:
            e.config(state = NORMAL)
    def __disableControls__(self):
        for e in self.disabledWhileRunning:
            e.config(state = "disabled")
    def __addPoint__(self, x, values):
        def c():
            for i in range(len(self.canvas.graphs)):
                self.canvas.graphs[i].addPoint(x, values[i])
        self.invoke(c)    
    def invoke(self, callable):
        self.after_idle(callable)
        
    def __stop__(self):
        self.control.stop()
    def __quit__(self):
        self.__stop__()
        def quitting():
            if self.thread and self.thread.is_alive():
                print("Thread is active")
                return False
            self.quit()
            return True
        run_repeating(self, quitting)
        
    def createWidgets(self):
        columns=3
        startButton = Button (self, name='start', text='Старт', command=self.__start__)
        startButton.grid(row=0,column=0)
        self.disabledWhileRunning.append(startButton)         
        Button (self, text='Стоп', command=self.__stop__).grid(row=0,column=1)         
        Button (self, name='quit', text='Выход', command=self.__quit__).grid(row=0,column=2)
        self.formulae=list(map(lambda t: StringVar(self, t), ["x/7.14+4","20-x/7.14"]))
        self.pumpEntries=[]
        for f in self.formulae:
            e = Entry(self, textvariable=f)
            e.grid(sticky=E+W, columnspan=columns)
            self.disabledWhileRunning.append(e)
            self.pumpEntries.append(e)
            f.trace("w", lambda *x: self.after_idle(self.plotFormulae))

        self.canvas = GraphCanvas(self)
        self.graphs = (Graph(self.canvas), Graph(self.canvas))
        
        self.canvas.x.end=100
        self.canvas.y.end=24
        self.plotFormulae()
        self.canvas.grid(sticky=E+W+S+N, columnspan=columns)


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
        finally:
            root.destroy()
        
    def test_quit(self):
        def t(root, gui):
            gui.invoke(gui.nametowidget("quit").invoke)
            root.mainloop()
        self.withRoot(t)
    def test_startQuit(self):
        def t(root, gui):
            gui.nametowidget("start").invoke()
            gui.nametowidget("quit").invoke()
            root.mainloop()
        self.withRoot(t)
        
if __name__ == '__main__':
    unittest.main()
       
