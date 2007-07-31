
from unittest import TestCase

from storage import Storage
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join, isdir, isfile

class StorageTest(TestCase):
    def setUp(self):
        self._tempdir = join(mkdtemp(), 'storage')
    
    def tearDown(self):
        isdir(self._tempdir) and rmtree(self._tempdir)

    def testInit(self):
        self.assertFalse(isdir(self._tempdir))
        s = Storage(self._tempdir)
        self.assertTrue(isdir(self._tempdir))
        
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
        stream = s.get('mydata')
        self.assertEquals('some data of mine', stream.next())
        
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
        
        s2.put('s1', s1)
        
        self.assertEquals('data', s2.get('s1').get('mydata').next())
        self.assertEquals('data', s1.get('mydata').next())
        
    def testPutStorageAssumesOwnership(self):
        s1 = Storage(join(self._tempdir, 'basedir1'))
        s2 = Storage(join(self._tempdir, 'basedir2'))
        s2.put('s1', s1)
        self.assertFalse(isdir(join(self._tempdir , 'basedir1')))
        
        
     
    # geen storage.basedir niet opgegeven
    # rare tekens,
    # naam te lang
    