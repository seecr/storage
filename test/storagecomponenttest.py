# -*- coding: utf-8 -*-
## begin license ##
#
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance.
#
# Copyright (C) 2007-2009 SURF Foundation. http://www.surf.nl
# Copyright (C) 2007 SURFnet. http://www.surfnet.nl
# Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
# Copyright (C) 2007-2009 Stichting Kennisnet Ict op school. http://www.kennisnetictopschool.nl
# Copyright (C) 2011-2012, 2016 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://stichting.bibliotheek.nl
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

from seecr.test import SeecrTestCase

from storage.storagecomponent import StorageComponent, DefaultStrategy, HashDistributeStrategy
from cStringIO import StringIO
from weightless.core import compose, consume
from os.path import join


class StorageComponentTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)

        self.storageComponent = StorageComponent(self.tempdir)
        self.storage = self.storageComponent._storage

    def testAdd(self):
        consume(self.storageComponent.add("id_0", "partName", "The contents of the part"))
        self.assertEquals('The contents of the part', self.storage.get(('id_0', 'partName')).read())

    def testAddEmptyIdentifier(self):
        self.assertRaises(ValueError, lambda: list(compose(self.storageComponent.add("", "part", "data"))))
        self.assertRaises(ValueError, lambda: list(compose(self.storageComponent.add(None, "part", "data"))))

    def testDeleteEmptyIdentifier(self):
        self.assertRaises(ValueError, lambda: list(compose(self.storageComponent.delete(""))))
        self.assertRaises(ValueError, lambda: list(compose(self.storageComponent.delete(None))))
        self.storageComponent.deletePart("","part")

    def testIsAvailableIdAndPart(self):
        sink = self.storage.put(('some:thing:anId-123','somePartName'))
        sink.send('read string')
        sink.close()

        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "somePartName")
        self.assertTrue(hasId)
        self.assertTrue(hasPartName)

    def testIsAvailableId(self):
        sink = self.storage.put(('some:thing:anId-123','somePartName.xml'))
        sink.send('read string')
        sink.close()

        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "nonExistingPart")
        self.assertTrue(hasId)
        self.assertFalse(hasPartName)

    def testIsNotAvailable(self):
        hasId, hasPartName = self.storageComponent.isAvailable("some:thing:anId-123", "nonExistingPart")
        self.assertFalse(hasId)
        self.assertFalse(hasPartName)

    def testWrite(self):
        sink = self.storage.put(('some:thing:anId-123','somePartName'))
        sink.send('read string')
        sink.close()
        stream = StringIO()
        self.storageComponent.write(stream, "some:thing:anId-123", "somePartName")
        self.assertEquals('read string', stream.getvalue())

    def testDeleteParts(self):
        identifier = ('some:thing:anId-123','somePartName')
        self.storage.put(identifier).close()
        self.assertTrue(identifier in self.storage)
        self.storageComponent.deletePart('some:thing:anId-123', 'somePartName')
        self.assertFalse(identifier in self.storage)

    def testDelete(self):
        identifier = ('some:thing:anId-123','somePartName')
        self.storage.put(identifier).close()
        self.assertTrue(identifier in self.storage)
        list(compose(self.storageComponent.delete('some:thing:anId-123')))
        self.assertTrue(identifier in self.storage)

        self.storageComponent = StorageComponent(self.tempdir, partsRemovedOnDelete=['somePartName'])
        self.storage = self.storageComponent._storage
        list(compose(self.storageComponent.delete('some:thing:anId-123')))
        self.assertFalse(identifier in self.storage)

    def testPurgeWithoutIdentifierNotAllowed(self):
        self.assertRaises(ValueError, lambda: StorageComponent(self.tempdir).purge(''))

    def testPurge(self):
        identifier = ('some:thing:anId-123','somePartName')
        self.storage.put(identifier).close()
        self.assertTrue(identifier in self.storage)
        self.storageComponent.purge('some:thing:anId-123')
        self.assertTrue(identifier in self.storage)

        self.storageComponent = StorageComponent(self.tempdir, partsRemovedOnDelete=['somePartName'])
        self.storage = self.storageComponent._storage
        self.storageComponent.purge('some:thing:anId-123')
        self.assertFalse(identifier in self.storage)

        self.storageComponent = StorageComponent(self.tempdir, partsRemovedOnDelete=['somePartName'], partsRemovedOnPurge=['notTherePart'])
        self.storage = self.storageComponent._storage
        self.storageComponent.purge('some:thing:anId-123')
        self.assertFalse(identifier in self.storage)

    def testDeleteNonexisting(self):
        identifier = ('some:thing:anId-123','somePartName.xml')
        self.assertFalse(identifier in self.storage)
        self.storageComponent.deletePart('some:thing:anId-123', 'somePartName')
        self.assertFalse(identifier in self.storage)

    def testEnumerate(self):
        self.assertEquals(set([]), set(self.storageComponent.listIdentifiers()))
        list(compose(self.storageComponent.add('some:thing:anId-123','somePartName', 'data')))
        self.assertEquals(set(['some:thing:anId-123']), set(self.storageComponent.listIdentifiers()))
        list(compose(self.storageComponent.add('some:thing:anId-123','anotherPartName', 'data')))
        self.assertEquals(set(['some:thing:anId-123']), set(self.storageComponent.listIdentifiers()))
        list(compose(self.storageComponent.add('some:thing:anId-122','anotherPartName', 'data')))
        list(compose(self.storageComponent.add('any:thing:anId-123','somePartName', 'data')))
        self.assertEquals(set(['some:thing:anId-123', 'some:thing:anId-122', 'any:thing:anId-123']), set(self.storageComponent.listIdentifiers()))
        self.assertEquals(set(['some:thing:anId-123', 'any:thing:anId-123']), set(self.storageComponent.listIdentifiers('somePartName')))

    def testGlob(self):
        self.assertEquals(set([]), set(self.storageComponent.glob(('some:thing:anId-123', None))))

        list(compose(self.storageComponent.add('some:thing:anId-123','somePartName', 'data')))
        self.assertEquals(set([('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('so', None))))
        self.assertEquals(set([('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('some', None))))
        self.assertEquals(set([('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('some:thing', None))))
        self.assertEquals(set([('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('some:thing:anId', None))))

        list(compose(self.storageComponent.add('some:thing:anId-123','anotherPartName', 'data')))
        self.assertEquals(set([('some:thing:anId-123', 'anotherPartName'), ('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('some:thing:anId', None))))

        list(compose(self.storageComponent.add('some:thing:anId-124','anotherPartName', 'data')))
        self.assertEquals(set([('some:thing:anId-123', 'anotherPartName'), ('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('some:thing:anId-123', None))))
        self.assertEquals(set([('some:thing:anId-123', 'somePartName')]), set(self.storageComponent.glob(('some:thing:anId-123', 'somePartName'))))

        self.assertEquals(set([('some:thing:anId-123', 'anotherPartName'), ('some:thing:anId-124', 'anotherPartName')]), set(self.storageComponent.glob(('some:thing:anId', 'anotherPartName'))))

        list(compose(self.storageComponent.add('some:thing:else-1','anotherPartName', 'data')))
        self.assertEquals(set([('some:thing:anId-123', 'anotherPartName'), ('some:thing:anId-124', 'anotherPartName')]), set(self.storageComponent.glob(('some:thing:anId', 'anotherPartName'))))

    def testObservableNameNotSet(self):
        s = StorageComponent(self.tempdir)
        self.assertEquals(None, s.observable_name())

    def testObservableNameSet(self):
        s = StorageComponent(self.tempdir, name="name")
        self.assertEquals("name", s.observable_name())

    def testDirectoryStrategy(self):
        class TestStrategy:
            @classmethod
            def split(self, (identifier, partname)):
                return identifier.swapcase(), partname.swapcase()
            join = None
        s = StorageComponent(self.tempdir, strategy=TestStrategy)
        list(compose(s.add("AnIdentifier", "Part1", "Contents")))
        self.assertEquals("Contents", open(join(self.tempdir, "aNiDENTIFIER", "pART1")).read())

    def testDirectorySplit(self):
        class TestStrategy:
            @classmethod
            def split(self, (identifier, partname)):
                return tuple(c for c in identifier) + (partname,)
            join = None
        s = StorageComponent(self.tempdir, strategy=TestStrategy)
        list(compose(s.add("id09", "Part1", "Contents")))
        self.assertEquals("Contents", open(join(self.tempdir, "i", "d", "0", "9", "Part1")).read())

    def testDirectoryStrategyJoin(self):
        class TestStrategy:
            @classmethod
            def split(self, (identifier, partname)):
                result = tuple(c for c in identifier)
                return result if not partname else result + (partname,)
            @classmethod
            def join(self, parts):
                return ''.join(parts[:-1]), parts[-1]
        s = StorageComponent(self.tempdir, strategy=TestStrategy)
        list(compose(s.add("id09", "Part1", "Contents")))
        self.assertEquals(["id09"], list(s.listIdentifiers()))

    def testDefaultStrategy(self):
        s = DefaultStrategy
        self.assertEquals(["a", "b", "c"], s.split(("a:b", "c")))
        self.assertEquals(("a:b", "c"), s.join(("a", "b", "c")))
        self.assertEquals(["a", "b"], s.split(("a:b", None)))
        self.assertEquals(["a", "b:c", "d"], s.split(("a:b:c", "d")))
        self.assertEquals(("a:b:c", "d"), s.join(("a", "b:c", "d")))

    def testDefaultStrategyIsDefaultStrategy(self):
        s = StorageComponent(self.tempdir)
        list(compose(s.add("a:b:c", "d", "Hi")))
        self.assertEquals("Hi", open(join(self.tempdir, "a", "b:c", "d")).read())

    def testHashDistributeStrategy(self):
        s = HashDistributeStrategy()
        self.assertEquals(("58", "eb", "58eb8a535f07b1f7b94cd6083e664137301048a7.rdf"), s.split(("AnIdentifier", "rdf")))
        self.assertEquals(("58", "eb", "58eb8a535f07b1f7b94cd6083e664137301048a7.xml"), s.split(("AnIdentifier", "xml")))
        self.assertEquals(("35", "6a", "356a192b7913b04c54574d18c28d46e6395428ab."), s.split(("1", "")))
        self.assertEquals(("35", "6a", "356a192b7913b04c54574d18c28d46e6395428ab."), s.split(("1", None)))

        self.assertRaises(KeyError, lambda: s.join("NA"))

    def testGetData(self):
        consume(self.storageComponent.add("id_0", "partName", "The contents of the part"))
        self.assertEquals('The contents of the part', self.storageComponent.getData(identifier='id_0', name='partName'))
        self.assertRaises(KeyError, lambda: self.storageComponent.getData('does', 'notexist'))
