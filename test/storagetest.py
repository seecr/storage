# -*- encoding: UTF-8
## begin license ##
#
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance.
#
# Copyright (C) 2006-2010 Seek You Too B.V. (CQ2) http://www.cq2.nl
# Copyright (C) 2011-2012 Seecr (Seek You Too B.V.) http://seecr.nl
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

from storage import Storage
from storage.storage import DirectoryNotEmptyError
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join, isdir, isfile
from os import getcwd, listdir, stat
import subprocess

from stat import ST_MODE, S_IRUSR, S_IWUSR, S_IXUSR, S_IRGRP, S_IXGRP, S_IROTH, S_IXOTH


class StorageTest(TestCase):
    def setUp(self):
        self._tempdir = mkdtemp()

    def tearDown(self):
        isdir(self._tempdir) and rmtree(self._tempdir)

    def testInit(self):
        myStorageDir = join(self._tempdir, 'myStorage')
        self.assertFalse(isdir(myStorageDir))
        s = Storage(myStorageDir)
        self.assertTrue(isdir(myStorageDir))

    def testPutEmptyFile(self):
        s = Storage(self._tempdir)
        s.put('mydata').close()
        expectedFilename = join(self._tempdir, 'mydata')
        self.assertTrue(isfile(expectedFilename))

    def testPutData(self):
        s = Storage(self._tempdir)
        sink = s.put('mydata')
        sink.send('some data of mine')
        sink.close()
        expectedFilename = join(self._tempdir, 'mydata')
        with open(expectedFilename) as f:
            self.assertEqual('some data of mine', f.read())

    def testGetData(self):
        s = Storage(self._tempdir)
        sink = s.put('mydata')
        sink.send('some data of mine')
        sink.close()
        self.assertTrue('mydata' in s)
        stream = s.get('mydata')
        self.assertEqual('some data of mine', next(stream))

    def testGetNotExistingData(self):
        s = Storage(self._tempdir)
        self.assertFalse('name' in s)
        try:
            s.get('name')
            self.fail()
        except KeyError as k:
            self.assertEqual("'name'", str(k))

    def testGetAllData(self):
        s = Storage(self._tempdir)
        sink = s.put('mydata')
        sink.send('some data of mine')
        sink.send('some more data of mine')
        sink.close()
        data = []
        stream = s.get('mydata')
        for block in stream:
            data.append(block)
        self.assertEqual(['some data of minesome more data of mine'], data)

    def testPutStorage(self):
        s1 = Storage(join(self._tempdir, 'basedir1'))
        s2 = Storage(join(self._tempdir, 'basedir2'))
        sink = s1.put('mydata')
        sink.send('data')
        sink.close()

        newStorage = s2.put('s1', s1)

        self.assertEqual('data', next(s2.get('s1').get('mydata')))
        self.assertEqual('data', next(s1.get('mydata')))
        self.assertEqual('data', next(newStorage.get('mydata')))

    def testPutStorageChangesName(self):
        s1 = Storage(join(self._tempdir, 'basedir1'))
        s2 = Storage(join(self._tempdir, 'basedir2'))
        self.assertEqual('basedir1', s1.name)
        self.assertEqual('basedir2', s2.name)
        s2.put('s1', s1)
        self.assertEqual('s1', s1.name)


    def testPutStorageAssumesOwnership(self):
        s1 = Storage(join(self._tempdir, 'basedir1'))
        s2 = Storage(join(self._tempdir, 'basedir2'))
        s2.put('s1', s1)
        self.assertFalse(isdir(join(self._tempdir , 'basedir1')))

    def testPutFileOverStorageFails(self):
        s = Storage(self._tempdir)
        s.put('name', Storage())
        try:
            s.put('name')
            self.fail()
        except KeyError as e:
            self.assertEqual("'Key already exists: name'", str(e))

    def testPutStorageOverAFileFails(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        try:
            s.put('name', Storage())
            self.fail()
        except KeyError as e:
            self.assertEqual("'Key already exists: name'", str(e))

    def testPutStorageOverEmptyStorage(self):
        s = Storage(self._tempdir)
        s.put('name', Storage())
        s.put('name', Storage())

    def testPutStorageOverStorageFails(self):
        s = Storage(self._tempdir)
        s.put('name', Storage()).put('sub').close()
        try:
            s.put('name', Storage())
            self.fail()
        except KeyError as e:
            self.assertEqual("'Key already exists: name'", str(e))

    def testCreateTempStorage(self):
        stemp = Storage()
        s = Storage(self._tempdir)
        sink = stemp.put('mydata')
        sink.send('data')
        sink.close()
        s.put('mystore', stemp)
        self.assertEqual('data', next(s.get('mystore').get('mydata')))

    def testStrangeCharactersInName(self):
        self.assertName('~!@# $%^&*()\t_+\\\f\n\/{}[-]ç«»\'´`äëŝÄ')
        self.assertName('---------')
        self.assertName('sudo rm -rf /*')
        self.assertName('version,v')

    def assertName(self, name):
        s = Storage(self._tempdir)
        sink = s.put(name)
        sink.send('data')
        sink.close()
        self.assertEqual('data', next(s.get(name)))

    def testNameTooLong(self):
        s = Storage()
        try:
            s.put('long'*200)
            self.fail()
        except KeyError as e:
            self.assertEqual("'Name too long: " + "long" * 200 + "'", str(e))

    def testEmptyName(self):
        s = Storage()
        try:
            s.put('')
            self.fail()
        except KeyError as e:
            self.assertEqual("'Empty name'", str(e))

    def testEmptyNameStorage(self):
        s = Storage()
        try:
            s.put('', Storage())
            self.fail()
        except KeyError as e:
            self.assertEqual("'Empty name'", str(e))

    def testNameTooLongForStorage(self):
        s = Storage()
        s2 = Storage()
        try:
            s.put('long'*200, s2)
            self.fail()
        except KeyError as e:
            self.assertEqual("'Name too long: " + "long" * 200 + "'", str(e))

    def testPutStorageInSameStorage(self):
        s1 = Storage(join(self._tempdir, 'samedir'))
        s2 = Storage(join(self._tempdir, 'samedir'))
        try:
            s1.put('other', s2)
            self.fail()
        except ValueError as e:
            self.assertEqual("Cannot put Storage inside itself.", str(e))

    def testPutStorageInOtherStorage(self):
        s1 = Storage(join(self._tempdir, 'samedir'))
        s2 = Storage()
        s1.put('sub', s2)
        try:
            s2.put('subsub', s1)
            self.fail()
        except ValueError as e:
            self.assertEqual("Cannot put Storage inside itself.", str(e))

    def testDefaultsToNoRevisionControl(self):
        s = Storage()
        result = s.put('name').close()
        self.assertEqual(None, result)

    def testDeleteFile(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        self.assertTrue(isfile(join(self._tempdir, 'name')))
        s.delete('name')
        self.assertFalse(isfile(join(self._tempdir, 'name')))

    def testDeleteStorage(self):
        s = Storage(self._tempdir)
        substore = Storage()
        substore.put('name').close()
        s.put('sub', substore)
        s.delete('sub')
        self.assertFalse(isdir(join(self._tempdir, 'sub')))

    def testDeleteNonExisting(self):
        try:
            s = Storage()
            s.delete('name')
            self.fail()
        except KeyError as e:
            self.assertEqual("'name'", str(e))

    def testPurgeStorage(self):
        s = Storage(self._tempdir)
        substore = Storage()
        substore.put('name').close()
        s.put('sub', substore)
        self.assertRaises(DirectoryNotEmptyError, lambda: s.purge('sub'))
        self.assertTrue(isdir(join(self._tempdir, 'sub')))

        substore.purge('name')
        s.purge('sub')
        self.assertFalse(isdir(join(self._tempdir, 'sub')))

    def testPurgeNonExisting(self):
        try:
            s = Storage()
            s.purge('sub')
        except KeyError as e:
            self.assertEqual("'sub'", str(e))

    def testEnumerateEmptyThing(self):
        s = Storage(self._tempdir, )
        self.assertEqual([], list(s))

    def testEnumerateOneFile(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        allnames = [item.name for item in s]
        self.assertEqual(['name'], allnames)

    def testEnumerateFilesWithStrangeNames(self):
        def create(storage, name):
            storage.put(name).close()
        self.assertEnumerateName('~!@# $%^&*()\t_+\\\f\n\/{}[-]ç«»\'´`äëŝÄ', create)
        self.assertEnumerateName('---------', create)
        self.assertEnumerateName('sudo rm -rf /*', create)
        self.assertEnumerateName('version,v', create)
        self.assertEnumerateName('..', create)
        self.assertEnumerateName('.', create)

    def testEnumerateStorageWithStrangeNames(self):
        def create(storage, name):
            storage.put(name, Storage())
        self.assertEnumerateName('~!@# $%^&*()\t_+\\\f\n\/{}[-]ç«»\'´`äëŝÄ', create)
        self.assertEnumerateName('---------', create)
        self.assertEnumerateName('sudo rm -rf /*', create)
        self.assertEnumerateName('version,v', create)
        self.assertEnumerateName('..', create)
        self.assertEnumerateName('.', create)

    def assertEnumerateName(self, name, create):
        s = Storage()
        create(s, name)
        self.assertEqual([name], [item.name for item in s])

    def testEnumerateMultipleNames(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        s.put('name2').close()
        allnames = [item.name for item in s]
        self.assertEqual(set(['name', 'name2']), set(allnames))

    def testEnumerateWithSubstorage(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        sub = Storage()
        s.put('sub', sub)
        self.assertEqual(set(['name', 'sub']), set([item.name for item in s]))

    def testEnumerationDeliversObjectReadyForWork(self):
        s = Storage(self._tempdir)
        sink = s.put('name')
        sink.send('data')
        sink.close()
        allitems = list(s)
        self.assertEqual(1, len(allitems))
        item1 = allitems[0]
        self.assertEqual('name', item1.name)
        self.assertEqual('data', ''.join(item1))

    def testNiceNames(self):
        s = Storage(self._tempdir)
        s.put('name.xml').close()
        self.assertTrue(isfile(join(self._tempdir, 'name.xml')))

    def testMoveOverDevicesFails(self):
        mydir = join(getcwd(), 'justForOneTest')
        try:
            s = Storage(mydir)
            s.put('test', s.newStorage())
        finally:
            rmtree(mydir)

    def testRandomTempDirectory(self):
        s = Storage()
        def assertHasBit(bit):
            self.assertTrue(stat(s._basedir)[ST_MODE] & bit == bit)

        assertHasBit(S_IRUSR)
        assertHasBit(S_IWUSR)
        assertHasBit(S_IXUSR)
        assertHasBit(S_IRGRP)
        assertHasBit(S_IXGRP)
        assertHasBit(S_IROTH)
        assertHasBit(S_IXOTH)

    def testWriteReadSimultaneously(self):
        s = Storage(self._tempdir)
        sink = s.put('mydata')
        sink.send('firsttimedata')
        sink.close()
        sink2 = s.put("mydata")
        sink2.send("second\n"*12345)
        f = s.get("mydata")
        self.assertEqual("first", f.read(5))
        f.close()
        sink2.send("more")
        sink2.close()
        f = s.get("mydata")
        self.assertEqual("second", f.read(6))
        f.close()
