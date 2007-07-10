## begin license ##
#
#    Storage stores data in a reliable, extendable filebased storage
#    with great performance.
#    Copyright (C) 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
#
#    This file is part of Storage.
#
#    Storage is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    Storage is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Storage; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

import os
from hex import stringToHexString, hexStringToString
from hasher import Hasher
from file import File

def _directoryForHash(aHash):
    return os.path.sep.join(aHash[0:4])

class StorageException(Exception):
    pass


class Storage(object):

    def __init__(self, aBaseDirectory, hasher = Hasher()):
        self._hasher = hasher
        self._baseDirectory = aBaseDirectory
        if not os.path.isdir(self._baseDirectory):
            os.makedirs(self._baseDirectory)

    """ API """
    def getUnit(self, anId):
        if not anId:
            raise StorageException("Invalid Id")
        return Unit(anId, self._baseDirFor(anId))

    """ API """
    def hasUnit(self, anId):
        return self.getUnit(anId).exists()

    """ API """
    def removeUnit(self, anId):
        self.getUnit(anId).remove()

    def _baseDirFor(self, anId):
        return os.path.join(self._baseDirectory, _directoryForHash(self._hasher.hash(anId)))
    

class Unit(object):
    def __init__(self, identifier, baseDir):
        self._identifier = identifier
        self._file = File(baseDir, identifier, exceptionHandle = self._handleException)
        
    def getId(self):
        return self._identifier
    
    def exists(self):
        return self._file.exists()
    
    def openBox(self, boxName, mode = 'r'):
        return self._file.openExtension(boxName, mode)
    
    def hasBox(self, boxName):
        return self._file.extensionExists(boxName)

    def _handleException(self, message):
        raise StorageException("Invalid boxname")
    
    def listBoxes(self):
        return self._file.listExtensions() 
        
    def remove(self):
        for boxName in self.listBoxes():
            self.removeBox(boxName)
            
    def removeBox(self, boxName):
        if self.hasBox(boxName):
            self._file.removeExtension(boxName)
            
    def moveBox(self, srcBoxName, dstBoxName):
        if self.hasBox(srcBoxName):
            self._file.renameExtension(srcBoxName, dstBoxName)


