#!/usr/bin/env python
#
# Generated with:
#
# $Id: gen_alltests.sh,v 1.6 2006/03/16 08:06:56 cvs Exp $
#
# on Tue Apr 11 14:58:34 CEST 2006 by johan
#

import os
os.system('rm *.pyc')

import unittest

from storagefiletest import StorageFileTest
from storagetest import StorageTest

if __name__ == '__main__':
        unittest.main()

