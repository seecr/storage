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

from unittest import TestCase
from storage import Directory
from tempfile import mkdtemp
from os.path import join, exists, isdir, isfile
from os import makedirs, listdir
from shutil import rmtree

class DirectoryTest(TestCase):
    def setUp(self):
        self._tempdir = mkdtemp()
        self._basedir = join(self._tempdir, 'basedir')
        self.exceptions = [] 
    
    def tearDown(self):
        if exists(self._tempdir):
            rmtree(self._tempdir)
       
    def _handleException(self, message):
        self.exceptions.append(message)
        raise Exception(message)
    
    def createDirectory(self, basename):
        return Directory(self._basedir, basename, self._handleException)
    
    def testName(self):
        d = self.createDirectory('aap')
        d.openFile('noot', 'w').close()
        self.assertEquals(['616170.6E6F6F74'], self._listdir(self._basedir))
        self.assertEquals(['noot'], d.listFiles())
        d.openFile('mies', 'w').close()
        self.assertEquals(['mies', 'noot'], sorted(d.listFiles()))
        d.removeFile('noot')
        self.assertEquals(['mies'], d.listFiles())
        self.assertTrue(d.extensionExists('mies'))
        self.assertFalse(d.extensionExists('noot'))
        d.renameFile('mies', 'vuur')
        self.assertFalse(d.extensionExists('mies'))
        self.assertTrue(d.extensionExists('vuur'))
        
    def _listdir(self, aDirectory):
        all=[]
        for item in listdir(aDirectory):
            fullpath = join(aDirectory,item)
            if isfile(fullpath):
                all.append(item)
            elif isdir(fullpath):
                all.extend([join(item, f) for f in self._listdir(fullpath)])
        return sorted(all)
        
    def testLongFilename(self):
        d = self.createDirectory('longname')
        self.assertEquals(250, d._maxfilelength)
        d._maxfilelength = 14
        d.openFile('aap', 'w').close()
        self.assertEquals(['6C6F6E676E61@/@6D65.616170'], self._listdir(self._basedir))
        d.openFile('abcdefghijklmnopqrst', 'w').close()
        self.assertEquals(['6C6F6E676E61@/@6D65.616170', '6C6F6E676E61@/@6D65.6162636@/@465666768696@/@A6B6C6D6E6F7@/@071727374'], self._listdir(self._basedir))
        
    def testLongFilenameWithListFiles(self):
        d = self.createDirectory('longname')
        d._maxfilelength = 14
        d.openFile('aap', 'w').close()
        d.openFile('abcdefghijklmnopqrst', 'w').close()
        self.assertEquals(['aap', 'abcdefghijklmnopqrst'], sorted(d.listFiles()))
        
    def testLongFilenameWithListFileOnTheEdge(self):
        d = self.createDirectory('longna')
        d._maxfilelength = 15
        d.openFile('aap', 'w').close()
        d.openFile('abcdefghijklmnopqrst', 'w').close()
        self.assertEquals(['aap', 'abcdefghijklmnopqrst'], sorted(d.listFiles()))
        self.assertEquals(['6C6F6E676E61.@/@616170', '6C6F6E676E61.@/@6162636465666@/@768696A6B6C6D@/@6E6F707172737@/@4'], self._listdir(self._basedir))
        
    def testExistsWithLongFilename(self):
        d = self.createDirectory('longname')
        d._maxfilelength = 14
        d.openFile('aap', 'w').close()
        d.exists()
        
    def testRemoveWithLongFilename(self):
        d = self.createDirectory('longname')
        d._maxfilelength = 9
        d.openFile('aap', 'w').close()
        d2 = self.createFile('long2')
        d2._maxfilelength = 9
        d2.openFile('aap', 'w').close()
        self.assertEquals(['6C6F6E6@/@732.616@/@170', '6C6F6E6@/@76E616D@/@65.6161@/@70'], self._listdir(self._basedir))
        d.removeFile('aap')
        self.assertEquals(['@732.616@'], listdir(join(self._basedir, '6C6F6E6@')))
        
        
    def testRemoveWithLongFilename(self):
        d = self.createDirectory('long')
        d._maxfilelength = 9
        d.openFile('aap', 'w').close()
        self.assertEquals(['6C6F6E6@/@7.61617@/@0'], self._listdir(self._basedir))
        d.renameFile('aap', 'noot')
        self.assertEquals(['@7.6E6F6@'], listdir(join(self._basedir, '6C6F6E6@')))
        
