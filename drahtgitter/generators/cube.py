'''
Simple cube mesh generator for drahtgitter
'''

from ..core import *

#-------------------------------------------------------------------------------
def generateMesh(vertexLayout, size=Vector(1.0, 1.0, 1.0), origin=Vector(0.0, 0.0, 0.0)) :
    '''
    Generate a cube mesh with given vertex layout, size and origin
    '''
    pos0 = ('position', 0)
    norm0 = ('normal', 0)
    tex0 = ('texcoord', 0)

    coords = [  Vector(-0.5, -0.5, -0.5), Vector(-0.5, -0.5, +0.5),
                Vector(+0.5, -0.5, +0.5), Vector(+0.5, -0.5, -0.5),
                Vector(-0.5, +0.5, -0.5), Vector(-0.5, +0.5, +0.5),
                Vector(+0.5, +0.5, +0.5), Vector(+0.5, +0.5, -0.5) ]

    norms = [   Vector(-1.0,  0.0,  0.0), Vector( 0.0, +1.0,  0.0),
                Vector(+1.0,  0.0,  0.0), Vector( 0.0, -1.0,  0.0),
                Vector( 0.0,  0.0, +1.0), Vector( 0.0,  0.0, -1.0) ]

    uvs = [ Vector(0.0, 0.0), Vector(0.0, 1.0), Vector(1.0, 1.0), Vector(1.0, 0.0) ]

    coordMap = [ [0, 1, 5, 4], [4, 5, 6, 7], [7, 6, 2, 3],
                 [1, 0, 3, 2], [1, 2, 6, 5], [0, 4, 7, 3] ]

    uvMap = [ [3, 0, 1, 2], [0, 1, 2, 3], [1, 2, 3, 0],
              [0, 1, 2, 3], [3, 0, 1, 2], [0, 1, 2, 3] ]

    mesh = Mesh(vertexLayout, 24, 12)

    for i in range(0, 6) :
        for j in range(0, 4) :
            vertIndex = i * 4 + j
            coord = coords[coordMap[i][j]] * size + origin
            mesh.setVertex(vertIndex, pos0, coord)
            mesh.setVertex(vertIndex, norm0, norms[i])
            mesh.setVertex(vertIndex, tex0, uvs[uvMap[i][j]])

        triIndex = i * 2
        triVertIndex = i * 4
        mesh.setTriangle(triIndex, Triangle(triVertIndex, triVertIndex+1, triVertIndex+2, 0))
        mesh.setTriangle(triIndex + 1, Triangle(triVertIndex+2, triVertIndex+3, triVertIndex, 0))

    return mesh

#--- eof







