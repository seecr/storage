## begin license ##
#
#    Storage stores data in a reliable, extendable filebased storage
#    with great performance.
#    Copyright (C) 2006-2007 Seek You Too B.V. (CQ2) http://www.cq2.nl
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
from tempfile import mkdtemp
from shutil import rmtree
from os.path import isdir

from storage import HierarchicalStorage, Storage, HierarchicalStorageError

class HierarchicalStorageTest(TestCase):
    def setUp(self):
        self._tempdir = mkdtemp()

    def tearDown(self):
        isdir(self._tempdir) and rmtree(self._tempdir)

    def testPut(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        sink = f.put('name')
        sink.send('somedata')
        sink.close()
        self.assertEquals('somedata', s.get('name').next())

    def testPutStorageNotAllowed(self):
        f = HierarchicalStorage(Storage(self._tempdir))
        try:
            f.put('sub', Storage())
            self.fail()
        except TypeError, e:
            pass

    def testGet(self):
        s = Storage(self._tempdir)
        sink = s.put('name')
        sink.send('somedata')
        sink.close()

        f = HierarchicalStorage(s)
        self.assertEquals('somedata', f.get('name').next())

    def testPutWithSplitMethod(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda x:x.split('.'))
        sink = f.put('one.two.three')
        sink.send('data')
        sink.close()
        self.assertEquals('data', s.get('one').get('two').get('three').next())

    def testGetWithSplitMethod(self):
        s = Storage(self._tempdir)
        sink = s.put('one', Storage()).put('two', Storage()).put('three')
        sink.send('data')
        sink.close()
        f = HierarchicalStorage(s, split=lambda x:x.split('.'))
        self.assertEquals('data', f.get('one.two.three').next())

    def testPutOverAnExistingStorage(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda x:x.split('.'))
        sink = f.put('one.three')
        sink.send('data3')
        sink.close()
        sink = f.put('one.two')
        sink.send('data2')
        sink.close()
        self.assertEquals('data2', f.get('one.two').next())
        self.assertEquals('data3', f.get('one.three').next())

    def testPutWithProblemSplit(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda x:('first','','second'))
        try:
            sink = f.put('one..two')
            self.fail()
        except HierarchicalStorageError, e:
            self.assertEquals("Name 'one..two' not allowed.", str(e))

    def testGetWithProblemSplit(self):
        s = Storage(self._tempdir)
        s.put('first', Storage()).put('second').close()
        f = HierarchicalStorage(s, split=lambda x:('first','','second'))
        try:
            sink = f.get('one..two')
            self.fail()
        except HierarchicalStorageError, e:
            self.assertEquals("Name 'one..two' does not exist.", str(e))

    def testGetNonExisting(self):
        self.assertGetNameError('name')
        self.assertGetNameError('name.name')

    def assertGetNameError(self, name):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split = lambda x:x.split('.'))
        try:
            sink = f.get(name)
            self.fail()
        except HierarchicalStorageError, e:
            self.assertEquals("Name '%s' does not exist." % name, str(e))

    def testExists(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        f.put('othername').close()
        self.assertFalse('name' in f)
        self.assertTrue('othername' in f)

    def testExistsWithSplittingUp(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split = lambda x: x.split('.'))
        s.put('one', Storage()).put('two').close()
        self.assertFalse('sub.one' in f)
        self.assertFalse('one.one' in f)
        self.assertTrue('one.two' in f)

    def testDeleteFile(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        f.put('name').close()
        self.assertTrue('name' in f)
        f.delete('name')
        self.assertFalse('name' in f)

    def testDeleteSplittedFile(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split= lambda x: x)
        f.put(('sub','name')).close()
        self.assertTrue(('sub','name') in f)
        f.delete(('sub','name'))
        self.assertFalse(('sub','name') in f)

    def testNonStringNamesShowUpCorrectInError(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split = lambda x: x)
        try:
            f.get(('sub','name'))
            self.fail()
        except HierarchicalStorageError, e:
            self.assertEquals("Name '('sub', 'name')' does not exist.", str(e))

    def testDeleteNonExisting(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        try:
            f.delete('not here')
            self.fail()
        except HierarchicalStorageError, e:
            self.assertEquals("Name 'not here' does not exist.", str(e))

    def testIter(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        f.put('some.name.0').close()
        f.put('some.name.1').close()
        l = list(f)
        self.assertEquals(set(['some.name.0', 'some.name.1']), set(l))

    def testIterWithSplit(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda s: s.split('.'), join=lambda l: ".".join(l))
        f.put('something').close()
        f.put('left.right').close()
        f.put('left.middle.right').close()
        l = list(f)
        self.assertEquals(set(['something', 'left.right', 'left.middle.right']), set(l))


    # TODO
    # get with a Storage ????

    # assert bij Aanmaken HierarchicalStorage dat string == join(split(string)) lijst = split(join(lijst))
    # waarschijnlijk niet gewenst, omdat testdata niet geschikt kan zijn.
    #
    # - put('one') where 'one' is a storage
    # - exists
    # - enumerate Names
