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
        mat.addParam(MatParam('Emissive', MatParam.Float4, emissive))
        mat.addParam(MatParam('Ambient', MatParam.Float4, ambient))
        mat.addParam(MatParam('Diffuse', MatParam.Float4, diffuse))
        mat.addParam(MatParam('Bump', MatParam.Float4, bump))
        mat.addParam(MatParam('NormalMap', MatParam.Float4, normalMap))
        mat.addParam(MatParam('TransparentColor', MatParam.Float4, transparentColor))
        mat.addParam(MatParam('DisplacementColor', MatParam.Float4, displacementColor))
        mat.addParam(MatParam('Specular', MatParam.Float4, specular))
        mat.addParam(MatParam('Reflection', MatParam.Float4, reflection))
        mat.addParam(MatParam('Shininess', MatParam.Float, shininess))

#--- eof
