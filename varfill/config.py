from configparser import ConfigParser
from errno import ENOENT

class Config(object):
    def __init__(self):
        self.filename = "varfill.ini"
        self.executionTime = 360
        self.programSpeed = 250
        self.maxTravel = -200000
        self.formulae = ["x/22.5+4","20-x/22.5"]
    def write(self, file = None):
        if not file:
            file = open(self.filename, 'w')
        config = ConfigParser()
        program = {}
        program['executionTime'] = abs(float(self.executionTime))
        program['programSpeed'] = abs(int(self.programSpeed))
        program['maxTravel'] = int(self.maxTravel)
        program['formula1'] = self.formulae[0]
        program['formula2'] = self.formulae[1]
        config['program']=program
        config.write(file)
    def read(self, file = None):
        try:
            if not file:
                file = open(self.filename, 'r')
            config = ConfigParser()        
            config.read_file(file, self.filename)
            program = config['program']
            self.executionTime = abs(float(program['executionTime']))
            self.programSpeed = abs(int(program['programSpeed']))
            self.maxTravel = int(program['maxTravel'])
            self.formulae = list(map(lambda key: program[key], ["formula1", "formula2"]))
        except IOError as e:
            if e.errno != ENOENT:
                raise
        
    def getFromControl(self, control):
        self.executionTime = abs(float(control.fullTime))
        self.maxTravel = int(control.mover.maxTravel)
        self.programSpeed = abs(int(control.mover.getSpeed()))
    
    def configureControl(self, control):
        control.fullTime = abs(float(self.executionTime))
        control.mover.maxTravel = int(self.maxTravel)
        control.mover.setSpeed(abs(int(self.programSpeed)))

        