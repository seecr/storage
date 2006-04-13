#
# Hex
#
# $Id: hex.py,v 1.2 2006/02/21 12:13:24 cvs Exp $
#
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