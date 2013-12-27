'''
    STL ASCII writer
'''
from ..core import *

#-------------------------------------------------------------------------------
def writeMesh(mesh, path) :

    f = open(path, 'w')

    pos0 = ('position', 0)
    f.write('solid mesh\n')
    for tri in mesh.triangles :
        v0 = mesh.getVertex(tri.vertexIndex0, pos0)
        v1 = mesh.getVertex(tri.vertexIndex1, pos0)
        v2 = mesh.getVertex(tri.vertexIndex2, pos0)
        f.write('facet normal {0} {1} {2}\n'.format(tri.normalX, tri.normalY, tri.normalZ))
        f.write('\touter loop\n')
        f.write('\t\tvertex {0} {1} {2}\n'.format(v0.x, v0.y, v0.z))
        f.write('\t\tvertex {0} {1} {2}\n'.format(v1.x, v1.y, v1.z))
        f.write('\t\tvertex {0} {1} {2}\n'.format(v2.x, v2.y, v2.z))
        f.write('\tendloop\n')
        f.write('endfacet\n')
    f.write('endsolid mesh')
    f.close()



