
from os.path import join, isdir
from os import makedirs, rename

class Storage(object):
    def __init__(self, basedir):
        self._basedir = basedir
        isdir(self._basedir) or makedirs(self._basedir)
        
    def put(self, name, aStorage = None):
        path = join(self._basedir, name)
        if aStorage:
            rename(aStorage._basedir, path)
            aStorage._basedir = path
        else:
            file = open(path, 'w')
            return Sink(file)
    
    def get(self, name):
        path = join(self._basedir, name)
        if isdir(path):
            return Storage(path) 
        return open(path)
    
    
    
class Sink(object):
    def __init__(self, file):
        self.send = file.write
        self._close = file.close
    
    def close(self):
        return self._close()