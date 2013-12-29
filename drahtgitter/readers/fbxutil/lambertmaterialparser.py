'''
Material parser for the standard FBX Lambert material
'''
from ...core import *
from ..fbxutil.general import getPropVector
from fbx import *

#-------------------------------------------------------------------------------
class lambertMaterialParser :
    '''
    Extracts material parameters for FbxSurfaceLambert materials
    '''    
    def getName(self) :
        return 'Lambert Material Parser'

    def accepts(self, fbxMaterial) :
        '''
        Returns True if the provided material is a FbxSurfaceLambert object
        '''
        return fbxMaterial.GetClassId().Is(FbxSurfaceLambert.ClassId)

    def parse(self, fbxMaterial, mat) :
        '''
        Parses the FbxMaterial into a drahtgitter material
        '''    
        # FIXME: there could be textures attached to these values?!?!
        emissive  = getPropVector(fbxMaterial.Emissive, fbxMaterial.EmissiveFactor)
        ambient   = getPropVector(fbxMaterial.Ambient, fbxMaterial.AmbientFactor)
        diffuse   = getPropVector(fbxMaterial.Diffuse, fbxMaterial.DiffuseFactor)
        bump      = getPropVector(fbxMaterial.Bump, fbxMaterial.BumpFactor)
        normalMap = getPropVector(fbxMaterial.NormalMap, None)
        transparentColor  = getPropVector(fbxMaterial.TransparentColor, fbxMaterial.TransparencyFactor)
        displacementColor = getPropVector(fbxMaterial.DisplacementColor, fbxMaterial.DisplacementFactor)
        vectorDisplacementColor = getPropVector(fbxMaterial.VectorDisplacementColor, fbxMaterial.VectorDisplacementFactor)

        mat.type = 'Lambert'
        mat.addParam(MatParam('Emissive', MatParam.Color, emissive))
        mat.addParam(MatParam('Ambient', MatParam.Color, ambient))
        mat.addParam(MatParam('Diffuse', MatParam.Color, diffuse))
        mat.addParam(MatParam('Bump', MatParam.Color, bump))
        mat.addParam(MatParam('NormalMap', MatParam.Color, normalMap))
        mat.addParam(MatParam('TransparentColor', MatParam.Color, transparentColor))
        mat.addParam(MatParam('DisplacementColor', MatParam.Color, displacementColor))


#--- eof
