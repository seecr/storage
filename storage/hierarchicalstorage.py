
from storage import Storage
from os.path import isfile

def catchPutError(aMethod):
    def wrapper(self, name):
        try:
            return aMethod(self, name)
        except KeyError, e:
            raise FacadeError("Name '%s' not allowed." % name)
    return wrapper

def catchGetError(aMethod):
    def wrapper(self, name):
        try:
            return aMethod(self, name)
        except KeyError, e:
            raise FacadeError("Name '%s' does not exist." % name)
    return wrapper

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
                storeHere = storeHere.put(storeName, Storage())
            except KeyError:
                storeHere = storeHere.get(storeName)
        return storeHere.put(splitted[-1])

    @catchGetError
    def get(self, name):
        splitted = self._split(name)
        store = self._storage
        for storeName in splitted[:-1]:
            store = store.get(storeName)
        result = store.get(splitted[-1])
        return result

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