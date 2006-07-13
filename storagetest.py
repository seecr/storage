#
# Storage Test
#
# $Id: storagetest.py,v 1.12 2006/04/11 09:29:53 cvs Exp $
#

import unittest
import tempfile
import storage
import os.path
import shutil
import cStringIO

import hex

STORAGETEMPLATE = """Content-type: multipart/mixed; boundary="-x-x-BOUNDARY-x-x-"

---x-x-BOUNDARY-x-x-
Content-type: text/plain; name="a name"

%s
---x-x-BOUNDARY-x-x---
"""


class StorageTest(unittest.TestCase):
	def setUp(self):
		self._tempdir = tempfile.gettempdir()+'/testing'
		self._storagedir = os.path.join(self._tempdir, 'storage')
	
	def tearDown(self):
		if os.path.exists(self._tempdir):
			shutil.rmtree(self._tempdir)

	""" self shunt """
	def hash(self, anId):
		return '0A2F45A3F15etc'

	def _writeToStorage(self, aStorage, anId, aString):
		stream = aStorage.store(anId)
		try:
			stream.addPart('a name', 'text/plain', aString)
		finally:
			stream.close()

	def testCreation(self):

		fileStorage = storage.Storage(self._storagedir, self)
		self.assertEquals(os.path.exists(self._storagedir), True)
		self.assertEquals(os.path.isdir(self._storagedir), True)
		
	def testStore(self):
		fileStorage = storage.Storage(self._storagedir, self)
		anId = 'bestand'
		self.assertFalse(fileStorage.isStored(anId))
		
		self._writeToStorage(fileStorage, anId, "contents")
		filename = self._storagedir+'/0/A/2/F/'+hex.stringToHexString(anId)
		
		self.assertEquals(os.path.exists(filename), True)
		self.assertEquals(open(filename).read(), STORAGETEMPLATE % "contents", True)

		self.assertTrue(fileStorage.isStored(anId))
		try:
			f = fileStorage.fetch(anId)
			contents = f.partAsString('a name')
		finally:
			f.close()
		self.assertEquals('contents\n', contents)

	def testStoreTwice(self):
		fileStorage = storage.Storage(self._storagedir, self)
		
		anId = 'bestand'
		self._writeToStorage(fileStorage, anId, "contents")
		self._writeToStorage(fileStorage, anId, "contents2")
		filename = self._storagedir+'/0/A/2/F/'+hex.stringToHexString(anId)
		
		self.assertEquals(os.path.exists(filename), True)
		self.assertEquals(open(filename).read(), STORAGETEMPLATE % "contents2", True)

		try:
			f = fileStorage.fetch(anId)
			contents = f.partAsString('a name')
		finally:
			f.close()
		self.assertEquals('contents2\n', contents)


	def testDisappearingFile(self):
		fileStorage = storage.Storage(self._storagedir, self)
		
		anId = 'bestand'
		self._writeToStorage(fileStorage, anId, "contents")
		filename = self._storagedir+'/0/A/2/F/'+hex.stringToHexString(anId)
		
		self.assertEquals(os.path.exists(filename), True)
		self.assertEquals(open(filename).read(), STORAGETEMPLATE % "contents", True)

		os.remove(filename)
	
		try:
			f = fileStorage.fetch(anId)
			try:
				contents = f.partAsString('a name')
			finally:
				f.close()
			self.fail()
		except storage.StorageException, e:
			self.assertEquals("File not found for " + anId, str(e))

	def testAddJunkToStorage(self):
		fileStorage = storage.Storage(self._storagedir, self)
		try:
			self._writeToStorage(fileStorage, '', "contents")
			self.fail()
		except storage.StorageException, e:
			self.assertEquals("Invalid Id", str(e))

		try:
			self._writeToStorage(fileStorage, None, "contents")
			self.fail()
		except storage.StorageException, e:
			self.assertEquals("Invalid Id", str(e))

	def testRemoveNoID(self):
		fileStorage = storage.Storage(self._storagedir, self)
		
		try:
			fileStorage.remove('')
			self.fail()
		except:
			pass

	def testRemove(self):
		fileStorage = storage.Storage(self._storagedir, self)
		myId = '1'
		
		self._writeToStorage(fileStorage, myId, "contents")
		self.assertTrue(fileStorage.isStored(myId))
		fileStorage.remove(myId)
		self.assertFalse(fileStorage.isStored(myId))

	def testRemoveBadId(self):
		fileStorage = storage.Storage(self._storagedir, self)
		badId = '2'
		
		self.assertFalse(fileStorage.isStored(badId))
		try:
			fileStorage.remove(badId)
			self.fail()
		except:
			pass
		self.assertFalse(fileStorage.isStored(badId))

if __name__ == '__main__':
	unittest.main()
