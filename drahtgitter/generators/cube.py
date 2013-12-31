'''
Simple cube primitive generator for drahtgitter
'''

from ..core import *

#-------------------------------------------------------------------------------
def generate(vertexLayout, size=Vector(1.0, 1.0, 1.0), origin=Vector(0.0, 0.0, 0.0)) :
    '''
    Generate a cube model with given vertex layout, size and origin
    '''
    dgLogger.debug('generators.cube')

    pos0 = ('position', 0)
    norm0 = ('normal', 0)
    uv0 = ('texcoord', 0)

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

    posOffset  = mesh.getComponentOffset(pos0)
    normOffset = mesh.getComponentOffset(norm0)
    uvOffset   = mesh.getComponentOffset(uv0)
    for i in range(0, 6) :
        for j in range(0, 4) :
            vertIndex = i * 4 + j
            coord = coords[coordMap[i][j]] * size + origin
            norm  = norms[i]
            uv    = uvs[uvMap[i][j]]
            mesh.setData3(vertIndex, posOffset, coord.x, coord.y, coord.z)
            mesh.setData3(vertIndex, normOffset, norm.x, norm.y, norm.z)
            mesh.setData2(vertIndex, uvOffset, uv.x, uv.y)

        triIndex = i * 2
        triVertIndex = i * 4
        mesh.setTriangle(triIndex, Triangle(triVertIndex, triVertIndex+1, triVertIndex+2, 0))
        mesh.setTriangle(triIndex + 1, Triangle(triVertIndex+2, triVertIndex+3, triVertIndex, 0))

    # create a dummy model
    model = Model('cube')
    model.mesh = mesh
    model.addMaterial(Material.createDefaultMaterial())

    return model

#--- eof







