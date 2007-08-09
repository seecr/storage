#!/usr/bin/env python

from sys import path
from os import system
path.insert(0, '..')
system('rm -rf ../storage/*.pyc *.pyc')

from storagetest import StorageTest
from facadetest import FacadeTest

from unittest import main

if __name__ == '__main__':
    main()