from tkinter import Frame, Button, Entry, StringVar, Canvas, E, W, BOTH, N, S, LAST


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
    
class Graph(Canvas):
    def __init__(self, parent):
        Canvas.__init__(self, parent, bg="white")
        self.points = []
        self.start = 0
     r  self.end = 100
        self.bind("<Configure>", lambda ev: self.after_idle(self.__onResize__))
        self.x=Axis()
        self.y=Axis()
        self.y.direction=-1
        
    def __onResize__(self):
        w = self.winfo_width()
        h = self.winfo_height()
        if w in [-1, 1]:
            return
        if h in [-1, 1]:
            return
        self.x.size = w  
        self.y.size = h
        self.update()

    def drawLine(self, x1, y1, x2, y2):
        y1 = self.y.toExternal(y1)
        coord = (self.x.toExternal(x1), y1,
                 self.x.toExternal(x2), self.y.toExternal(y2))
        print(coord)
        self.create_line(*coord, width=1)
        
    def drawStep(self, prevPoint, currentPoint):
        assert(len(prevPoint) == len(currentPoint))
        for i in range(1, len(prevPoint)):
            self.drawLine(prevPoint[0], prevPoint[i], currentPoint[0], currentPoint[i])
    
    def drawAxises(self):
        y0 = self.y.toExternal(0)
        y1 = self.y.toExternal(self.y.end) 
        x0 = self.x.toExternal(0)
        x1 = self.x.toExternal(self.x.end)
        self.create_line(x0, y0, x1, y0, width = 2, arrow=LAST)
        self.create_line(x0, y0, x0, y1, width = 2, arrow=LAST)
    def update(self):
        for i in self.find_all():
            self.delete(i)
        self.drawAxises()
        prev = None
        for p in self.points:
            if prev:
                self.drawStep(prev, p)
            prev = p
    def addPoint(self, x, values):
        point = [x]
        point.extend(values)
        self.points.append(point)
    def setRange(self, start, end):
        pass
    def clear(self):
        for i in self.find_all():
            self.delete(i)
        self.points=[]
        
class Gui(Frame):
    def __init__(self, control, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.control = control
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)
        self.createWidgets()
    
    def compileFormulae(self):
        rv = []
        for f in self.formulae:
            body = "def formula5480750923(x):\n  return "+f.get()
            l = {}
            exec(body, {}, l)
            compiled = l["formula5480750923"]
            compiled(0)
            rv.append(compiled)
        return rv
    def plotFormulae(self):
        compiled = self.compileFormulae()
        for x in range(100):        
            point = []
            for c in range(len(compiled)):
                point.append(compiled[c](x))
            self.graph.addPoint(x, point)
    def createWidgets(self):
        self.formulae=list(map(lambda t: StringVar(self, t), ["x/7.14+4","20-x/7.14"]))
        for f in self.formulae:
            Entry(self, textvariable=f).grid(sticky=E+W)
        Button (self, text='Quit', command=self.quit).grid()         
        self.graph = Graph(self)
        
        self.graph.setRange(0, 100)
        self.plotFormulae()
        self.graph.grid(sticky=E+W+S+N)
