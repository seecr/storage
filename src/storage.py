
from os.path import join, isdir
from os import makedirs, rename
from tempfile import mkdtemp
from errno import ENAMETOOLONG, EINVAL 
from shutil import rmtree

BAD_CHARS=['/', chr(0), '%']
def escapeChar(char):
    if char in BAD_CHARS:
        return '%%%02X' % ord(char)
    return char

def escapeName(name):
    return ''.join((escapeChar(char) for char in name))
        

class Storage(object):
    def __init__(self, basedir = None):
        if not basedir:
            self._basedir = mkdtemp()
            self._own = True
        else:
            self._basedir = basedir
            self._own = False
            isdir(self._basedir) or makedirs(self._basedir)

    def __del__(self):
        if self._own:
            rmtree(self._basedir)
        
    def _transferOwnership(self, path):
        rename(self._basedir, path)
        self._basedir = path
        self._own = False
        
    def put(self, name, aStorage = None):
        path = join(self._basedir, escapeName(name))
        try:
            if aStorage:
                aStorage._transferOwnership(path)
            else:
                file = open(path, 'w')
                return Sink(file)
        except (OSError,IOError), e:
            if e.errno == ENAMETOOLONG:
                raise KeyError('Name too long: ' + name)
            elif e.errno == EINVAL:
                raise ValueError('Cannot put Storage inside itself.')
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