'''
General helper functions for the drahtgitter FBX reader
'''

from ...core import *
from fbx import *

#-------------------------------------------------------------------------------
def getPropVector(fbxVec, fbxScale) :
    '''
    Private helper method to convert a FBX property vector and scale to a Vector
    '''
    vec = Vector(fbxVec.Get()[0], fbxVec.Get()[1], fbxVec.Get()[2])
    if fbxScale != None :
        vec.x *= fbxScale.Get()
        vec.y *= fbxScale.Get()
        vec.z *= fbxScale.Get()
    return vec

#-------------------------------------------------------------------------------
def extractLayerElement(fbxMesh, fbxLayer, polyIndex, pointIndex, controlPointIndex) :
    '''
    Extracts a layer element (normal, uv, ...) and returns the
    element as FbxVector4
    '''
    vertexIndex = polyIndex * 3 + pointIndex
    mapMode = fbxLayer.GetMappingMode()
    refMode = fbxLayer.GetReferenceMode()
    if mapMode == FbxLayerElement.eByControlPoint :
        if refMode == FbxLayerElement.eDirect :
            fbxVec = fbxLayer.GetDirectArray().GetAt(controlPointIndex)
        elif refMode == FbxLayerElement.eIndexToDirect :
            id = fbxLayer.GetIndexArray().GetAt(controlPointIndex)
            fbxVec = fbxLayer.GetDirectArray().GetAt(id)
    elif mapMode == FbxLayerElement.eByPolygonVertex :
        if refMode == FbxLayerElement.eDirect :
            fbxVec = fbxLayer.GetDirectArray().GetAt(vertexIndex)
        elif refMode == FbxLayerElement.eIndexToDirect :
            id = fbxLayer.GetIndexArray().GetAt(vertexIndex)
            fbxVec = fbxLayer.GetDirectArray().GetAt(id)
    elif mapMode == FbxLayerElement.eByPolygon :
        raise Exception('Mapping mode is eByPolygon')
    elif mapMode == FbxLayerElement.eAllSame :
        raise Exception('Mapping mode is eAllSame')
    elif mapMode == FbxLayerElement.eNone :
        raise Exception('Mapping mode is eNone')

    if isinstance(fbxVec, FbxVector2) : 
        return FbxVector4(fbxVec[0], fbxVec[1], 0.0, 0.0)
    else :
        return fbxVec
 





