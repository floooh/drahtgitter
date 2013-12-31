'''
Returns a new Model object with duplicate vertices removed and
also returns a integer array which maps vertices in the
source mesh to vertices in the returned mesh. 
NOTE that the global DG_TOLERANCE variable defines the
precision with which the equality test is performed!
'''
from ..core import *

#-------------------------------------------------------------------------------
def do(srcModel) :

    dgLogger.debug('operators.deflate: model={}'.format(srcModel.name))

    srcMesh = srcModel.mesh

    # create a sorted key map
    keyMap = VertexKeyMap(srcMesh)
    keyMap.sort()

    # create a new vertex buffer with duplicates removed
    outIndexMap = [-1] * len(keyMap.keys)
    vertexSize = srcMesh.vertexLayout.size
    dstVertexBuffer = []
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

    # create a new model
    dstModel = copy.deepcopy(srcModel)
    dstModel.mesh.vertexBuffer = dstVertexBuffer

    # create a new triangle array for the dst mesh with mapped vertex indices
    for tri in dstModel.mesh.triangles :
        tri.vertexIndex0 = outIndexMap[tri.vertexIndex0]
        tri.vertexIndex1 = outIndexMap[tri.vertexIndex1]
        tri.vertexIndex2 = outIndexMap[tri.vertexIndex2]

    return dstModel, outIndexMap

#--- eof