#!/usr/bin/python
'''
Test FBX related stuff, only works if the FBX Python SDK is installed.
'''
import unittest
from drahtgitter.core import *
import drahtgitter.readers.fbxreader as fbxreader
import drahtgitter.operators.deflate as deflate
import drahtgitter.operators.randomMaterialColors as randomMaterialColors
import drahtgitter.operators.removeDegenerateTriangles as removeDegenerateTriangles
import drahtgitter.operators.computeTriangleNormals as computeTriangleNormals
import drahtgitter.writers.stlasciiwriter as stlasciiwriter
import drahtgitter.writers.threejswriter as threejswriter
import drahtgitter.readers.fbxutil.nebulamaterialparser as nebulamaterialparser

class TestFBX(unittest.TestCase) :

    def _convert(self, name, scale) :
        config = fbxreader.config()
        model = fbxreader.read(config, 'data/' + name + '.fbx', name)
        model = randomMaterialColors.do(model)
        model, indexMap = deflate.do(model)
        model = removeDegenerateTriangles.do(model)
        model = computeTriangleNormals.do(model)
        model.dumpMaterials()
        threejswriter.write(model, 'data/' + name + '.model.js', 100)

    def test_FbxReader(self) :
        self._convert('teapot_yellow', 100)
        self._convert('teapot_transparent', 100)
        self._convert('radonlabs_opelblitz', 100)
        self._convert('radonlabs_tiger', 100)

    def test_NebulaMaterialParser(self) :
        config = fbxreader.config()
        config.materialParsers.insert(0, nebulamaterialparser.nebulaMaterialParser())
        model = fbxreader.read(config, 'data/radonlabs_opelblitz.fbx', 'blitz')
        model.dumpMaterials()

if __name__ == '__main__':
    unittest.main()
#--- eof



