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

from storage import Storage
from os.path import isfile

def catchKeyError(message, aMethod):
    def wrapper(self, name):
        try:
            return aMethod(self, name)
        except KeyError, e:
            raise HierarchicalStorageError(message % str(name))
    return wrapper

catchPutError = lambda aMethod: catchKeyError("Name '%s' not allowed.", aMethod)
catchDoesNotExistError = lambda aMethod: catchKeyError("Name '%s' does not exist.", aMethod)
    
class HierarchicalStorage:
    def __init__(self, storage, split = lambda x:(x,)):
        self._storage = storage
        self._split = split

    @catchPutError
    def put(self, name):
        splitted = self._split(name)
        storeHere = self._storage
        for storeName in splitted[:-1]:
            try:
                storeHere = storeHere.get(storeName)
            except KeyError:
                storeHere = storeHere.put(storeName, Storage())
        return storeHere.put(splitted[-1])

    @catchDoesNotExistError
    def get(self, name):
        splitted = self._split(name)
        store = self._storage
        for storeName in splitted[:-1]:
            store = store.get(storeName)
        result = store.get(splitted[-1])
        return result

    @catchDoesNotExistError
    def delete(self, name):
        splitted = self._split(name)
        store = self._storage
        for storeName in splitted[:-1]:
            store = store.get(storeName)
        store.delete(splitted[-1])

    def __contains__(self, name):
        splitted = self._split(name)
        store = self._storage
        try:
            for storeName in splitted[:-1]:
                store = store.get(storeName)
        except KeyError:
            return False
        return splitted[-1] in store


class HierarchicalStorageError(Exception):
    pass
