## begin license ##
# 
# "Storage" stores data in a reliable, extendable filebased storage
# with great performance. 
# 
# Copyright (C) 2011 Seecr (Seek You Too B.V.) http://seecr.nl
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

set -e

rm -rf tmp build

python setup.py install --root tmp

export PYTHONPATH=$(find `pwd` -name '*-packages' -print)
cp -r test tmp/test

(
cd tmp/test
./alltests.sh --$(pyversions --default)
)

rm -rf tmp build
