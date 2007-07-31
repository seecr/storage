
from os.path import join, isdir
from os import makedirs, rename, popen3
from tempfile import mkdtemp
from errno import ENAMETOOLONG, EINVAL 
from shutil import rmtree
from re import compile

BAD_CHARS = map(chr, range(32)) + ['/', '%']
BAD_BASH_CHARS = ['!','@','$','&','<','>', '|', '(',')',';', '*', '`', '\'', '"', '\\', ' ']

def escapeName(name):
    return ''.join((char in BAD_CHARS and '%%%02X' % ord(char) or char for char in name))

def bashEscape(name):
    return ''.join((char in BAD_BASH_CHARS and '\\' + char or char for char in name))
        

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
     

responsePattern = compile(r'(?s).*(?P<status>initial|unchanged|new).*?\d+\.(?P<revision1>\d+)[^\d]*(?:\d+\.(?P<revision2>\d+))?')

class Sink(object):
    def __init__(self, file):
        self.send = file.write
        self.name = file.name
        self.fileno = file.fileno
        self._close = file.close
    
    def close(self):
        self._close()
        stdin, stdout, stderr = popen3("ci -t-storage -l -mnomesg %s" % bashEscape(self.name))
        response = stderr.read()
        result = responsePattern.match(response).groupdict()
        if result['status'] == 'initial':
            return 0, int(result['revision1'])
        if result['status'] == 'unchanged':
            return int(result['revision1']), int(result['revision1'])
        if result['status'] == 'new':
            return int(result['revision2']), int(result['revision1'])