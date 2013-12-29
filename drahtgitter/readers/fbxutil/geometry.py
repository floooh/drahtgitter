'''
Geometry export related FBX utility functions.
'''

from ...core import *
from ..fbxutil.general import extractLayerElement
from fbx import *

#-------------------------------------------------------------------------------
def buildVertexLayout(fbxScene) :
    '''
    Builds a vertex layout matching the information in the 
    provided fbxScene (iterates over all meshes and their layers)
    '''
    vertexLayout = VertexLayout()
    vertexLayout.add(VertexComponent(('position', 0), 3))

    # for each node...
    for nodeIndex in range(0, fbxScene.GetNodeCount()) :
        fbxNode = fbxScene.GetNode(nodeIndex)
        fbxMesh = fbxNode.GetMesh()
        if fbxMesh != None :

            # for each layer in mesh...
            normalCount   = 0
            tangentCount  = 0
            binormalCount = 0
            uvCount       = 0
            colorCount    = 0                
            for layerIndex in range(0, fbxMesh.GetLayerCount()) :
                fbxLayer = fbxMesh.GetLayer(layerIndex)
                if fbxLayer.GetNormals() :
                    vc = VertexComponent(('normal', normalCount), 3)
                    if not vertexLayout.contains(vc.nameAndIndex) :
                        print 'Normal layer detected at layer {}'.format(layerIndex)
                        vertexLayout.add(vc)
                        normalCount += 1
                if fbxLayer.GetTangents() :
                    vc = VertexComponent(('tangent', tangentCount), 3)
                    if not vertexLayout.contains(vc.nameAndIndex) :
                        print 'Tangent layer detected at layer {}'.format(layerIndex)
                        vertexLayout.add(vc)
                        tangentCount += 1
                if fbxLayer.GetBinormals() :
                    vc = VertexComponent(('binormal', binormalCount), 3)
                    if not vertexLayout.contains(vc.nameAndIndex) :
                        print 'Binormal layer detected at layer {}'.format(layerIndex)
                        vertexLayout.add(vc)
                        binormalCount += 1
                if fbxLayer.GetUVs() :
                    vc = VertexComponent(('texcoord', uvCount), 2)
                    if not vertexLayout.contains(vc.nameAndIndex) :
                        print 'UV layer detected at layer {}'.format(layerIndex)
                        vertexLayout.add(vc)
                        uvCount += 1
                if fbxLayer.GetVertexColors() :
                    vc = VertexComponent(('color', colorCount), 4)
                    if not vertexLayout.contains(vc.nameAndIndex) :
                        print 'Color layer detected at layer {}'.format(layerIndex)
                        vertexLayout.add(vc)
                        colorCount += 1

    return vertexLayout

#-------------------------------------------------------------------------------
def countTriangles(fbxScene) :
    '''
    Count the number of triangles in the fbx scene
    '''
    numTriangles = 0

    # for each node...
    for nodeIndex in range(0, fbxScene.GetNodeCount()) :
        fbxNode = fbxScene.GetNode(nodeIndex)
        fbxMesh = fbxNode.GetMesh()
        if fbxMesh != None :
            numTriangles += fbxMesh.GetPolygonCount()

    return numTriangles

#-------------------------------------------------------------------------------
def extractGeometry(mesh, fbxNode, fbxMesh, materialIndex, curTriIndex) :
    '''
    Takes an FbxMesh and it's parent node, and extracts the geometry
    in the mesh to the provided drahtgitter Mesh object.
    NOTE: It is assumed that the FBX mesh has been triangulated and
    that each mesh has only one material assigned (the 
    FbxGeometryConverter.SplitMeshesPerMaterial method can be used for this)
    '''

    # get the current node's global transform
    affineMatrix = fbxNode.EvaluateGlobalTransform()
    pointTransform = FbxMatrix(affineMatrix)
    affineMatrix.SetT(FbxVector4(0.0, 0.0, 0.0, 0.0))
    normalTransform = FbxMatrix(affineMatrix)

    # extract positions; for each polygon:
    pos0 = ('position', 0)
    for polyIndex in xrange(0, fbxMesh.GetPolygonCount()) :
        # for each point in polygon
        numPoints = fbxMesh.GetPolygonSize(polyIndex)
        if numPoints != 3 :
            raise Exception('FBX mesh not triangulated!')

        # add vertex positions
        for pointIndex in range(0, numPoints) :
            posIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
            fbxPos = fbxMesh.GetControlPointAt(posIndex)
            fbxPos = pointTransform.MultNormalize(fbxPos)
            pos = Vector(fbxPos[0], fbxPos[1], fbxPos[2])
            vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
            mesh.setVertex(vertexIndex, pos0, pos)

        # add a new triangles
        startIndex = (curTriIndex + polyIndex) * 3
        mesh.setTriangle(curTriIndex + polyIndex, Triangle(startIndex, startIndex+1, startIndex+2, materialIndex))

    # extract additional vertex elements
    # FIXME: handle vertex color
    normalLayerCount = 0
    tangentLayerCount = 0
    binormalLayerCount = 0
    colorLayerCount = 0
    uvLayerCount = 0
    for layerIndex in range(0, fbxMesh.GetLayerCount()) :

        # extract normals
        lNormals = fbxMesh.GetLayer(layerIndex).GetNormals()
        if lNormals :
            normalComponent = ('normal', normalLayerCount)
            normalLayerCount += 1
            for polyIndex in xrange(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    fbxNorm = extractLayerElement(fbxMesh, lNormals, polyIndex, pointIndex, cpIndex)
                    fbxNorm = normalTransform.MultNormalize(fbxNorm)
                    fbxNorm.Normalize()
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, normalComponent, Vector(fbxNorm[0], fbxNorm[1], fbxNorm[2]))

        # extract tangents
        lTangents = fbxMesh.GetLayer(layerIndex).GetTangents()
        if lTangents :
            tangentComponent = ('tangent', tangentLayerCount)
            tangentLayerCount += 1
            for polyIndex in xrange(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    fbxTang = extractLayerElement(fbxMesh, lTangents, polyIndex, pointIndex, cpIndex)
                    fbxTang = normalTransform.MultNormalize(fbxTang)
                    fbxTang.Normalize()
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, tangentComponent, Vector(fbxTang[0], fbxTang[1], fbxTang[2]))

        # extract binormals
        lBinormals = fbxMesh.GetLayer(layerIndex).GetBinormals()
        if lBinormals :
            binormalComponent = ('binormal', binormalLayerCount)
            binormalLayerCount += 1
            for polyIndex in xrange(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    fbxBinorm = extractLayerElement(fbxMesh, lBinormals, polyIndex, pointIndex, cpIndex)
                    fbxBinorm = normalTransform.MultNormalize(fbxNorm)
                    fbxNorm.Normalize()
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, binormalComponent, Vector(fbxBinorm[0], fbxBinorm[1], fbxBinorm[2]))

        # extract UVs
        lUVs = fbxMesh.GetLayer(layerIndex).GetUVs()
        if lUVs :
            uvComponent = ('texcoord', uvLayerCount)
            uvLayerCount += 1
            for polyIndex in range(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    fbxUV = extractLayerElement(fbxMesh, lUVs, polyIndex, pointIndex, cpIndex)
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, uvComponent, Vector(fbxUV[0], fbxUV[1]))

        # extract vertex colors
        lColors = fbxMesh.GetLayer(layerIndex).GetVertexColors()
        if lColors :
            colorComponent = ('color', colorLayerCount)
            colorLayerCount += 1
            for polyIndex in range(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    fbxColor = extractLayerElement(fbxMesh, lColors, polyIndex, pointIndex, cpIndex)
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, colorComponent, Vector(fbxColor[0], fbxColor[1], fbxColor[2], fbxColor[3]))


