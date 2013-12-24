'''
Cylinder mesh generator
FIXME: UV coords!
'''

from ..core import *

#-------------------------------------------------------------------------------
def generateMesh(vertexLayout, baseRadius, topRadius, length, numSlices, numStacks) :
    '''
    Generate cylinder mesh
    '''
    pos0 = ('position', 0)
    norm0 = ('normal', 0)
    tex0 = ('texcoord', 0)

    # generate a sin/cos table
    sinTable = []
    cosTable = []
    for i in range(0, numSlices) :
        val = 2.0 * math.pi * i / numSlices
        sinTable.append(math.sin(val))
        cosTable.append(math.cos(val))

    deltaRadius = topRadius - baseRadius
    sideLength  = math.sqrt(deltaRadius * deltaRadius + length * length)
    normalXY = 1.0
    normalZ  = 0.0
    if sideLength > 0.00001 :
        normalXY = length / sideLength
        normalZ  = -deltaRadius / sideLength

    # initialize mesh object
    numVerts = 2 * (numSlices+1) + (numStacks+1) * numSlices
    numTris  = 2 * numSlices + numSlices * numStacks * 2
    mesh = Mesh(vertexLayout, numVerts, numTris)

    # base cap vertices
    curVertexIndex = 0
    baseZ = -0.5 * length
    mesh.setVertex(curVertexIndex, pos0, Vector(0.0, 0.0, baseZ))
    mesh.setVertex(curVertexIndex, norm0, Vector(0.0, 0.0, -1.0))
    curVertexIndex += 1
    for i in range(0, numSlices) :
        pos = Vector(baseRadius * sinTable[i], baseRadius * cosTable[i], baseZ)
        mesh.setVertex(curVertexIndex, pos0, pos)
        mesh.setVertex(curVertexIndex, norm0, Vector(0.0, 0.0, -1.0))
        curVertexIndex += 1

    # stack vertices
    for j in range(0, numStacks + 1) :
        frac = float(j) / float(numStacks)
        z = length * (frac - 0.5)
        radius = baseRadius + frac * deltaRadius

        for i in range(0, numSlices) :
            pos  = Vector(radius * sinTable[i], radius * cosTable[i], z)
            norm = Vector(normalXY * sinTable[i], normalXY * cosTable[i], normalZ)  
            mesh.setVertex(curVertexIndex, pos0, pos)
            mesh.setVertex(curVertexIndex, norm0, norm)
            curVertexIndex += 1

    # top cap vertices
    topZ = 0.5 * length
    for i in range(0, numSlices) :
        pos = Vector(topRadius * sinTable[i], topRadius * cosTable[i], topZ)
        mesh.setVertex(curVertexIndex, pos0, pos)
        mesh.setVertex(curVertexIndex, norm0, Vector(0.0, 0.0, 1.0))
        curVertexIndex += 1

    mesh.setVertex(curVertexIndex, pos0, Vector(0.0, 0.0, topZ))
    mesh.setVertex(curVertexIndex, norm0, Vector(0.0, 0.0, 1.0))
    curVertexIndex += 1
    if curVertexIndex != mesh.getNumVertices() :
        raise Exception("Vertex count mismatch!")


    # generate triangles
    triIndex = 0

    # base cap triangles
    rowA = 0
    rowB = 1
    for i in range(0, numSlices-1) :
        mesh.setTriangle(triIndex, Triangle((rowA, rowB+i, rowB+i+1), 0))
        triIndex += 1
    i += 1
    mesh.setTriangle(triIndex, Triangle((rowA, rowB+i, rowB), 0))
    triIndex += 1

    # stack triangles
    for j in range(0, numStacks) :
        rowA = 1 + (j + 1) * numSlices
        rowB = rowA + numSlices
        for i in range(0, numSlices-1) :
            mesh.setTriangle(triIndex, Triangle((rowA+i, rowB+i, rowA+i+1), 0))
            triIndex += 1
            mesh.setTriangle(triIndex, Triangle((rowA+i+1, rowB+i, rowB+i+1), 0))
            triIndex += 1
        i += 1
        mesh.setTriangle(triIndex, Triangle((rowA+i, rowB+i, rowA), 0))
        triIndex += 1
        mesh.setTriangle(triIndex, Triangle((rowA, rowB+i, rowB), 0))
        triIndex += 1

    # top cap triangles
    rowA = 1 + (numStacks + 2) * numSlices
    rowB = rowA + numSlices
    for i in range(0, numSlices - 1) :
        mesh.setTriangle(triIndex, Triangle((rowA+i, rowB, rowA+i+1), 0))
        triIndex += 1
    i += 1
    mesh.setTriangle(triIndex, Triangle((rowA+i, rowB, rowA), 0))
    triIndex += 1
    if triIndex != mesh.getNumTriangles() :
        raise Exception("Triangle count mismatch")

    return mesh

#--- eof
