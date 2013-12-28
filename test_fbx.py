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

    def _convertMeshFbx(self, name, scale) :
        mesh = fbxreader.readMesh('data/' + name + '.fbx')
        mesh, indexMap = deflate.do(mesh)
        stlasciiwriter.writeMesh(mesh, 'data/' + name + '_ascii.stl')
        threejswriter.writeMesh(mesh, 'data/' + name + '_threejs.json', scale)

    def test_FbxMeshReader(self) :
        #self._convertMeshFbx('cubeman', 10.0)
        #self._convertMeshFbx('teapot', 500.0)
        self._convertMeshFbx('radonlabs_tiger', 100.0)
        self._convertMeshFbx('radonlabs_opelblitz', 100.0)

    '''
    def test_FbxModelReader(self) :
        fbxreader.readModel('data/teapot.fbx')
        fbxreader.readModel('data/cubeman.fbx')
    '''

if __name__ == '__main__':
    unittest.main()
#--- eof



