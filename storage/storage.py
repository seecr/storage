# -*- coding: utf-8 -*-
## begin license ##
#
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance.
#
# Copyright (C) 2006-2010 Seek You Too B.V. (CQ2) http://www.cq2.nl
# Copyright (C) 2011-2013 Seecr (Seek You Too B.V.) http://seecr.nl
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

from os.path import join, isdir, basename, isfile
from os import makedirs, rename, remove, listdir, rmdir
from tempfile import gettempdir
from errno import ENAMETOOLONG, EINVAL, ENOENT, EISDIR, ENOTDIR, ENOTEMPTY, EEXIST
from shutil import rmtree
import re
from random import choice

from escaping import escapeFilename, unescapeFilename


defaultTempdir = gettempdir()



class DirectoryNotEmptyError(Exception):
    pass


class Storage(object):
    def __init__(self, basedir=None, tempdir=defaultTempdir, checkExists=True):
        if not basedir:
            self._basedir = self._createRandomDirectory(tempdir=tempdir)
            self._own = True
        else:
            self._basedir = basedir
            self._own = False
            if checkExists:
                isdir(self._basedir) or makedirs(self._basedir)
        self.name = unescapeFilename(basename(self._basedir))

    def __del__(self):
        if self._own:
            rmtree(self._basedir)

    def _createRandomDirectory(self, tempdir=defaultTempdir):
        randomName = '.' + ''.join([choice(CHARS_FOR_RANDOM) for i in range(0,6)])
        fullname = join(tempdir, randomName)
        makedirs(fullname)
        return fullname

    def newStorage(self):
        return Storage(tempdir = self._basedir)

    def _transferOwnership(self, path):
        rename(self._basedir, path)
        self._basedir = path
        self._own = False
        self.name = unescapeFilename(basename(self._basedir))

    def put(self, name, aStorage = None):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeFilename(name))
        try:
            if aStorage:
                aStorage._transferOwnership(path)
                return aStorage
            else:
                return Sink(path)
        except (OSError,IOError) as e:
            if e.errno == ENAMETOOLONG:
                raise KeyError('Name too long: ' + name)
            elif e.errno == EINVAL:
                raise ValueError('Cannot put Storage inside itself.')
            elif e.errno in [ENOTDIR, EISDIR, ENOTEMPTY, EEXIST]:
                raise KeyError('Key already exists: ' + name)
            raise

    def get(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeFilename(name))
        if isdir(path):
            return Storage(path)
        elif isfile(path):
            return File(path)
        raise KeyError(name)

    def getStorage(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeFilename(name))
        return Storage(path, checkExists=False)

    def getFile(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeFilename(name))
        return File(path)

    def __contains__(self, name):
        path = join(self._basedir, escapeFilename(name))
        return isfile(path) or isdir(path)

    def delete(self, name):
        path = join(self._basedir, escapeFilename(name))
        try:
            if isdir(path):
                rmtree(path)
            else:
                remove(path)
        except OSError as e:
            if e.errno == ENOENT:
                raise KeyError(name)
            raise

    def purge(self, name):
        path = join(self._basedir, escapeFilename(name))
        try:
            if isdir(path):
                try:
                    rmdir(path)
                except OSError as e:
                    if e.errno == ENOTEMPTY:
                        raise DirectoryNotEmptyError(name)
                    raise
            else:
                remove(path)
        except OSError as e:
            if e.errno == ENOENT:
                raise KeyError(name)
            raise

    def __iter__(self):
        for item in listdir(self._basedir):
            yield self.get(unescapeFilename(item))

class Sink(object):
    def __init__(self, path):
        self._openpath = path
        if isfile(path):
            self._openpath += ',t'
        fd = open(self._openpath, 'w')
        self.send = fd.write
        self.name = path
        self.fileno = fd.fileno
        self._close = fd.close

    def close(self):
        self._close()
        rename(self._openpath, self.name)

class File(object):
    def __init__(self, path):
        self.path = path
        self.name = unescapeFilename(basename(path))
        self.__file = None

    def _file(self):
        if self.__file == None:
            self.__file = open(self.path)
        return self.__file

    def __getattr__(self, attr):
        return getattr(self._file(), attr)

    def __iter__(self):
        return self

    def __next__(self):
        data = self._file().read(4096)
        if not data:
            self.close()
            raise StopIteration
        return data

    def close(self):
        self.__file.close()

CHARS_FOR_RANDOM = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890'

