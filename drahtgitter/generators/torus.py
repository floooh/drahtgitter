'''
Torus generator
FIXME uv coord!
'''

from ..core import *

#-------------------------------------------------------------------------------
def generate(vertexLayout, innerRadius, outerRadius, numSides, numRings) :
    '''
    Generate torus model
    '''
    dgLogger.debug('generators.torus')
    # initialize mesh object
    numVertices = numRings * numSides 
    numTriangles = (numRings-1) * numSides * 2 + numSides * 2
    mesh = Mesh(vertexLayout, numVertices, numTriangles)
    posOffset = mesh.getComponentOffset(('position', 0))
    normOffset = mesh.getComponentOffset(('normal', 0))

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

            nx = cosTheta * cosPhi
            ny = -sinTheta * cosPhi
            nz = sinPhi

            mesh.setData3(vertexIndex, posOffset, px, py, pz)
            mesh.setData3(vertexIndex, normOffset, nx, ny, nz)
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

    # create a dummy model
    model = Model('torus')
    model.mesh = mesh
    model.addMaterial(Material.createDefaultMaterial())

    return model

#-- eof







