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
		strm = StringIO()
		sf.getPartNamed('part one', strm)
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', strm.getvalue())

	def testReadFileWithTwoMultipart(self):
		stream = getAnIOString()
		stream.write(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		stream.seek(0L)
		
		strm = StringIO()
		sf = storagefile.StorageFile(stream, mode='r')
		sf.getPartNamed('part one', strm)
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', strm.getvalue())
		
		strm = StringIO()
		sf.getPartNamed('part two', strm)
		self.assertEquals('aap noot mies\n', strm.getvalue())

	def testSpeed(self):
		stream = StringIO(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		sf = storagefile.StorageFile(stream, mode='r')
		
		strm = StringIO()
		sf.getPartNamed('part one', strm)		
		self.assertEquals(83, sf._partsList['part one'])
		self.assertEquals(['part one'], sf._partsList.keys())
		
		strm = StringIO()
		sf.getPartNamed('part two', strm)
		self.assertEquals(['part two', 'part one'], sf._partsList.keys())

	def testReread(self):
		stream = StringIO(TWOPARTMESSAGE % {'boundary':storagefile.BOUNDARY})
		sf = storagefile.StorageFile(stream, mode='r')
		stream.seek(0L)
		
		strm = StringIO()
		sf.getPartNamed('part two', strm)
		self.assertEquals('aap noot mies\n', strm.getvalue())
		
		strm = StringIO()
		sf.getPartNamed('part one', strm)
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', strm.getvalue())
		
		strm = StringIO()
		sf.getPartNamed('part two', strm)
		self.assertEquals('aap noot mies\n', strm.getvalue())
		
		strm = StringIO()
		sf.getPartNamed('part one', strm)
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', strm.getvalue())
		
		strm = StringIO()
		sf.getPartNamed('part two', strm)
		self.assertEquals('aap noot mies\n', strm.getvalue())
		
		strm = StringIO()
		sf.getPartNamed('part one', strm)
		self.assertEquals('<a><b>1</b><b>2</b></a>\n', strm.getvalue())


if __name__ == '__main__':
	unittest.main()