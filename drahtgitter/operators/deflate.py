'''
Returns a new Mesh object with duplicate vertices removed and
also returns a integer array which maps vertices in the
source mesh to vertices in the returned mesh
'''
from ..core import *

#-------------------------------------------------------------------------------
def do(srcMesh) :

    # create a sorted key map
    keyMap = VertexKeyMap(srcMesh)
    keyMap.sort()
    outIndexMap = [-1] * len(keyMap.keys)

    # create a new vertex buffer with duplicates removed
    vertexSize = srcMesh.vertexLayout.size()
    dstVertexBuffer = array('f')
    lastUniqueIndex = -1
    curDstVertexIndex = 0
    for vertexIndex in range(0, len(keyMap.keys)):
        # copy unique vertices and skip duplicate vertices
        if lastUniqueIndex == -1 or keyMap.keys[vertexIndex] != keyMap.keys[lastUniqueIndex] :
            # new vertex encountered
            lastUniqueIndex = vertexIndex
            # copy the vertex data
            for valueIndex in range(0, vertexSize) :
                dstVertexBuffer.append(srcMesh.vertexBuffer[keyMap.keys[vertexIndex].index * vertexSize + valueIndex])
            curDstVertexIndex += 1            

        # map original vertex index to new vertex index
        outIndexMap[keyMap.keys[vertexIndex].index] = curDstVertexIndex - 1

    if -1 in outIndexMap :
        raise Exception('Empty slot in outIndexMap, should not happen!')

    # create a new mesh
    dstMesh = Mesh(copy.deepcopy(srcMesh.vertexLayout))
    dstMesh.vertexBuffer = dstVertexBuffer

    # create a new triangle array for the dst mesh with mapped vertex indices
    dstMesh.triangles = copy.deepcopy(srcMesh.triangles)
    for tri in dstMesh.triangles :
        i0 = outIndexMap[tri.vertexIndices[0]]
        i1 = outIndexMap[tri.vertexIndices[1]]
        i2 = outIndexMap[tri.vertexIndices[2]]
        tri.vertexIndices = (i0, i1, i2)

    return dstMesh, outIndexMap

#--- eof