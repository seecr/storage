## begin license ##
#
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance.
#
# Copyright (C) 2016 Seecr (Seek You Too B.V.) http://seecr.nl
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

from seecr.test import SeecrTestCase, CallTrace
from storage.storageadapter import StorageAdapter
from weightless.core import retval
from StringIO import StringIO


class StorageAdapterTest(SeecrTestCase):

    def testRetrieveData(self):
        adapter = StorageAdapter()
        observer = CallTrace(returnValues=dict(getStream=StringIO("DATA")))
        adapter.addObserver(observer)

        result = retval(adapter.retrieveData(identifier='id:1', name='partname'))
        self.assertEqual('DATA', result)
        self.assertEqual(['getStream'], observer.calledMethodNames())
        self.assertEqual({'partname': 'partname', 'identifier': 'id:1'}, observer.calledMethods[0].kwargs)

    def testGetData(self):
        adapter = StorageAdapter()
        observer = CallTrace(returnValues=dict(getStream=StringIO("DATA")))
        adapter.addObserver(observer)

        result = adapter.getData(identifier='id:1', name='partname')
        self.assertEqual('DATA', result)
        self.assertEqual(['getStream'], observer.calledMethodNames())
        self.assertEqual({'partname': 'partname', 'identifier': 'id:1'}, observer.calledMethods[0].kwargs)