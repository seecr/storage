#
# Storage
#
# $Id: storage.py,v 1.12 2006/03/09 09:09:55 cvs Exp $
#

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
