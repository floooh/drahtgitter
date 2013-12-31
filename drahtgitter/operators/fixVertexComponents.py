'''
Copy the provided Model object and add or remove vertex components as 
requested. This will return a new Model object.
'''

from ..core import *
#-------------------------------------------------------------------------------
def do(srcModel, dstVertexLayout) :

    dgLogger.debug('operators.fixVertexComponents: model={}'.format(srcModel.name))

    # create a mapping from existing to new vertex components,
    # one entry per float, -1 for new components (will be
    # filled with 0.0)
    srcMesh = srcModel.mesh
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
    for vertexIndex in xrange(0, numVertices) :
        for mapIndex in range(0, len(mapping)) :
            dstIndex = vertexIndex * dstVertexLayout.size + mapIndex
            if mapping[mapIndex] >= 0 :
                srcIndex = vertexIndex * srcVertexLayout.size + mapping[mapIndex]
                dstMesh.vertexBuffer[dstIndex] = srcMesh.vertexBuffer[srcIndex]
            else :
                dstMesh.vertexBuffer[dstIndex] = 0.0
    dstMesh.triangles = copy.deepcopy(srcMesh.triangles)

    # create a new Model
    dstModel = copy.deepcopy(srcModel)
    dstModel.mesh = dstMesh

    return dstModel

#--- eof

