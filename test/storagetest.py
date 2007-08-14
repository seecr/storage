# -*- encoding: UTF-8


from unittest import TestCase

from storage import Storage
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join, isdir, isfile

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
        s.put('mydata')            
        expectedFilename = join(self._tempdir, 'mydata')
        self.assertTrue(isfile(expectedFilename))
        
    def testPutData(self):
        s = Storage(self._tempdir)
        sink = s.put('mydata')            
        sink.send('some data of mine')
        sink.close()
        expectedFilename = join(self._tempdir, 'mydata')
        self.assertEquals('some data of mine', open(expectedFilename).read())
        
    def testGetData(self):
        s = Storage(self._tempdir)
        sink = s.put('mydata')            
        sink.send('some data of mine')
        sink.close()
        self.assertTrue('mydata' in s)
        stream = s.get('mydata')
        self.assertEquals('some data of mine', stream.next())

    def testGetNotExistingData(self):
        s = Storage(self._tempdir)
        self.assertFalse('name' in s)
        try:
            s.get('name')
            self.fail()
        except KeyError, k:
            self.assertEquals("'name'", str(k))
        
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
        self.assertEquals(['some data of minesome more data of mine'], data)
        
    def testPutStorage(self):
        s1 = Storage(join(self._tempdir, 'basedir1'))
        s2 = Storage(join(self._tempdir, 'basedir2'))
        sink = s1.put('mydata')            
        sink.send('data')
        sink.close()
        
        newStorage = s2.put('s1', s1)
        
        self.assertEquals('data', s2.get('s1').get('mydata').next())
        self.assertEquals('data', s1.get('mydata').next())
        self.assertEquals('data', newStorage.get('mydata').next())

    def testPutStorageChangesName(self):
        s1 = Storage(join(self._tempdir, 'basedir1'))
        s2 = Storage(join(self._tempdir, 'basedir2'))
        self.assertEquals('basedir1', s1.name)
        self.assertEquals('basedir2', s2.name)
        s2.put('s1', s1)
        self.assertEquals('s1', s1.name)
        

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
        except KeyError, e:
            self.assertEquals("'Key already exists: name'", str(e))

    def testPutStorageOverAFileFails(self):
        s = Storage(self._tempdir)
        s.put('name')
        try:
            s.put('name', Storage())
            self.fail()
        except KeyError, e:
            self.assertEquals("'Key already exists: name'", str(e))
        
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
        except KeyError, e:
            self.assertEquals("'Key already exists: name'", str(e))

    def testCreateTempStorage(self):
        stemp = Storage()
        s = Storage(self._tempdir)
        sink = stemp.put('mydata')
        sink.send('data')
        sink.close()
        s.put('mystore', stemp)
        self.assertEquals('data', s.get('mystore').get('mydata').next())

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
        self.assertEquals('data', s.get(name).next())

    def testNameTooLong(self):
        s = Storage()
        try:
            s.put('long'*200)
            self.fail()
        except KeyError, e:
            self.assertEquals("'Name too long: " + "long" * 200 + "'", str(e))

    def testEmptyName(self):
        s = Storage()
        try:
            s.put('')
            self.fail()
        except KeyError, e:
            self.assertEquals("'Empty name'", str(e))
    
    def testEmptyNameStorage(self):
        s = Storage()
        try:
            s.put('', Storage())
            self.fail()
        except KeyError, e:
            self.assertEquals("'Empty name'", str(e))

    def testNameTooLongForStorage(self):
        s = Storage()
        s2 = Storage()
        try:
            s.put('long'*200, s2)
            self.fail()
        except KeyError, e:
            self.assertEquals("'Name too long: " + "long" * 200 + "'", str(e))

    def testPutStorageInSameStorage(self):
        s1 = Storage(join(self._tempdir, 'samedir'))
        s2 = Storage(join(self._tempdir, 'samedir'))
        try:
            s1.put('other', s2)
            self.fail()
        except ValueError, e:
            self.assertEquals("Cannot put Storage inside itself.", str(e))

    def testPutStorageInOtherStorage(self):
        s1 = Storage(join(self._tempdir, 'samedir'))
        s2 = Storage()
        s1.put('sub', s2)
        try:
            s2.put('subsub', s1)
            self.fail()
        except ValueError, e:
            self.assertEquals("Cannot put Storage inside itself.", str(e))

    def testInitialRevision(self):
        s = Storage()
        sink = s.put('name')
        sink.send('data')
        oldrevision, newrevision = sink.close()
        self.assertEquals(0, oldrevision)
        self.assertEquals(1, newrevision)

    def testNewRevision(self):
        s = Storage()
        sink = s.put('name')
        sink.send('data')
        sink.close()
        sink = s.put('name')
        sink.send('otherdata')
        oldrevision, newrevision = sink.close()
        self.assertEquals(1, oldrevision)
        self.assertEquals(2, newrevision)

    def testSameRevision(self):
        s = Storage()
        sink = s.put('name')
        sink.send('data')
        sink.close()
        sink = s.put('name')
        sink.send('data')
        oldrevision, newrevision = sink.close()
        self.assertEquals(1, oldrevision)
        self.assertEquals(1, newrevision)

    def testDeleteFile(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        s.delete('name')
        # delete also removes versions.
        oldrev, newrev = s.put('name').close()
        self.assertEquals(0, oldrev)
        self.assertEquals(1, newrev)

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
        except KeyError, e:
            self.assertEquals("'name'", str(e))

    def testEnumerateEmptyThing(self):
        s = Storage(self._tempdir)
        self.assertEquals([], list(s))

    def testEnumerateOneFile(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        allnames = [item.name for item in s]
        self.assertEquals(['name'], allnames)
            
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
        self.assertEquals([name], [item.name for item in s])

    def testEnumerateMultipleNames(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        s.put('name2').close()
        allnames = [item.name for item in s]
        self.assertEquals(set(['name', 'name2']), set(allnames))

    def testEnumerateWithSubstorage(self):
        s = Storage(self._tempdir)
        s.put('name').close()
        sub = Storage()
        s.put('sub', sub)
        self.assertEquals(set(['name', 'sub']), set([item.name for item in s]))

    def testEnumerationDeliversObjectReadyForWork(self):
        s = Storage(self._tempdir)
        sink = s.put('name')
        sink.send('data')
        sink.close()
        allitems = list(s)
        self.assertEquals(1, len(allitems))
        item1 = allitems[0]
        self.assertEquals('name', item1.name)
        self.assertEquals('data', ''.join(item1))

    def testNiceNames(self):
        s = Storage(self._tempdir)
        s.put('name.xml').close()
        self.assertTrue(isfile(join(self._tempdir, 'name.xml')))
        
        
        

    #TODO

    # Probably the following are YAGNI:
    # move
    # move over existing ...
    # move non existing
    # move to substorage??
