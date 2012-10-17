from tkinter import Frame, LabelFrame, Button, Entry, StringVar, Canvas, E, W, N, S, LAST, NORMAL, Tk, DoubleVar, IntVar, Label
from threading import Thread
from queue import Queue
import unittest
from control import mockControl

class Axis(object):
    def __init__(self, start=0, end = 100, size = 100, direction = 1, margin = 20):
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
        self.config(padx=2)
        self.queue = Queue()
        self.control = control
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
        self.canvas.x.end=self.executionTime.get()
        self.canvas.clear()
        for x in range(self.canvas.x.start, int(self.canvas.x.end)):        
            point = []
            for c in range(len(compiled)):
                v = None
                if compiled[c]:
                    v = compiled[c](x)
                point.append(v)
            self.__addPoint__(x, point)
        self.canvas.update()
    def __start__(self):
        self.canvas.x.end=self.executionTime.get()
        time = float(self.canvas.x.end - self.canvas.x.start)        
        pumps = self.compileFormulae()        
        self.control.mover.maxTravel = abs(int(self.maxTravel.get()))
        def calcPumpValues(time):
            return list(map(lambda x: x(time), pumps))
        def thFunc():
            try:
                for g in self.graphs:
                    g.points=[]
                self.control.executeProgram(time, abs(int(self.programSpeed.get())), calcPumpValues)
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
        def quitting():
            self.__stop__()
            if self.thread and self.thread.is_alive():
                print("Thread is active")
                return False
            self.quit()
            return True
        run_repeating(self, quitting)

    def __move__(self, steps):
        speed= int(self.speed.get())
        if speed < 0:
            speed *= -1
            self.speed.set(speed)
        self.control.mover.go(steps)
    def __up__(self):
        steps = int(self.steps.get())
        self.__move__(steps)
    def __down__(self):
        steps = int(self.steps.get())
        self.__move__(-steps)
        
    def createWidgets(self):
        panel = Frame(self, name="mainMenu")
        panel.grid(sticky=W)        
        Button (panel, name='quit', text='Выход', command=self.__quit__).grid(row=0,column=2)
        panel = LabelFrame(self, text="Прямое управление стаканом", name="motor")
        panel.grid(sticky=W)
        b=Button(panel, text='Вверх', command=self.__up__, name="up")
        b.grid(row=0, column=0)
        self.disabledWhileRunning.append(b)
        b=Button(panel, text='Вниз', command=self.__down__, name="down")
        b.grid(row=1, column=0)
        self.disabledWhileRunning.append(b)
        Label(panel, text="Шаг:").grid(sticky=E, row=0, column=1)
        self.steps = IntVar(self, "100")
        Entry(panel, textvariable=self.steps, width=6).grid(sticky=W, row=0, column=2)
        Label(panel, text="Скорость:").grid(sticky=E, row=1, column=1)
        self.speed = IntVar(self, "1000")
        Entry(panel, textvariable=self.speed, width=6).grid(sticky=W, row=1, column=2)
        self.position = IntVar(self, "1000")
        def readPosition():
            self.position.set(self.control.mover.getPosition())
        b=Button(panel, text="Прочитать положение", command=readPosition)
        b.grid(row=0, column=3, columnspan=2)
        self.disabledWhileRunning.append(b)
        Label(panel, text="Положение:").grid(sticky=E, row=1, column=3)
        Entry(panel, textvariable=self.position, width=8, state = "disabled").grid(sticky=W, row=1, column=4)

        self.formulae=list(map(lambda t: StringVar(self, t), ["x/7.14+4","20-x/7.14"]))
        panel = LabelFrame(self, text="Программа", name="program")
        program=panel
        panel.grid(sticky=W+E)
        panel.columnconfigure(1, weight=1)
        row = 0
        for f in self.formulae:
            columns, rows = self.grid_size()
            Label(panel, text="Насос %d:" % (row+1)).grid(row=row, column=0, sticky=E)           
            e = Entry(panel, textvariable=f)
            e.grid(sticky=E+W, row=row, column=1)            
            self.disabledWhileRunning.append(e)            
            f.trace("w", lambda *x: self.after_idle(self.plotFormulae))
            row+=1
        panel = Frame(program, name="mover")
        panel.grid(columnspan=2, sticky=W)        
        self.maxTravel = IntVar(self, "-1000000")
        Label(panel, text="Максимальное смещение:").grid(sticky=E)
        Entry(panel, textvariable=self.maxTravel, width=8).grid(sticky=W, row=0, column=1)
        Label(panel, text="Скорость:").grid(sticky=E)
        self.programSpeed=IntVar(self, "-1000")
        Entry(panel, textvariable=self.programSpeed, width=8).grid(sticky=W, row=1, column=1)
        Label(panel, text="Время выполнения (в секундах):").grid(sticky=E)
        self.executionTime = DoubleVar(self, "100")
        e=Entry(panel, textvariable=self.executionTime, width=4)
        e.grid(sticky=W, row=2, column=1)
        self.disabledWhileRunning.append(e)
        self.executionTime.trace("w", lambda *x: self.plotFormulae())
        
        panel = Frame(program, name="bottom")
        panel.grid(columnspan=2, sticky=W)
        row=0
        startButton = Button (panel, name='start', text='Старт', command=self.__start__)
        startButton.grid(row=row, column=0)
        self.disabledWhileRunning.append(startButton)         
        Button (panel, text='Стоп', command=self.__stop__).grid(row=row, column=1)         
        
        
        self.canvas = GraphCanvas(self)
        self.graphs = (Graph(self.canvas), Graph(self.canvas))
        
        self.canvas.x.end=100
        self.canvas.y.end=24
        self.plotFormulae()
        self.canvas.grid(sticky=E+W+S+N)
        columns, rows = self.grid_size()
        self.columnconfigure(columns-1, weight=1)
        self.rowconfigure(rows-1, weight=1)


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
       
