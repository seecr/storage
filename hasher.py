#
# Hasher
#
# $Id: hasher.py,v 1.3 2006/02/15 13:27:20 cvs Exp $
#

import md5

class Hasher:
	
    def hash(self, aString):
        return md5.md5(aString).hexdigest()
