## begin license ##
#
#    Storage stores data in a reliable, extendable filebased storage
#    with great performance.
#    Copyright (C) 2006 Seek You Too B.V. (CQ2) http://www.cq2.nl
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

import sys

def stringToHexString(aString):
	result = ""
	for char in aString:
		result += charToHexString(char)
	return result
	
def charToHexString(aChar):
	i = ord(aChar)
	l = i >> 4
	r = i % 16
	return nrToHexString(l) + nrToHexString(r)
	
def nrToHexString(nr):
	if 0 <= nr <= 9:
		 return str(nr)
	return chr(ord("A") + nr - 10)

def hexStringToString(aHexString):
	if len(aHexString) == 0:
		 return ""
	return hexByteToChar(aHexString[0:2]) + hexStringToString(aHexString[2:])
	
def hexByteToChar(aHexByte):
	return chr(hexToNr(aHexByte[0]) * 16 + hexToNr(aHexByte[1]))
	
def hexToNr(aHex):
	if "0" <= aHex <= "9":
		 return int(aHex)
	return ord(aHex) - ord("A") + 10

if __name__ == "__main__":
	print stringToHexString(sys.stdin.read())
