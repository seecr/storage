
from os.path import join, isdir, basename, isfile
from os import makedirs, rename, popen3, remove, listdir
from tempfile import mkdtemp
from errno import ENAMETOOLONG, EINVAL, ENOENT, EISDIR, ENOTDIR, ENOTEMPTY
from shutil import rmtree
from re import compile

BAD_CHARS = map(chr, range(32)) + ['/', '%', ',', '.']
REVERSE_BAD_CHARS = compile('%([0-9A-F]{2})')
HEX_TO_CHAR = lambda x:chr(int(x.group(1),16))
BAD_BASH_CHARS = ['!','@','$','&','<','>', '|', '(',')',';', '*', '`', '\'', '"', '\\', ' ']

def escapeName(name):
    return ''.join((char in BAD_CHARS and '%%%02X' % ord(char) or char for char in name))

def unescapeName(name):
    return REVERSE_BAD_CHARS.sub(HEX_TO_CHAR, name)

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
        self.name = unescapeName(basename(self._basedir))

    def __del__(self):
        if self._own:
            rmtree(self._basedir)
        
    def _transferOwnership(self, path):
        rename(self._basedir, path)
        self._basedir = path
        self._own = False
        self.name = unescapeName(basename(self._basedir))
        

    def put(self, name, aStorage = None):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeName(name))
        try:
            if aStorage:
                aStorage._transferOwnership(path)
                return aStorage
            else:
                file = open(path, 'w')
                return Sink(file)
        except (OSError,IOError), e:
            if e.errno == ENAMETOOLONG:
                raise KeyError('Name too long: ' + name)
            elif e.errno == EINVAL:
                raise ValueError('Cannot put Storage inside itself.')
            elif e.errno in [ENOTDIR, EISDIR, ENOTEMPTY]:
                raise KeyError('Key already exists: ' + name)
            raise
    
    def get(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeName(name))
        if isdir(path):
            return Storage(path)
        return File(path)

    def __contains__(self, name):
        path = join(self._basedir, escapeName(name))
        return isfile(path) or isdir(path)

    def delete(self, name):
        path = join(self._basedir, escapeName(name))
        try:
            if isdir(path):
                rmtree(path)
            else:
                remove(path)
                remove(path + ',v')
        except OSError, e:
            if e.errno == ENOENT:
                raise KeyError(name)
            raise

    def __iter__(self):
        for item in listdir(self._basedir):
            if not item.endswith(',v'):
                yield self.get(unescapeName(item))
            
responsePattern = compile(r'(?s).*(?P<status>initial|unchanged|new).*?\d+\.(?P<revision1>\d+)[^\d]*(?:\d+\.(?P<revision2>\d+))?')

class Sink(object):
    def __init__(self, file):
        self.send = file.write
        self.name = file.name
        self.fileno = file.fileno
        self._close = file.close
    
    def close(self):
        self._close()
        return self._generateRevision()

    def _generateRevision(self):
        stdin, stdout, stderr = popen3("ci -t-storage -l -mnomesg %s" % bashEscape(self.name))
        response = stderr.read()
        result = responsePattern.match(response).groupdict()
        if result['status'] == 'initial':
            return 0, int(result['revision1'])
        if result['status'] == 'unchanged':
            return int(result['revision1']), int(result['revision1'])
        if result['status'] == 'new':
            return int(result['revision2']), int(result['revision1'])

class File(object):
    def __init__(self, path):
        self.path = path
        self.name = unescapeName(basename(path))
        self.__file = None

    def _file(self):
        if self.__file == None:
            self.__file = open(self.path)
        return self.__file

    def __getattr__(self, attr):
        return getattr(self._file(), attr)

    def __iter__(self):
        return self._file()
