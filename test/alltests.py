#!/usr/bin/env python
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
# Generated with:
#
# $Id: gen_alltests.sh,v 1.6 2006/03/16 08:06:56 cvs Exp $
#
# on Tue Apr 11 14:58:34 CEST 2006 by johan
#

import os, sys
os.system('rm *.pyc')

sys.path.insert(0, '../src/')

import unittest

from storagefiletest import StorageFileTest
from storagetest import StorageTest

if __name__ == '__main__':
        unittest.main()

