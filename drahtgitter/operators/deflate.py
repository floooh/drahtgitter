'''
Returns a new Mesh object with duplicate vertices removed and
also returns a integer array which maps vertices in the
source mesh to vertices in the returned mesh
'''
from ..core import *
import time

#-------------------------------------------------------------------------------
def do(srcMesh) :

    print 'Deflate before: numVertices {}'.format(srcMesh.getNumVertices())

    # create a sorted key map
    startTime = time.time()
    keyMap = VertexKeyMap(srcMesh)
    keyMap.sort()
    print 'Sorting: {}'.format(time.time() - startTime)
    startTime = time.time()

    # create a new vertex buffer with duplicates removed
    startTime = time.time()
    outIndexMap = [-1] * len(keyMap.keys)
    vertexSize = srcMesh.vertexLayout.size()
    dstVertexBuffer = array('f')
    lastUniqueIndex = -1
    curDstVertexIndex = 0
    for vertexIndex in xrange(0, len(keyMap.keys)):
        # copy unique vertices and skip duplicate vertices
        if lastUniqueIndex == -1 or keyMap.keys[vertexIndex] != keyMap.keys[lastUniqueIndex] :
            # new vertex encountered
            lastUniqueIndex = vertexIndex
            # copy the vertex data
            for valueIndex in range(0, vertexSize) :
                dstVertexBuffer.append(srcMesh.vertexBuffer[keyMap.keys[vertexIndex].bufferIndex + valueIndex])
            curDstVertexIndex += 1            

        # map original vertex index to new vertex index
        outIndexMap[keyMap.keys[vertexIndex].vertexIndex] = curDstVertexIndex - 1

    print 'Remove dups: {}'.format(time.time() - startTime)

    # create a new mesh
    dstMesh = Mesh(copy.deepcopy(srcMesh.vertexLayout))
    dstMesh.vertexBuffer = dstVertexBuffer

    # create a new triangle array for the dst mesh with mapped vertex indices
    dstMesh.triangles = copy.deepcopy(srcMesh.triangles)
    for tri in dstMesh.triangles :
        tri.vertexIndex0 = outIndexMap[tri.vertexIndex0]
        tri.vertexIndex1 = outIndexMap[tri.vertexIndex1]
        tri.vertexIndex2 = outIndexMap[tri.vertexIndex2]

    print 'Deflate after: numVertices {}'.format(dstMesh.getNumVertices())

    return dstMesh, outIndexMap

#--- eof