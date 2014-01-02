# -*- coding: utf-8 -*-
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

from .storage import File, DirectoryNotEmptyError

def catchKeyError(message, aMethod):
    def wrapper(self, name):
        try:
            return aMethod(self, name)
        except KeyError:
            raise HierarchicalStorageError(message % repr(name))
    return wrapper

def catchPutKeyError(message, aMethod):
    def wrapper(self, name):
        try:
            return aMethod(self, name)
        except KeyError as e:
            raise HierarchicalStorageError("%s %s" % (message % repr(name), str(e)))
    return wrapper

catchPutError = lambda aMethod: catchPutKeyError("Name %s not allowed:", aMethod)
catchDoesNotExistError = lambda aMethod: catchKeyError("Name %s does not exist.", aMethod)

class HierarchicalStorage(object):
    def __init__(self, storage, split = lambda x:(x,), join=''.join):
        self._storage = storage
        self._split = split
        self._join = join

    @catchPutError
    def put(self, name):
        splitted = self._split(name)
        storeHere = self._storage
        for storeName in splitted[:-1]:
            try:
                storeHere = storeHere.get(storeName)
            except KeyError:
                storeHere = storeHere.put(storeName, self._storage.newStorage())
        return storeHere.put(splitted[-1])

    @catchDoesNotExistError
    def get(self, name):
        splitted = self._split(name)
        result = self._storage
        for storeName in splitted[:-1]:
            result = result.getStorage(storeName)
        result = result.get(splitted[-1])
        return result

    @catchDoesNotExistError
    def getFile(self, name):
        """Returns a file without checking for existence!"""
        splitted = self._split(name)
        result = self._storage
        for storeName in splitted[:-1]:
            result = result.getStorage(storeName)
        result = result.getFile(splitted[-1])
        return result

    @catchDoesNotExistError
    def delete(self, name):
        splitted = self._split(name)
        store = self._storage
        for storeName in splitted[:-1]:
            store = store.get(storeName)
        store.delete(splitted[-1])

    @catchDoesNotExistError
    def purge(self, name):
        splitted = self._split(name)
        stores = []
        stores.append(self._storage)
        for storeName in splitted[:-1]:
            stores.append(stores[-1].get(storeName))
        for i, storeName in enumerate(reversed(splitted)):
            try:
                stores[-i-1].purge(storeName)
            except DirectoryNotEmptyError:
                break

    def __contains__(self, name):
        try:
            self.get(name)
            return True
        except HierarchicalStorageError:
            return False

    def __iter__(self):
        SKIP_BASENAME = 1
        for item in self.allFilenamesIn(self._storage):
            yield self._join(item[SKIP_BASENAME:])

    def allFilenamesIn(self, storageOrFile):
        if type(storageOrFile) == File:
            yield [storageOrFile.name]
        else:
            aStorage = storageOrFile
            for storageOrFile in aStorage:
                for fileName in self.allFilenamesIn(storageOrFile):
                    yield [aStorage.name] + fileName

    def glob(self, pattern):
        splitted = self._split(pattern)
        store = self._storage
        eatenName = []
        for storeName in splitted:
            if storeName == '':
                break
            if storeName in store:
                eatenName.append(storeName)
                store = store.get(storeName)

        for item in self.allFilenamesIn(store):
            yield self._join(eatenName + item[1:])

class HierarchicalStorageError(Exception):
    pass
