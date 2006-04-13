#
# Hasher Test
#
# $Id: hashertest.py,v 1.2 2006/02/14 11:32:34 cvs Exp $
#

import unittest
import hasher

class HashTest(unittest.TestCase):

	def testHash(self):
		myHasher = hasher.Hasher()
	
		self.assertEquals('98bf7d8c15784f0a3d63204441e1e2aa', myHasher.hash('contents'))
		
	def testHashingIsConsistent(self):
		myHasher = hasher.Hasher()
		self.assertEquals(myHasher.hash("a"), myHasher.hash("a"))
	
	def testUnicode(self):
		myHasher = hasher.Hasher()
		self.assertEquals(myHasher.hash("a"), myHasher.hash(u"a"))

if __name__ == '__main__':
	unittest.main()
