'''
Material related FBX utility functions.
'''

from ...core import *
from ..fbxutil.general import dumpUserProperties
from fbx import *

#-------------------------------------------------------------------------------
def lookupMaterialIndex(model, fbxNode, fbxMesh) :
    '''
    Lookup the material index for a mesh. Can return None.
    '''
    matCount = fbxNode.GetMaterialCount()
    if matCount == 0 :
        dgLogger.warning('No material assigned to mesh {} at node {}'.format(fbxMesh.GetName(), fbxNode.GetName()))
        return None        
    if matCount > 1 :
        dgLogger.warning('More then one material assigned to mesh {} at node {}'.format(fbxMesh.GetName(), fbxNode.GetName()))
        return None
    fbxMaterial = fbxNode.GetMaterial(0)
    matIndex = model.findMaterialIndex(fbxMaterial.GetName())
    return matIndex

#-------------------------------------------------------------------------------
def extractMaterials(config, fbxScene, model) :
    '''
    Extract all materials in the scene and adds them to the model
    '''
    for i in range(0, fbxScene.GetMaterialCount()) :
        fbxMaterial = fbxScene.GetMaterial(i)
        for matParser in config.materialParsers :
            if matParser.accepts(fbxMaterial) :
                mat = Material(fbxMaterial.GetName())
                matParser.parse(fbxMaterial, mat)
                model.addMaterial(mat)
                break
        else :
            raise Exception('No suitable material parser for {}'.format(fbxMaterial.GetName()))

