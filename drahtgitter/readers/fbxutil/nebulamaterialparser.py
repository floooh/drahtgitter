'''
A material parser for Nebula Toolkit custom shader parameters.
This is an example of how to use custom properties for advanced
shader parameters.

FIXME: instead of checking for user properties starting with
rl* this module should read the Nebula Toolkit's shaders.xml
file to lookup the shader parameters required for a specific
shader, this will also ignore obsolete shader params, and 
use default values for new shader params.
'''
from ...core import *
from fbx import *

#-------------------------------------------------------------------------------
class nebulaMaterialParser :
    '''
    Extracts custom Nebula Toolkit shader parameters from 
    FBX custom properties.
    '''
    def getName(self) :
        return 'Nebula Toolkit Material Parser'

    def accepts(self, fbxMaterial) :
        '''
        Returns true if the provided material is a 
        Nebula Toolkit material (those have custom
        properties starting with rl*)
        '''
        return fbxMaterial.FindProperty('rlNebulaShader', True) != None

    def parse(self, fbxMaterial, mat) :
        '''
        Parse the fbxMaterial class for Nebula Toolkit shader params.
        Currently this is implemented by iterating over all custom
        params and finding the ones starting with rl*. Later this
        should be implemented by loading the toolkit's shaders.xml
        file once and looking up shader params from there.
        '''
        mat.type = 'Nebula'
        prop = fbxMaterial.GetFirstProperty()
        while prop.IsValid() :
            if prop.GetFlag(FbxPropertyAttr.eUserDefined) :
                name = prop.GetName().Buffer()
                if name == 'rlNebulaShader' :
                    mat.shaderName = FbxPropertyString(prop).Get()
                elif name.startswith('rl') :
                    matParam = MatParam()
                    matParam.name = name[2:]
                    propType = prop.GetPropertyDataType().GetType()
                    if propType == eFbxInt :
                        matParam.type  = MatParam.Int
                        matParam.value = FbxPropertyInteger1(prop).Get()
                    elif propType == eFbxFloat :
                        matParam.type  = MatParam.Float
                        matParam.value = FbxPropertyFloat1(prop).Get()
                    elif propType == eFbxDouble :
                        matParam.type  = MatParam.Float
                        matParam.value = FbxPropertyDouble1(prop).Get()
                    elif propType == eFbxDouble2 :
                        val = FbxPropertyDouble2(prop).Get()
                        matParam.type  = MatParam.Float2
                        matParam.value = Vector(val[0], val[1])
                    elif propType == eFbxDouble3 :
                        val = FbxPropertyDouble3(prop).Get()
                        matParam.type  = MatParam.Float3
                        matParam.value = Vector(val[0], val[1], val[2])
                    elif propType == eFbxDouble4 :
                        val = FbxPropertyDouble4(prop).Get()
                        matParam.type  = MatParam.Float4
                        matParam.value = Vector(val[1], val[2], val[3], val[4])
                    elif propType == eFbxString :
                        matParam.type  = MatParam.Texture
                        matParam.value = FbxPropertyString(prop).Get()
                    elif propType == eFbxEnum :
                        matParam.type  = MatParam.Int
                        matParam.value = FbxPropertyEnum(prop).Get()
                    else :
                        dgLogger.warning('WARNING: unsupported shader param type {}'.format(propType.GetName()))
                    
                    if matParam.type != None :
                        mat.addParam(matParam)
            prop = fbxMaterial.GetNextProperty(prop)

#-- eof









