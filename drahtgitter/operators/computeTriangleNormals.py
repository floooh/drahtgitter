'''
    drahtgitter operator to compute triangle normals
'''

from ..core import *

#-------------------------------------------------------------------------------
def do(mesh) :

    pos0 = ('position', 0)
    for tri in mesh.triangles :
        v0 = mesh.getVertex(tri.vertexIndices[0], pos0)
        v1 = mesh.getVertex(tri.vertexIndices[1], pos0)
        v2 = mesh.getVertex(tri.vertexIndices[2], pos0)
        tri.normal = Vector.normalize(Vector.cross3(v1 - v0, v2 - v0))
    return mesh

#--- eof
