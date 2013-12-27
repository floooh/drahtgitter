'''
Torus generator
FIXME uv coord!
'''

from ..core import *

#-------------------------------------------------------------------------------
def generateMesh(vertexLayout, innerRadius, outerRadius, numSides, numRings) :
    '''
    Generate torus mesh
    '''
    pos0 = ('position', 0)
    norm0 = ('normal', 0)
    tex0 = ('texcoord', 0)

    # initialize mesh object
    numVertices = numRings * numSides 
    numTriangles = (numRings-1) * numSides * 2 + numSides * 2
    mesh = Mesh(vertexLayout, numVertices, numTriangles)

    # generate vertices
    vertexIndex = 0
    for i in range(0, numRings) :
        theta = i * 2.0 * math.pi / numRings
        sinTheta = math.sin(theta)
        cosTheta = math.cos(theta)

        for j in range(0, numSides) :
            phi = j * 2.0 * math.pi / numSides
            sinPhi = math.sin(phi)
            cosPhi = math.cos(phi)

            px = cosTheta * (outerRadius + innerRadius * cosPhi)
            py = -sinTheta * (outerRadius + innerRadius * cosPhi)
            pz = sinPhi * innerRadius
            pos = Vector(px, py, pz)

            nx = cosTheta * cosPhi
            ny = -sinTheta * cosPhi
            nz = sinPhi
            norm = Vector(nx, ny, nz)

            mesh.setVertex(vertexIndex, pos0, pos)
            mesh.setVertex(vertexIndex, norm0, norm)
            vertexIndex += 1

    if vertexIndex != mesh.getNumVertices() :
        raise Exception('Vertex count mismatch!')

    # generate numTriangles
    triIndex = 0
    for i in range(0, numRings - 1) :
        for j in range(0, numSides - 1) :
            mesh.setTriangle(triIndex, Triangle(i*numSides+j, i*numSides+j+1, (i+1)*numSides+j, 0))
            triIndex += 1
            mesh.setTriangle(triIndex, Triangle((i+1)*numSides+j, i*numSides+j+1, (i+1)*numSides+j+1, 0))
            triIndex += 1
        j += 1
        mesh.setTriangle(triIndex, Triangle(i*numSides+j, i*numSides, (i+1)*numSides+j, 0))
        triIndex += 1
        mesh.setTriangle(triIndex, Triangle((i+1)*numSides+j, i*numSides, (i+1)*numSides, 0))
        triIndex += 1
    i += 1
    for j in range(0, numSides - 1) :
        mesh.setTriangle(triIndex, Triangle(i*numSides+j, i*numSides+j+1, j, 0))
        triIndex += 1
        mesh.setTriangle(triIndex, Triangle(j, i*numSides+j+1, j+1, 0))
        triIndex += 1
    j += 1
    mesh.setTriangle(triIndex, Triangle(i*numSides+j, i*numSides, j, 0))
    triIndex += 1
    mesh.setTriangle(triIndex, Triangle(j, i*numSides, 0, 0))
    triIndex += 1

    if triIndex != mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')

    return mesh

#-- eof







