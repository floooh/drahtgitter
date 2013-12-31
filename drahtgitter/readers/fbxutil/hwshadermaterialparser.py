'''
Material parser for HW Shader materials
TODO: UNFINISHED!
'''
from ...core import *
from ..fbxutil.general import getPropVector
from fbx import *

#-------------------------------------------------------------------------------
class hwShaderMaterialParser :
    '''
    Extracts material parameters for CGFX or HLSL hardware shader materials
    '''
    def getName(self) :
        return 'HW Shader Material Parser'

    def accepts(self, fbxMaterial) :
        '''
        Checks whether this is a hardware material
        '''
        impl = GetImplementation(fbxMaterial, 'ImplementationHLSL')
        if not impl :
            impl = GetImplementation(fbxMaterial, 'ImplementationCGFX')
        return impl != None

    def parse(self, fbxMaterial, mat) :
        '''
        Parse hw shader params
        '''
        impl = GetImplementation(fbxMaterial, 'ImplementationHLSL')
        shdType = 'HLSL'
        if not impl :
            impl = GetImplementation(fbxMaterial, 'ImplementationCGFX')
            shdType = 'CGFX'
    
        dgLogger.debug('Hardware Shader: {}'.format(fbxMaterial.GetName()))
        dgLogger.debug('Shader Type: {}'.format(shdType))

        mat.type = 'FBX HW {}'.format(shdType)

        # parse the binding table
        table = impl.GetRootTable()
        for entryIndex in range(0, table.GetEntryCount()) :
            entry = table.GetEntry(entryIndex)

            dgLogger.debug('Entry Type: {}'.format(entry.GetType(True)))
            dgLogger.debug('Entry Source: {}'.format(entry.GetSource()))

            raise Exception('FIXME FIXME FIXME')

#--- eof
