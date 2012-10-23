import unittest
from config import Config
from control import mockControl
from tempfile import TemporaryFile
from os import fdopen, close

class TestConfig(unittest.TestCase):
    def writeAndRestore(self, config):
        file = TemporaryFile(suffix=".ini", prefix="varfill", mode='w+')
        try:
            config.write(file)
            file.seek(0)
            config = Config()
            config.read(file)
            return config
        finally:
            file.close()
            
    def createConfig(self):
        config = Config()
        config.executionTime=1
        config.programSpeed=2
        config.maxTravel=3
        config.formulae=["4", "5"]
        return config
               
    def testBase(self):
        config = self.createConfig()
        
        config = self.writeAndRestore(config)
        
        self.assertEqual(config.executionTime, 1)
        self.assertEqual(config.programSpeed, 2)
        self.assertEqual(config.maxTravel, 3)
        self.assertEqual(config.formulae, ["4", "5"])
    
    def testValues(self):
        config = Config()
        
        config.executionTime = -401
        config.formulae = ["aa", "bb"]
        config.maxTravel = -5
        config.programSpeed = -7
        
        config = self.writeAndRestore(config)
        
        self.assertEqual(config.executionTime, 401)
        self.assertEqual(config.formulae, ["aa", "bb"])
        self.assertEqual(config.maxTravel, -5)
        self.assertEqual(config.programSpeed, 7)
    
    def testControlSet(self):
        config = self.createConfig()
        control = mockControl()
        config.configureControl(control)
        self.assertEqual(control.fullTime, 1)
        self.assertEqual(control.mover.getSpeed(), 2)
        self.assertEqual(control.mover.maxTravel, 3)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()