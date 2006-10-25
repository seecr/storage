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
#
# Storage File Test
#
# $Id: storagefiletest.py,v 1.4 2006/04/11 09:29:53 cvs Exp $
#

import unittest
from StringIO import StringIO
import storagefile

EMPTYMESSAGE = """Content-type: multipart/mixed; boundary="%(boundary)s"

--%(boundary)s--
"""

ONEPARTMESSAGE = """Content-type: multipart/mixed; boundary="%(boundary)s"

--%(boundary)s
Content-type: text/xml; name="part one"

<a><b>1</b><b>2</b></a>
--%(boundary)s--
"""

TWOPARTMESSAGE = """Content-type: multipart/mixed; boundary="%(boundary)s"

--%(boundary)s
Content-type: text/xml; name="part one"

<a><b>1</b><b>2</b></a>
--%(boundary)s
Content-type: text/plain; name="part two"

aap noot mies
--%(boundary)s--
"""

def myClose():
	pass

def getAnIOString():
	stream = StringIO()
	stream.close = myClose
	return stream

class StorageFileTest(unittest.TestCase):
	
	def testWriteEmptyFile(self):
		stream = getAnIOString()
		sf = storagefile.StorageFile(stream, mode='w')
		sf.close()
		
		self.assertEquals(EMPTYMESSAGE % {'boundary':storagefile.BOUNDARY}, stream.getvalue())
		
	def testClose(self):
		stream = getAnIOString()
		sf = storagefile.StorageFile(stream, mode='w')
		sf.close()
		try:
			stream.getvalue()
			self.fail()
		except:
			pass
		
	def testWriteFileWithOneMultipart(self):
		stream = getAnIOString()
		sf = storagefile.StorageFile(stream, mode='w')
		sf.addPart('part one', 'text/xml', '<a><b>1</b><b>2</b></a>')		
		sf.close()
		
		self.assertEquals(ONEPARTMESSAGE % {'boundary':storagefile.BOUNDARY}, stream.getvalue())

	def testWriteFileWithTwoMultiparts(self):
		stream = getAnIOString()
		sf = storagefile.StorageFile(stream, mode='w')
		sf.addPart('part one', 'text/xml', '<a><b>1</b><b>2</b></a>')
		sf.addPart('part two', 'text/plain', 'aap noot mies')	
		sf.close()
		
		self.assertEquals(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY}, stream.getvalue())
		
	def testReadFileWithOneMultipart(self):
		stream = getAnIOString()
		stream.write(ONEPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		stream.seek(0L)
		
		sf = storagefile.StorageFile(stream, mode='r')
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', sf.partAsString('part one'))

	def testReadFileWithTwoMultipart(self):
		stream = getAnIOString()
		stream.write(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		stream.seek(0L)
		
		sf = storagefile.StorageFile(stream, mode='r')
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', sf.partAsString('part one'))
		
		self.assertEquals('aap noot mies\n', sf.partAsString('part two'))

	def testSpeed(self):
		stream = StringIO(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		sf = storagefile.StorageFile(stream, mode='r')
		
		sf.partAsString('part one')
		self.assertEquals(83, sf._partsList['part one'])
		self.assertEquals(['part one'], sf._partsList.keys())
		
		sf.partAsString('part two')
		self.assertEquals(['part two', 'part one'], sf._partsList.keys())

	def testReread(self):
		stream = StringIO(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		sf = storagefile.StorageFile(stream, mode='r')
		stream.seek(0L)
		
		self.assertEquals('aap noot mies\n', sf.partAsString('part two'))
		
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', sf.partAsString('part one'))
		
		self.assertEquals('aap noot mies\n', sf.partAsString('part two'))
		
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', sf.partAsString('part one'))
		
		self.assertEquals('aap noot mies\n', sf.partAsString('part two'))
		
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', sf.partAsString('part one'))


if __name__ == '__main__':
	unittest.main()