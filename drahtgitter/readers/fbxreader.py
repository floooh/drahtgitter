'''
FBX reader. 
You need to install the FBX Python SDK for this: 
http://docs.autodesk.com/FBX/2014/ENU/FBX-SDK-Documentation/index.html
'''
from ..core import *
from fbxutil.context import *
from fbxutil.general import *
from fbxutil.geometry import *
from fbxutil.material import *
from fbxutil.hwshadermaterialparser import *
from fbxutil.lambertmaterialparser import *
from fbxutil.phongmaterialparser import *
from fbx import *

#-------------------------------------------------------------------------------
class config :
    '''
    A config object to configure the FBX import process
    '''
    def __init__(self) :
        self.materialParsers = [ hwShaderMaterialParser(), phongMaterialParser(), lambertMaterialParser()  ]

#-------------------------------------------------------------------------------
def readMesh(path) :
    '''
    Open an FBX file and extract geometry information, returns
    a Mesh object. This loses hierarchy and material information
    and only returns a single, flattened mesh.
    '''

    print 'fbxreader.readMesh: {}'.format(path)
    context = Context()
    context.Setup(path)

    # detect the required vertex layout and setup a mesh object
    vertexLayout = buildVertexLayout(context.fbxScene)
    numTriangles = countTriangles(context.fbxScene)
    outMesh = Mesh(vertexLayout, numTriangles * 3, numTriangles)

    # iterate over nodes
    curTriIndex = 0
    for nodeIndex in range(0, context.fbxScene.GetNodeCount()) :
        fbxNode = context.fbxScene.GetNode(nodeIndex)
        fbxMesh = fbxNode.GetMesh()
        if fbxMesh != None :
            extractGeometry(outMesh, fbxNode, fbxMesh, 0, curTriIndex)
            curTriIndex += fbxMesh.GetPolygonCount()

    context.Discard()
    return outMesh

#-------------------------------------------------------------------------------
def readModel(config, path, name) :
    '''
    Reads an FBX file with material information, but flattens node hierarchy.
    FIXME: use a hint attribute to decide if a node must be preserved
    '''
    print 'fbxReader.readModel: {}'.format(path)
    context = Context()
    context.Setup(path)


    # extract Materials from the scene
    outModel = Model(name)
    extractMaterials(config, context.fbxScene, outModel)

    # detect the required vertex layout and setup a mesh object
    vertexLayout = buildVertexLayout(context.fbxScene)
    numTriangles = countTriangles(context.fbxScene)
    outModel.mesh = Mesh(vertexLayout, numTriangles * 3, numTriangles)

    # iterate over nodes
    curTriIndex = 0
    for nodeIndex in range(0, context.fbxScene.GetNodeCount()) :
        fbxNode = context.fbxScene.GetNode(nodeIndex)
        fbxMesh = fbxNode.GetMesh()
        if fbxMesh != None :
            materialIndex = lookupMaterialIndex(outModel, fbxNode, fbxMesh)
            extractGeometry(outModel.mesh, fbxNode, fbxMesh, materialIndex, curTriIndex)
            curTriIndex += fbxMesh.GetPolygonCount()

    context.Discard()

    return outModel
