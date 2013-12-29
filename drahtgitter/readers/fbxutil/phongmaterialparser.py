'''
Material parser for standard FBX Phong material
'''
from ...core import *
from ..fbxutil.general import getPropVector
from fbx import *

#-------------------------------------------------------------------------------
class phongMaterialParser :
    '''
    Extracts material parameters for FbxSurfacePhong materials
    '''
    def getName(self) :
        return 'Phong Material Parser'

    def accepts(self, fbxMaterial) :
        '''
        Returns True if the provided material is a FbxSurfacePhong object
        '''
        return fbxMaterial.GetClassId().Is(FbxSurfacePhong.ClassId)

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
        specular   = getPropVector(fbxMaterial.Specular, fbxMaterial.SpecularFactor)
        reflection = getPropVector(fbxMaterial.Reflection, fbxMaterial.ReflectionFactor)
        shininess  = fbxMaterial.Shininess.Get()

        mat.type = 'Phong'
        mat.addParam(MatParam('Emissive', MatParam.Color, emissive))
        mat.addParam(MatParam('Ambient', MatParam.Color, ambient))
        mat.addParam(MatParam('Diffuse', MatParam.Color, diffuse))
        mat.addParam(MatParam('Bump', MatParam.Color, bump))
        mat.addParam(MatParam('NormalMap', MatParam.Color, normalMap))
        mat.addParam(MatParam('TransparentColor', MatParam.Color, transparentColor))
        mat.addParam(MatParam('DisplacementColor', MatParam.Color, displacementColor))
        mat.addParam(MatParam('Specular', MatParam.Color, specular))
        mat.addParam(MatParam('Reflection', MatParam.Color, reflection))
        mat.addParam(MatParam('Shininess', MatParam.Float, shininess))

#--- eof
