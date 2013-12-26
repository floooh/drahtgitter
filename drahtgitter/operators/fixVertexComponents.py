'''
Copy the provided mesh object and add or remove vertex components as 
requested. This will return a new mesh object.
'''

from ..core import *
#-------------------------------------------------------------------------------
def do(srcMesh, dstVertexLayout) :

    # create a mapping from existing to new vertex components,
    # one entry per float, -1 for new components (will be
    # filled with 0.0)
    srcVertexLayout = srcMesh.vertexLayout
    mapping = []
    for dstComp in dstVertexLayout.vertexComponents.values() :
        if srcVertexLayout.contains(dstComp.nameAndIndex) :
            srcComp = srcVertexLayout.getComponent(dstComp.nameAndIndex)
            for i in range(0, dstComp.size) :
                if i < srcComp.size :
                    # a copy mapping
                    mapping.append(srcComp.offset + i)
                else :
                    # missing vertex component element, fill with -1
                    mapping.append(-1)
        else :
            # vertex component isn't in src mesh, fill with -1's
            for i in range(0, dstComp.size) :
                mapping.append(-1)

    # mapping now contains a >= 0 index for each float to be copied
    # and -1 for each new float (will be set to 0.0)
    # copy over old values, and fill new values to 0.0
    numVertices  = srcMesh.getNumVertices()
    numTriangles = srcMesh.getNumTriangles()
    dstMesh = Mesh(dstVertexLayout, numVertices, numTriangles)
    for vertexIndex in range(0, numVertices) :
        for mapIndex in range(0, len(mapping)) :
            dstIndex = vertexIndex * dstVertexLayout.size() + mapIndex
            if mapping[mapIndex] >= 0 :
                srcIndex = vertexIndex * srcVertexLayout.size() + mapping[mapIndex]
                dstMesh.vertexBuffer[dstIndex] = srcMesh.vertexBuffer[srcIndex]
            else :
                dstMesh.vertexBuffer[dstIndex] = 0.0

    # copy over the triangles    
    dstMesh.triangles = copy.deepcopy(srcMesh.triangles)

    return dstMesh

#--- eof

