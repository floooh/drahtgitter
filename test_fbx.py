#!/usr/bin/python
'''
Test FBX related stuff, only works if the FBX Python SDK is installed.
'''
import unittest
from drahtgitter.core import *
import drahtgitter.readers.fbxreader as fbxreader
import drahtgitter.operators.deflate as deflate
import drahtgitter.operators.randomMaterialColors as randomMaterialColors
import drahtgitter.writers.stlasciiwriter as stlasciiwriter
import drahtgitter.writers.threejswriter as threejswriter

class TestFBX(unittest.TestCase) :

    def _convertMesh(self, name, scale) :
        mesh = fbxreader.readMesh('data/' + name + '.fbx')
        mesh, indexMap = deflate.do(mesh)
        stlasciiwriter.writeMesh(mesh, 'data/' + name + '.ascii.stl')
        threejswriter.writeMesh(mesh, 'data/' + name + '.geom.js', scale)

    def test_FbxMeshReader(self) :
        self._convertMesh('cubeman', 10.0)
        self._convertMesh('teapot', 500.0)
        self._convertMesh('radonlabs_tiger', 100.0)
        self._convertMesh('radonlabs_opelblitz', 100.0)

    def _convertModel(self, name, scale) :
        config = fbxreader.config()
        model = fbxreader.readModel(config, 'data/' + name + '.fbx', name)
        model = randomMaterialColors.do(model)
        model.dumpMaterials()
        threejswriter.writeModel(model, 'data/' + name + '.model.js', 100)

    def test_FbxModelReader(self) :
        self._convertModel('teapot_yellow', 100)
        self._convertModel('teapot_transparent', 100)
        self._convertModel('radonlabs_opelblitz', 100)
        self._convertModel('radonlabs_tiger', 100)

if __name__ == '__main__':
    unittest.main()
#--- eof



