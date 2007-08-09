
from storage import Storage
from os.path import isfile

def catchError(aMethod):
    def wrapper(self, name):
        try:
            return aMethod(self, name)
        except KeyError, e:
            raise FacadeError("Name '%s' not allowed." % name)
        except IOError, e:
            raise FacadeError("Name '%s' does not exist." % name)
    return wrapper

class Facade:
    def __init__(self, storage, split = lambda x:(x,)):
        self._storage = storage
        self._split = split

    @catchError
    def put(self, name):
        splitted = self._split(name)
        storeHere = self._storage
        for storeName in splitted[:-1]:
            try:
                storeHere = storeHere.put(storeName, Storage())
            except KeyError:
                storeHere = storeHere.get(storeName)
        return storeHere.put(splitted[-1])

    @catchError
    def get(self, name):
        splitted = self._split(name)
        store = self._storage
        for storeName in splitted[:-1]:
            store = store.get(storeName)
        result = store.get(splitted[-1])
        result.mode #side-effects, if not file, raise IOError
        return result



class FacadeError(Exception):
    pass