'''
    drahtgitter operator to compute triangle normals
'''

from ..core import *

#-------------------------------------------------------------------------------
def do(mesh) :

    pos0 = ('position', 0)
    triIndex = 0
    for tri in mesh.triangles :
        v0 = mesh.getVertex(tri.vertexIndices[0], pos0)
        v1 = mesh.getVertex(tri.vertexIndices[1], pos0)
        v2 = mesh.getVertex(tri.vertexIndices[2], pos0)
        v10 = v1 - v0
        v20 = v2 - v0
        if Vector.length(v10) < 0.00001:
            raise Exception('Degenerate triangle {}: {} {} {} -> {} {} {}'.format(triIndex, v1.x, v1.y, v1.z, v0.x, v0.y, v0.z))
        if Vector.length(v20) < 0.00001:
            raise Exception('Degenerate triangle {}: {} {} {} -> {} {} {}'.format(triIndex, v2.x, v2.y, v2.z, v0.x, v0.y, v0.z))        
        tri.normal = Vector.normalize(Vector.cross3(v10, v20))
        triIndex += 1
    return mesh

#--- eof
