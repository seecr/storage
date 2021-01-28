## begin license ##
#
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance.
#
# Copyright (C) 2006-2010 Seek You Too B.V. (CQ2) http://www.cq2.nl
# Copyright (C) 2011-2012, 2020-2021 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2020-2021 Data Archiving and Network Services https://dans.knaw.nl
# Copyright (C) 2020-2021 SURF https://www.surf.nl
# Copyright (C) 2020-2021 Stichting Kennisnet https://www.kennisnet.nl
# Copyright (C) 2020-2021 The Netherlands Institute for Sound and Vision https://beeldengeluid.nl
#
# This file is part of "Storage"
#
# "Storage" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Storage" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Storage"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from unittest import TestCase
from tempfile import mkdtemp
from shutil import rmtree
from os.path import isdir, join
from os import getcwd

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
        self.assertEqual('somedata', next(s.get('name')))

    def testPutStorageNotAllowed(self):
        f = HierarchicalStorage(Storage(self._tempdir))
        try:
            f.put('sub', Storage())
            self.fail()
        except TypeError as e:
            pass

    def testGet(self):
        s = Storage(self._tempdir)
        sink = s.put('name')
        sink.send('somedata')
        sink.close()

        f = HierarchicalStorage(s)
        self.assertEqual('somedata', next(f.get('name')))

    def testPutWithSplitMethod(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda x:x.split('.'))
        sink = f.put('one.two.three')
        sink.send('data')
        sink.close()
        self.assertEqual('data', next(s.get('one').get('two').get('three')))

    def testGetWithSplitMethod(self):
        s = Storage(self._tempdir)
        sink = s.put('one', Storage()).put('two', Storage()).put('three')
        sink.send('data')
        sink.close()
        f = HierarchicalStorage(s, split=lambda x:x.split('.'))
        self.assertEqual('data', next(f.get('one.two.three')))

    def testPutOverAnExistingStorage(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda x:x.split('.'))
        sink = f.put('one.three')
        sink.send('data3')
        sink.close()
        sink = f.put('one.two')
        sink.send('data2')
        sink.close()
        self.assertEqual('data2', next(f.get('one.two')))
        self.assertEqual('data3', next(f.get('one.three')))

    def testPutWithProblemSplit(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda x:('first','','second'))
        try:
            sink = f.put('one..two')
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name 'one..two' not allowed: 'Empty name'", str(e))
        try:
            sink = f.put(('one', 'two'))
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name ('one', 'two') not allowed: 'Empty name'", str(e))

    def testGetWithProblemSplit(self):
        s = Storage(self._tempdir)
        s.put('first', Storage()).put('second').close()
        f = HierarchicalStorage(s, split=lambda x:('first','','second'))
        try:
            sink = f.get('one..two')
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name 'one..two' does not exist.", str(e))

    def testGetNonExisting(self):
        self.assertGetNameError('name')
        self.assertGetNameError('name.name')

    def assertGetNameError(self, name):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split = lambda x:x.split('.'))
        try:
            sink = f.get(name)
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name '%s' does not exist." % name, str(e))

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
        self.assertTrue('one' in f)
        self.assertFalse('sub' in f)

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
        self.assertTrue(('sub',) in f)

    def testPurgeFile(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        f.put('name').close()
        self.assertTrue('name' in f)
        f.purge('name')
        self.assertFalse('name' in f)

    def testPurgeSplittedFileWithDirectory(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split= lambda x: x)
        f.put(('sub', '00', 'ca', 'name')).close()
        self.assertTrue(('sub', '00', 'ca', 'name') in f)
        f.purge(('sub', '00', 'ca', 'name'))
        self.assertFalse(('sub', '00', 'ca', 'name') in f)
        self.assertFalse(('sub', '00', 'ca') in f)
        self.assertFalse(('sub', '00') in f)
        self.assertFalse(('sub',) in f)

    def testPurgeSplittedFileWithOnlyEmptyDirectories(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split= lambda x: x)
        f.put(('sub', '00', 'ca', 'name')).close()
        f.put(('sub', '01', 'ca', 'name')).close()
        self.assertTrue(('sub', '00', 'ca', 'name') in f)
        self.assertTrue(('sub', '01', 'ca', 'name') in f)
        f.purge(('sub', '00', 'ca', 'name'))
        self.assertFalse(('sub', '00', 'ca', 'name') in f)
        self.assertFalse(('sub', '00', 'ca') in f)
        self.assertFalse(('sub', '00') in f)
        self.assertTrue(('sub',) in f)
        self.assertTrue(('sub', '01', 'ca', 'name') in f)

    def testPurgeNonExistingFile(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        try:
            sink = f.purge('nonExisting')
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name 'nonExisting' does not exist.", str(e))

    def testNonStringNamesShowUpCorrectInError(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split = lambda x: x)
        try:
            f.get(('sub','name'))
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name ('sub', 'name') does not exist.", str(e))

    def testDeleteNonExisting(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        try:
            f.delete('not here')
            self.fail()
        except HierarchicalStorageError as e:
            self.assertEqual("Name 'not here' does not exist.", str(e))

    def testIter(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s)
        f.put('some.name.0').close()
        f.put('some.name.1').close()
        l = list(f)
        self.assertEqual(set(['some.name.0', 'some.name.1']), set(l))

    def testIterWithSplit(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda s: s.split('.'), join=lambda l: ".".join(l))
        f.put('something').close()
        f.put('left.right').close()
        f.put('left.middle.right').close()
        l = list(f)
        self.assertEqual(set(['something', 'left.right', 'left.middle.right']), set(l))

    def testGlobEmptyName(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda s: s.split('.'), join=lambda l: ".".join(l))
        f.put('a.b').close()
        f.put('a.c.file_one').close()
        f.put('a.c.file_two').close()
        f.put('a.d.a').close()

        self.assertEqual(set(['a.b', 'a.c.file_one', 'a.c.file_two', 'a.d.a']), set(list(f.glob(''))))


    def testGlobStorage(self):
        s = Storage(self._tempdir)
        f = HierarchicalStorage(s, split=lambda s: s.split('.'), join=lambda l: ".".join(l))
        f.put('a.b').close()
        f.put('a.c.file_one').close()
        f.put('a.c.file_two').close()
        f.put('a.d.a').close()

        self.assertEqual(set(['a.c.file_one', 'a.c.file_two']), set(list(f.glob('a.c.file'))))
        self.assertEqual(set(['a.b', 'a.c.file_one', 'a.c.file_two', 'a.d.a']), set(list(f.glob('a'))))
        self.assertEqual(set(['a.b']), set(list(f.glob('a.b'))))

        f.put('a.c.file_three').close()
        self.assertEqual(set(['a.c.file_one', 'a.c.file_two', 'a.c.file_three']), set(list(f.glob('a.c.file_t'))))
        self.assertEqual(set(['a.c.file_one', 'a.c.file_two', 'a.c.file_three']), set(list(f.glob('a.c'))))

    def testBasePathOnDifferentDeviceThenTmp(self):
        mydir = join(getcwd(), 'justForOneTest')
        try:
            s = Storage(mydir)
            f = HierarchicalStorage(s, split=lambda x:x)
            f.put(('sub','dir','here')).close()
        finally:
            rmtree(mydir)

    def testGetFile(self):
        s = Storage(self._tempdir)
        h = HierarchicalStorage(s, split=lambda s: s.split('.'))
        ab_file = h.put('a.b')
        ab_file.send('A.B')
        ab_file.close()
        ab = h.getFile('a.b')
        a_notexist = h.getFile('a.notexist')
        a = h.getFile('a')
        notexist = h.getFile('notexist')
        self.assertEqual('A.B', ''.join(ab))
        self.assertRaises(IOError, lambda: list(a_notexist))
        self.assertRaises(IOError, lambda: list(a))
        self.assertRaises(IOError, lambda: list(notexist))



