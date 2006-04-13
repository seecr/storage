#
# Hex Test
#
# $Id: hextest.py,v 1.1 2006/02/14 14:40:06 cvs Exp $
#

import unittest
import hex

class HexTest(unittest.TestCase):
	
	def testHexString(self):
		self.assertEquals('any string', hex.hexStringToString(hex.stringToHexString('any string')))
		
	#ev. toekomst: fout-checken, unicode
				
if __name__ == '__main__':
    unittest.main()
