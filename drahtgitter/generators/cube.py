'''
Simple cube mesh generator for drahtgitter
'''

from ..core import *

#-------------------------------------------------------------------------------
def generateMesh(vertexLayout, size=Vector(1.0, 1.0, 1.0), origin=Vector(0.0, 0.0, 0.0)) :
    '''
    Generate a cube mesh with given vertex layout, size and origin
    '''
    mesh = Mesh(vertexLayout, 24, 12)

    # generate vertex positions
    pos0 = ('position', 0)

    topLeftFrontPos  = origin + size * Vector(-0.5, +0.5, -0.5)
    topLeftBackPos   = origin + size * Vector(-0.5, +0.5, +0.5)
    topRightBackPos  = origin + size * Vector(+0.5, +0.5, +0.5)
    topRightFrontPos = origin + size * Vector(+0.5, +0.5, -0.5)

    bottomLeftFrontPos  = origin + size * Vector(-0.5, -0.5, -0.5)
    bottomLeftBackPos   = origin + size * Vector(-0.5, -0.5, +0.5)
    bottomRightBackPos  = origin + size * Vector(+0.5, -0.5, +0.5)
    bottomRightFrontPos = origin + size * Vector(+0.5, -0.5, -0.5)

    # top
    mesh.setVertex(0, pos0, topLeftFrontPos)
    mesh.setVertex(1, pos0, topLeftBackPos)
    mesh.setVertex(2, pos0, topRightBackPos)
    mesh.setVertex(3, pos0, topRightFrontPos)
    mesh.setTriangle(0, Triangle((0, 1, 2), 0))
    mesh.setTriangle(1, Triangle((0, 2, 3), 0))

    # front
    mesh.setVertex(4, pos0, topLeftFrontPos)
    mesh.setVertex(5, pos0, topRightFrontPos)
    mesh.setVertex(6, pos0, bottomRightFrontPos)
    mesh.setVertex(7, pos0, bottomLeftFrontPos)
    mesh.setTriangle(2, Triangle((4, 5, 6), 0))
    mesh.setTriangle(3, Triangle((4, 6, 7), 0))

    # left
    mesh.setVertex(8, pos0, topLeftBackPos)
    mesh.setVertex(9, pos0, topLeftFrontPos)
    mesh.setVertex(10, pos0, bottomLeftFrontPos)
    mesh.setVertex(11, pos0, bottomLeftBackPos)
    mesh.setTriangle(4, Triangle((8, 9, 10), 0))
    mesh.setTriangle(5, Triangle((8, 10, 11), 0))

    # right
    mesh.setVertex(12, pos0, topRightFrontPos)
    mesh.setVertex(13, pos0, topRightBackPos)
    mesh.setVertex(14, pos0, bottomRightBackPos)
    mesh.setVertex(15, pos0, bottomRightFrontPos)
    mesh.setTriangle(6, Triangle((12, 13, 14), 0))
    mesh.setTriangle(7, Triangle((12, 14, 15), 0))

    # back
    mesh.setVertex(16, pos0, topRightBackPos)
    mesh.setVertex(17, pos0, topLeftBackPos)
    mesh.setVertex(18, pos0, bottomLeftBackPos)
    mesh.setVertex(19, pos0, bottomRightBackPos)
    mesh.setTriangle(8, Triangle((16, 17, 18), 0))
    mesh.setTriangle(9, Triangle((16, 18, 19), 0))

    # bottom
    mesh.setVertex(20, pos0, bottomLeftBackPos)
    mesh.setVertex(21, pos0, bottomLeftFrontPos)
    mesh.setVertex(22, pos0, bottomRightFrontPos)
    mesh.setVertex(23, pos0, bottomRightBackPos)
    mesh.setTriangle(10, Triangle((20, 21, 22), 0))
    mesh.setTriangle(11, Triangle((20, 22, 23), 0))

    # generate UV coords if requested
    texcoord0 = ('texcoord', 0)
    if vertexLayout.contains(texcoord0) :        
        uv00 = Vector(0.0, 0.0)
        uv10 = Vector(1.0, 0.0)
        uv01 = Vector(0.0, 1.0)
        uv11 = Vector(1.0, 1.0)

        for i in range(0,6) :
            mesh.setVertex(i * 4 + 0, texcoord0, uv00)
            mesh.setVertex(i * 4 + 1, texcoord0, uv10)
            mesh.setVertex(i * 4 + 2, texcoord0, uv11)
            mesh.setVertex(i * 4 + 3, texcoord0, uv01)

    # generate normals if requested
    normal0 = ('normal', 0)
    if vertexLayout.contains(normal0) :
        
        # top normals
        for i in range(0, 4) :
            mesh.setVertex(i, normal0, Vector(0.0, +1.0, 0.0))

        # front normals
        for i in range(4, 8) :
            mesh.setVertex(i, normal0, Vector(0.0, 0.0, -1.0))

        # left normals
        for i in range(8, 12) :
            mesh.setVertex(i, normal0, Vector(-1.0, 0.0, 0.0))

        # right normals
        for i in range(12, 16) :
            mesh.setVertex(i, normal0, Vector(+1.0, 0.0, 0.0))

        # back normals
        for i in range(16, 20) :
            mesh.setVertex(i, normal0, Vector(0.0, 0.0, +1.0))

        # bottom normals
        for i in range(20, 24) :
            mesh.setVertex(i, normal0, Vector(0.0, -1.0, 0.0))

    return mesh

#--- eof







