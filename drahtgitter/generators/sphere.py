'''
Sphere generator
FIXME: uv coords!
'''

from ..core import *

#-------------------------------------------------------------------------------
def generate(vertexLayout, radius, numSlices, numStacks) :
    '''
    Generate sphere model
    '''
    dgLogger.debug('generators.sphere')
    # generate sin/cos tables
    sinTableI = []
    cosTableI = []
    for i in range(0, numSlices) :
        val = 2.0 * math.pi * i / numSlices
        sinTableI.append(math.sin(val))
        cosTableI.append(math.cos(val))

    sinTableJ = []
    cosTableJ = []
    for i in range(0, numStacks) :
        val = math.pi * i / numStacks
        sinTableJ.append(math.sin(val))
        cosTableJ.append(math.cos(val))

    # initialize mesh object
    numVerts = 2 + numSlices * (numStacks - 1)
    numTris  = 2 * numSlices + 2 * numSlices * (numStacks - 2)
    mesh = Mesh(vertexLayout, numVerts, numTris)
    posOffset = mesh.getComponentOffset(('position', 0))
    normOffset = mesh.getComponentOffset(('normal', 0))

    # top pole vertex
    curVertexIndex = 0
    mesh.setData3(curVertexIndex, posOffset, 0.0, 0.0, radius)
    mesh.setData3(curVertexIndex, normOffset, 0.0, 0.0, 1.0)
    curVertexIndex += 1

    # stack vertices
    for j in range(1, numStacks) :
        for i in range(0, numSlices) :
            nx = sinTableI[i] * sinTableJ[j]
            ny = cosTableI[i] * sinTableJ[j]
            nz = cosTableJ[j]
            norm = Vector(nx, ny, nz)
            pos  = Vector.scale(norm, radius)
            mesh.setData3(curVertexIndex, posOffset, pos.x, pos.y, pos.z)
            mesh.setData3(curVertexIndex, normOffset, norm.x, norm.y, norm.z)
            curVertexIndex += 1

    # base pole index
    mesh.setData3(curVertexIndex, posOffset, 0.0, 0.0, -radius)
    mesh.setData3(curVertexIndex, normOffset, 0.0, 0.0, -1.0)
    curVertexIndex += 1
    if curVertexIndex != mesh.getNumVertices() :
        raise Exception("Vertex count mismatch!")

    # generate triangles
    triIndex = 0

    # top pole triangles
    rowA = 0
    rowB = 1
    for i in range(0, numSlices - 1) :
        mesh.setTriangle(triIndex, Triangle(rowA, rowB+i+1, rowB+i, 0))
        triIndex += 1
    i += 1
    mesh.setTriangle(triIndex, Triangle(rowA, rowB, rowB+i, 0))
    triIndex += 1

    # stack triangles
    for j in range(1, numStacks - 1) :
        rowA = 1 + (j - 1) * numSlices
        rowB = rowA + numSlices
        for i in range(0, numSlices - 1) :
            mesh.setTriangle(triIndex, Triangle(rowA+i, rowA+i+1, rowB+i, 0))
            triIndex += 1
            mesh.setTriangle(triIndex, Triangle(rowA+i+1, rowB+i+1, rowB+i, 0))
            triIndex += 1
        i += 1
        mesh.setTriangle(triIndex, Triangle(rowA+i, rowA, rowB+i, 0))
        triIndex += 1
        mesh.setTriangle(triIndex, Triangle(rowA, rowB, rowB+i, 0))
        triIndex += 1

    # base pole triangles
    rowA = 1 + (numStacks - 2) * numSlices
    rowB = rowA + numSlices
    for i in range(0, numSlices - 1) :
        mesh.setTriangle(triIndex, Triangle(rowA+i, rowA+i+1, rowB, 0))
        triIndex += 1
    i += 1
    mesh.setTriangle(triIndex, Triangle(rowA+i, rowA, rowB, 0))
    triIndex += 1
    if triIndex != mesh.getNumTriangles() :
        raise Exception("Triangle count mismatch")

    # create a dummy model
    model = Model('sphere')
    model.mesh = mesh
    model.addMaterial(Material.createDefaultMaterial())

    return model

#--- eof
