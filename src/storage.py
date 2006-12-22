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
from glob import glob

def _directoryForHash(aHash):
	return os.path.sep.join(aHash[0:4])

class StorageException(Exception):
	pass


class Storage:

	def __init__(self, aBaseDirectory, hasher = Hasher()):
		self._hasher = hasher
		self._baseDirectory = aBaseDirectory
		if not os.path.isdir(self._baseDirectory):
			os.makedirs(self._baseDirectory)

	""" API """
	def getUnit(self, anId):
		baseName = self._baseFilenameFor(anId)
		return Unit(anId, baseName)

	""" API """
	def hasUnit(self, anId):
		return self.getUnit(anId).exists()

	""" API """
	def removeUnit(self, anId):
		raise Exception('self.needsMoreWork')

	def _baseFilenameFor(self, anId):
		if not anId:
			raise StorageException("Invalid Id")
		return os.path.join(self._hashDirectory(anId), stringToHexString(anId))

	def _hashDirectory(self, anId):
		return os.path.join(self._baseDirectory, _directoryForHash(self._hasher.hash(anId)))
	

class Unit:
	def __init__(self, identifier, baseName):
		self._identifier = identifier
		self._baseName = baseName
		
	def getId(self):
		return self._identifier
	
	def getBaseName(self):
		return self._baseName
	
	def exists(self):
		return len(glob(self._baseName + '.*')) > 0
	
	def openBox(self, boxName, mode = 'r'):
		if not boxName:
			raise StorageException("Invalid boxname")
		
		filename = self._baseName + '.' + stringToHexString(boxName)
		
		dirname = os.path.dirname(filename)
		os.path.isdir(dirname) or os.makedirs(dirname)
		
		return open(filename, mode)
	
	def listBoxes(self):
		return [ hexStringToString(f.split('.')[-1]) for f \
			in glob(self._baseName + '.*') ]
