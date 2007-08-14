
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
