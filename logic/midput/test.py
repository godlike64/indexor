'''
Created on Dec 22, 2009

@author: godlike
'''
class Singleton(object):
    _instance = None
    
    def __init__(self):
        self.a = "aaauuu"
        self.b = "oooaaa"
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance