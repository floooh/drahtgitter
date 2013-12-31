'''
Compute triangle normals of a model.
'''

from ..core import *

#-------------------------------------------------------------------------------
def do(model) :

    dgLogger.debug('operators.computeTriangleNormals: model={}'.format(model.name))

    mesh = model.mesh
    pos0 = ('position', 0)
    triIndex = 0
    nullVec = Vector(0.0, 0.0, 0.0)
    for tri in mesh.triangles :
        v0 = mesh.getVertex(tri.vertexIndex0, pos0)
        v1 = mesh.getVertex(tri.vertexIndex1, pos0)
        v2 = mesh.getVertex(tri.vertexIndex2, pos0)
        v10 = v1 - v0
        v20 = v2 - v0
        cross = Vector.cross3(v10, v20)
        if cross != nullVec:
            triNormal = Vector.normalize(cross)
            tri.normalX = triNormal.x
            tri.normalY = triNormal.y
            tri.normalZ = triNormal.z
        else :
            dgLogger.warning('Degenerate triangle at tri index {}'.triIndex)
            tri.normalX = 0.0
            tri.normalY = 1.0
            tri.normalZ = 0.0
        triIndex += 1
        
    return model

#--- eof
