#!/usr/bin/python
'''
Test FBX related stuff, only works if the FBX Python SDK is installed.
'''
import unittest
from drahtgitter.core import *
import drahtgitter.readers.fbxreader as fbxreader
import drahtgitter.operators.deflate as deflate
import drahtgitter.writers.stlasciiwriter as stlasciiwriter
import drahtgitter.writers.threejswriter as threejswriter

class TestFBX(unittest.TestCase) :

    def _convertFbx(self, name, scale) :
        mesh = fbxreader.readMesh('data/' + name + '.fbx')
        mesh, indexMap = deflate.do(mesh)
        stlasciiwriter.writeMesh(mesh, 'data/' + name + '_ascii.stl')
        threejswriter.writeMesh(mesh, 'data/' + name + '_threejs.json', scale)

    def test_FbxReader(self) :
        self._convertFbx('cubeman', 10.0)
        self._convertFbx('teapot', 500.0)

if __name__ == '__main__':
    unittest.main()
#--- eof



