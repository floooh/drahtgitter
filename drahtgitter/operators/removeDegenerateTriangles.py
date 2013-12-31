'''
Check for and remove degenerate triangles (operates in-place)
'''

from ..core import *
#-------------------------------------------------------------------------------
def do(model) :

    dgLogger.debug('operators.removeDegenerateTriangles: model={}'.format(model.name))

    degenIndices = []
    triIndex = 0
    vertexLayout = model.mesh.vertexLayout
    vertexBuffer = model.mesh.vertexBuffer
    for tri in model.mesh.triangles :
        if tri.isDegenerate(vertexLayout, vertexBuffer) :
            degenIndices.append(triIndex)
            dgLogger.warning('Found degenerate triangle in {} tri-index {}'.format(model.name, triIndex))
        triIndex += 1

    for index in range(0, len(degenIndices)) :
        triIndex = degenIndices[index] - index
        del model.mesh.triangles[triIndex]
        dgLogger.warning('Removed degenerate triangle in {} at tri-index {}'.format(model.name, triIndex))

    '''
    for tri in model.mesh.triangles :
        if tri.isDegenerate(vertexLayout, vertexBuffer) :
            raise Exception('BLUB')
    '''

    return model

