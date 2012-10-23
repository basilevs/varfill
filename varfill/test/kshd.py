'''
Created on 23.10.2012

@author: gulevich
'''
import unittest
from piv import Kshd

class KshdConfigurationTest(unittest.TestCase):
    def test_parse(self):
        conf = Kshd.Configuration(3.5, 0.5, 2, True, False, True, True, True, True, True)
        w = conf.toWord()
        conf2 = Kshd.Configuration.fromWord(w)
        self.assertEqual(conf2.toWord(), w)
        self.assertEqual(conf.moveCurrent, 3.5)
    def test_speed(self):
        speedConf = Kshd.SpeedConf(1000, 2000, 3000)
        w = speedConf.toWord()
        speedConf2 = Kshd.SpeedConf.fromWord(w)
        self.assertEqual(speedConf2.toWord(), w)
        self.assertEqual(speedConf2.max, 2000)

if __name__ == '__main__':
    unittest.main()
        
()