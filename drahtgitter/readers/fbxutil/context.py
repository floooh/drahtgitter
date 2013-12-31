'''
The FBX contect class initializes FBX, and loads and prepares a scene for parsing.
'''
from ...core import *
from fbx import *
from ..fbxutil.geometry import removeBadPolygons

#-------------------------------------------------------------------------------
class Context :
    '''
    Initialize the FBX manager, load a scene and prepare the scene for 
    parsing
    '''
    def __init__(self) :
        self.fbxManager = None
        self.fbxScene = None
        self.fbxGeometryConverter = None

    def Setup(self, fbxFilePath) :
        '''
        Setup the FBX SDK, and load and preprocess a scene object
        '''
        self.fbxManager = FbxManager.Create()

        # load the scene
        fbxImporter = FbxImporter.Create(self.fbxManager, 'fbxImporter')
        status = fbxImporter.Initialize(fbxFilePath)
        if not status :
            raise Exception('FbxImporter: failed to load scene!')
        self.fbxScene = FbxScene.Create(self.fbxManager, 'fbxScene')
        fbxImporter.Import(self.fbxScene)
        fbxImporter.Destroy()

        # preprocess the scene
        self.fbxGeometryConverter = FbxGeometryConverter(self.fbxManager)
        if not self.fbxGeometryConverter.Triangulate(self.fbxScene, True) :
            raise Exception('Failed to triangulate FBX scene!')
        if not self.fbxGeometryConverter.SplitMeshesPerMaterial(self.fbxScene, True) :
            raise Exception('Failed to split meshes by material!')
        removeBadPolygons(self.fbxScene)

        return self.fbxScene

    def Discard(self) :
        '''
        Discard the FBX SDK
        '''
        if self.fbxGeometryConverter != None :
            self.fbxGeometryConverter = None

        if self.fbxScene != None :
            self.fbxScene.Destroy() 
            self.fbxScene = None

        if self.fbxManager != None :
            self.fbxManager.Destroy()
            self.fbxManager = None

#--- eof
