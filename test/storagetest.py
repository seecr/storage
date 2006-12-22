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

import os.path

from hex import stringToHexString
from unittest import TestCase
from storage import Storage, StorageException
from tempfile import mkdtemp
from shutil import rmtree

class StorageTest(TestCase):
	def setUp(self):
		self._tempdir = mkdtemp()
		self._storagedir = os.path.join(self._tempdir, 'storage')
		hasher = self
		self.storage = Storage(self._storagedir, hasher)
	
	def tearDown(self):
		if os.path.exists(self._tempdir):
			rmtree(self._tempdir)

	""" self shunt """
	def hash(self, anId):
		return '0A2F45A3F15etc'

	def testCreation(self):
		self.assertEquals(os.path.exists(self._storagedir), True)
		self.assertEquals(os.path.isdir(self._storagedir), True)
		
	def testGetUnit(self):
		anId = 'anIdentifier'
		self.assertFalse(self.storage.hasUnit(anId))
		
		unit = self.storage.getUnit(anId)
		
		self.assertEquals(anId, unit.getId())
		baseName = self._storagedir + '/0/A/2/F/' + stringToHexString(anId)
		self.assertEquals(baseName, unit.getBaseName())
		
	def testWriteToUnit(self):
		unit = self.storage.getUnit('anId')
		self.assertFalse(unit.exists())
		
		stream = unit.openBox('boxname', 'w')
		stream.write('data')
		stream.close()
		
		self.assertTrue(unit.exists())
		
		filename = self._storagedir + '/0/A/2/F/' + stringToHexString('anId') + '.' + stringToHexString('boxname')
		self.assertTrue(os.path.isfile(filename))
		stream = unit.openBox('boxname')
		try:
			self.assertEquals('data', stream.read())
		finally:
			stream.close()


	def testReadFromUnit(self):
		unit = self.storage.getUnit('anId')
		stream = unit.openBox('boxname', 'w')
		stream.write('data')
		stream.close()

		stream = unit.openBox('boxname')
		try:
			self.assertEquals('data', stream.read())
		finally:
			stream.close()
		
	def testListBoxes(self):
		unit = self.storage.getUnit('anId')
		self.assertEquals([], unit.listBoxes())
		unit.openBox('boxname', 'w').close()
		self.assertEquals(set(['boxname']), set(unit.listBoxes()))
		unit.openBox('boxname2', 'w').close()
		self.assertEquals(set(['boxname', 'boxname2']), set(unit.listBoxes()))
		
	def testWriteTwice(self):
		unit = self.storage.getUnit('anId')
		# write one
		stream = unit.openBox('boxname', 'w')
		stream.write('data')
		stream.close()
		# write again
		stream = unit.openBox('boxname', 'w')
		stream.write('otherdata')
		stream.close()
		# read
		stream = unit.openBox('boxname')
		try:
			self.assertEquals('otherdata', stream.read())
		finally:
			stream.close()
		
	def testEmptyId(self):
		def assertWrongId(anId):
			try:
				self.storage.getUnit(anId)
				self.fail()
			except StorageException, e:
				pass
		assertWrongId('')
		assertWrongId(None)
		
	def testEmptyBoxName(self):
		unit = self.storage.getUnit('anId')
		def assertWrongBoxName(name):
			try:
				unit.openBox(name, 'w')
				self.fail()
			except StorageException, e:
				pass
		assertWrongBoxName('')
		assertWrongBoxName(None)
		
	
	# storage.removeUnit
	# unit.remove
	# unit.removeBox
	#errors:
	# - wrong write mode

