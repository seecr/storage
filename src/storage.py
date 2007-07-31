
from os.path import join, isdir
from os import makedirs, rename
from tempfile import mkdtemp
from errno import ENAMETOOLONG

BAD_CHARS=['/', chr(0), '%']
def escapeChar(char):
    if char in BAD_CHARS:
        return '%%%02X' % ord(char)
    return char

def escapeName(name):
    return ''.join((escapeChar(char) for char in name))
        

class Storage(object):
    def __init__(self, basedir = None):
        self._basedir = basedir or mkdtemp()
        isdir(self._basedir) or makedirs(self._basedir)
        
    def put(self, name, aStorage = None):
        path = join(self._basedir, escapeName(name))
        try:
            if aStorage:
                rename(aStorage._basedir, path)
                aStorage._basedir = path
            else:
                file = open(path, 'w')
                return Sink(file)
        except (OSError,IOError), e:
            if e.errno == ENAMETOOLONG:
                raise KeyError('Name too long: ' + name)
            raise
    
    def get(self, name):
        path = join(self._basedir, escapeName(name))
        if isdir(path):
            return Storage(path) 
        return open(path)
     

    
class Sink(object):
    def __init__(self, file):
        self.send = file.write
        self._close = file.close
    
    def close(self):
        return self._close()