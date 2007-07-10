
from glob import glob
from os import remove, rename, makedirs, walk, rmdir, listdir
from os.path import isfile, join, dirname, isdir, sep as pathSeparator
from hex import stringToHexString, hexStringToString

class FileException(Exception):
    pass

SEPARATOR = '@' + pathSeparator + '@'

class File(object):
    def __init__(self, baseDir, baseName, exceptionHandle = FileException):
        self._baseDir = baseDir
        self._hexedBaseName = stringToHexString(baseName)
        self._exceptionHandle = exceptionHandle
        self._maxfilelength = 250
        
    def exists(self):
        return len(self.listExtensions()) > 0
    
    def listExtensions(self):
        return [ hexStringToString(f.replace(SEPARATOR, '').split('.')[-1]) for f \
            in self._listExtensions()]
        
    def removeExtension(self, extension):
        filename = self._withExtension(extension)
        isfile(filename) and remove(filename)
        self._pruneEmptyDirectories(dirname(filename))
        
    def renameExtension(self, srcExtension, dstExtension):
        srcFilename = self._withExtension(srcExtension)
        dstFilename = self._withExtension(dstExtension)
        isdir(dirname(dstFilename)) or makedirs(dirname(dstFilename))
        rename(srcFilename, dstFilename)
        self._pruneEmptyDirectories(dirname(srcFilename))
        
    def extensionExists(self, extension):
        return isfile(self._withExtension(extension))
        
    def openExtension(self, extension, mode):
        filename = self._withExtension(extension)
        
        directory = dirname(filename)
        isdir(directory) or makedirs(directory)
        
        return open(filename, mode)
        
    def _withExtension(self, extension):
        if not extension:
            raise self._exceptionHandle("Invalid extension")
        
        return join(self._baseDir, self._filename(self._hexedBaseName + '.' + stringToHexString(extension)))
    
    def _filename(self, name):
        if len(name) <= self._maxfilelength:
            return name
        return SEPARATOR.join(self._splitup(name, self._maxfilelength - 2))
        
    def _splitup(self, name, length):
        i = 0
        while(len(name[i:])):
            yield name[i:i+length]
            i += length
    
    def _listExtensions(self):
        for item in glob(join(self._baseDir, self._filename(self._hexedBaseName+'.')) + '*'):
            if isfile(item):
                yield item
            if isdir(item):
                for diritem in self._listdir(item):
                    yield diritem
                    
    def _listdir(self, basedirectory):
        for directory, subdirs, files in walk(basedirectory):
            for file in files:
                yield join(directory, file)

    def _pruneEmptyDirectories(self, directoryName):
        current = directoryName
        while(len(listdir(current)) == 0 and current != self._baseDir):
            rmdir(current)
            current = dirname(current)

