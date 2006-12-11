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
import errno
import hasher
import hex
import storagefile

def _directoryForHash(aHash):
	return os.path.sep.join(aHash[0:4])

class StorageException(Exception):
	pass

class Storage:

	def __init__(self, aBaseDirectory, aHasher = hasher.Hasher()):
		self._hasher = aHasher
		self._baseDirectory = aBaseDirectory
		if not os.path.exists(self._baseDirectory):
			os.makedirs(self._baseDirectory)

	""" API """
	def store(self, anId):
		hashDir = self._hashDirectory(anId)
		if not os.path.exists(hashDir):
			os.makedirs(hashDir)
		return storagefile.StorageFile(open(self.filenameFor(anId), 'w'), 'w')

	""" API """
	def isStored(self, anId):
		return os.path.isfile(self.filenameFor(anId))

	""" API """
	def fetch(self, anId):
		try:
			return storagefile.StorageFile(open(self.filenameFor(anId)), 'r')
		except IOError, e:
			if e.errno == errno.ENOENT:
				raise StorageException("File not found for " + anId)

	""" API """
	def remove(self, anId):
		if not anId:
			raise StorageException("Invalid Id")

		filename = self.filenameFor(anId)
		if not os.path.isfile(filename):
			raise StorageException("No such document")
			
		os.remove(filename)
		

	def filenameFor(self, anId):
		if not anId:
			raise StorageException("Invalid Id")
		return os.path.join(self._hashDirectory(anId), hex.stringToHexString(anId))

	def _hashDirectory(self, anId):
		return os.path.join(self._baseDirectory, _directoryForHash(self._hasher.hash(anId)))
