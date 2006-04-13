#
# Storage File
#
# $Id: storagefile.py,v 1.4 2006/04/11 09:29:53 cvs Exp $
#

import multifile
import mimetools
import cStringIO

BOUNDARY = '-x-x-BOUNDARY-x-x-'

class StorageFile:
	
	def __init__(self, aStream, mode='w'):
		self._stream = aStream
		self._file = multifile.MultiFile(self._stream)
		self._file.push(BOUNDARY)
		self._mode = mode
		self._partsList = {}
		if self._mode == 'w':
			self._writeFileHeader()
		
	def close(self):
		if self._mode == 'w':
			self._writeFileFooter()
		self._stream.close()
		
	def _writeFileHeader(self):
		self._stream.write("""Content-type: multipart/mixed; boundary="%s"

""" % BOUNDARY)
		
	def _writeFileFooter(self):
		self._stream.write('--%s--\n' % BOUNDARY)
		
	def addPart(self, aName, aType, aString):
		self._stream.write("""--%s
Content-type: %s; name="%s"

%s
""" % (BOUNDARY, aType, aName, aString))

	def getPartAtFileIndex(self, aPosition, aStream):
		currentPosition = self._stream.tell()
		try:
			self._stream.seek(aPosition)
			m = multifile.MultiFile(self._stream)
			m.push(BOUNDARY)
			message = mimetools.Message(m)
			mimetools.decode(m, aStream, message.getencoding())
		finally:
			self._stream.seek(currentPosition)
			
	def getPartNamed(self, aString, aStream):
		if aString in self._partsList:
			return self.getPartAtFileIndex(self._partsList[aString], aStream)
		
		while self._file.next():
			position = self._stream.tell()
			message = mimetools.Message(self._file)
			name = 'name' in message.getparamnames() and message.getparam('name') or None
			if name:
				self._partsList[name] =  position
			if name == aString:
				mimetools.decode(self._file, aStream, message.getencoding())
				break

