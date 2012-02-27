# -*- coding: utf-8 -*-
## begin license ##
# 
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance. 
# 
# Copyright (C) 2006-2010 Seek You Too B.V. (CQ2) http://www.cq2.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# Copyright (C) 2012 Stichting Kennisnet http://www.kennisnet.nl
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
from subprocess import Popen, PIPE
from tempfile import gettempdir
from errno import ENAMETOOLONG, EINVAL, ENOENT, EISDIR, ENOTDIR, ENOTEMPTY
from shutil import rmtree
import re
from random import choice

defaultTempdir = gettempdir()
BAD_CHARS = map(chr, range(32)) + ['/', '%', ',']
FIND_BAD_CHARS = re.compile('(^\.|' + '|'.join(BAD_CHARS)+')')
CHAR_TO_HEX = lambda x: '%%%02X' % ord(x.group(1))

HEX_TO_CHAR = lambda x:chr(int(x.group(1),16))
REVERSE_BAD_CHARS = re.compile('%([0-9A-F]{2})')

BAD_BASH_CHARS = ['!','@','$','&','<','>', '|', '(',')',';', '*', '`', '\'', '"', '\\', ' ']

CHARS_FOR_RANDOM = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890'

def escapeName(name):
    return FIND_BAD_CHARS.sub(CHAR_TO_HEX, name)

def unescapeName(name):
    return REVERSE_BAD_CHARS.sub(HEX_TO_CHAR, name)

def bashEscape(name):
    return ''.join((char in BAD_BASH_CHARS and '\\' + char or char for char in name))


class DirectoryNotEmptyError(Exception):
    pass


class Storage(object):
    def __init__(self, basedir=None, revisionControl=False, tempdir=defaultTempdir, checkExists=True):
        if not basedir:
            self._basedir = self._createRandomDirectory(tempdir=tempdir)
            self._own = True
        else:
            self._basedir = basedir
            self._own = False
            if checkExists:
                isdir(self._basedir) or makedirs(self._basedir)
        self._revisionControl = revisionControl
        self.name = unescapeName(basename(self._basedir))

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
        self.name = unescapeName(basename(self._basedir))

    def put(self, name, aStorage = None):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeName(name))
        try:
            if aStorage:
                aStorage._transferOwnership(path)
                aStorage._revisionControl = self._revisionControl
                return aStorage
            else:
                return Sink(path, self._revisionControl)
        except (OSError,IOError), e:
            if e.errno == ENAMETOOLONG:
                raise KeyError('Name too long: ' + name)
            elif e.errno == EINVAL:
                raise ValueError('Cannot put Storage inside itself.')
            elif e.errno in [ENOTDIR, EISDIR, ENOTEMPTY]:
                raise KeyError('Key already exists: ' + name)
            raise

    def get(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeName(name))
        if isdir(path):
            return Storage(path, revisionControl=self._revisionControl)
        elif isfile(path):
            return File(path)
        raise KeyError(name)

    def getStorage(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeName(name))
        return Storage(path, revisionControl=self._revisionControl, checkExists=False)

    def getFile(self, name):
        if not name:
            raise KeyError('Empty name')
        path = join(self._basedir, escapeName(name))
        return File(path)

    def __contains__(self, name):
        path = join(self._basedir, escapeName(name))
        return isfile(path) or isdir(path)

    def delete(self, name):
        path = join(self._basedir, escapeName(name))
        try:
            if isdir(path):
                rmtree(path)
            else:
                remove(path)
                self._revisionControl and remove(path + ',v')
        except OSError, e:
            if e.errno == ENOENT:
                raise KeyError(name)
            raise

    def purge(self, name):
        path = join(self._basedir, escapeName(name))
        try:
            if isdir(path):
                try:
                    rmdir(path)
                except OSError, e:
                    if e.errno == ENOTEMPTY:
                        raise DirectoryNotEmptyError(name)
                    raise
            else:
                remove(path)
                self._revisionControl and remove(path + ',v')
        except OSError, e:
            if e.errno == ENOENT:
                raise KeyError(name)
            raise

    def __iter__(self):
        for item in listdir(self._basedir):
            if not item.endswith(',v'):
                yield self.get(unescapeName(item))

responsePattern = re.compile(r'(?s).*(?P<status>initial|unchanged|new).*?\d+\.(?P<revision1>\d+)[^\d]*(?:\d+\.(?P<revision2>\d+))?')

class Sink(object):
    def __init__(self, path, revisionControl):
        self._openpath = path
        if isfile(path):
            self._openpath += ',t'
        fd = open(self._openpath, 'w')
        self.send = fd.write
        self.name = path
        self.fileno = fd.fileno
        self._close = fd.close
        self._revisionControl = revisionControl

    def close(self):
        self._close()
        rename(self._openpath, self.name)
        if self._revisionControl:
            return self._generateRevision()

    def _generateRevision(self):
        p = Popen(
            ['ci', '-t-storage', '-l', '-mnomesg', bashEscape(self.name)], 
            stdout=PIPE,
            stderr=PIPE)
        response = p.stderr.read()
        result = responsePattern.match(response).groupdict()
        if result['status'] == 'initial':
            return 0, int(result['revision1'])
        if result['status'] == 'unchanged':
            return int(result['revision1']), int(result['revision1'])
        if result['status'] == 'new':
            return int(result['revision2']), int(result['revision1'])

class File(object):
    def __init__(self, path):
        self.path = path
        self.name = unescapeName(basename(path))
        self.__file = None

    def _file(self):
        if self.__file == None:
            self.__file = open(self.path)
        return self.__file

    def __getattr__(self, attr):
        return getattr(self._file(), attr)

    def __iter__(self):
        f = self._file()
        x = f.read(4096)
        while x:
            yield x
            x = f.read(4096)
