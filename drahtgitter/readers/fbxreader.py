'''
FBX reader. 
You need to install the FBX Python SDK for this: 
http://docs.autodesk.com/FBX/2014/ENU/FBX-SDK-Documentation/index.html
'''
from ..core import *
import fbx as fbx

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
        node = fbxScene.GetNode(nodeIndex)
        # for each attr node
        for attrIndex in range(0, node.GetNodeAttributeCount()) :
            fbxMesh = node.GetNodeAttributeByIndex(attrIndex)
            # if current attr node is a mesh...
            if fbxMesh.ClassId == fbx.FbxMesh.ClassId :
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
        node = fbxScene.GetNode(nodeIndex)
        # for each attr node
        for attrIndex in range(0, node.GetNodeAttributeCount()) :
            fbxMesh = node.GetNodeAttributeByIndex(attrIndex)
            # if current attr node is a mesh...
            if fbxMesh.ClassId == fbx.FbxMesh.ClassId :
                numTriangles += fbxMesh.GetPolygonCount()

    return numTriangles

#-------------------------------------------------------------------------------
def extractLayerElement(fbxMesh, fbxLayer, polyIndex, pointIndex, controlPointIndex) :
    '''
    Extracts a layer element (normal, uv, ...) and returns the
    element as Vector
    '''
    vertexIndex = polyIndex * 3 + pointIndex
    mapMode = fbxLayer.GetMappingMode()
    refMode = fbxLayer.GetReferenceMode()
    if mapMode == fbx.FbxLayerElement.eByControlPoint :
        if refMode == fbx.FbxLayerElement.eDirect :
            fbxVec = fbx.fbxLayer.GetDirectArray().GetAt(controlPointIndex)
        elif refMode == fbx.FbxLayerElement.eIndexToDirect :
            id = fbxLayer.GetIndexArray().GetAt(controlPointIndex)
            fbxVec = fbxLayer.GetDirectArray().GetAt(id)
    elif mapMode == fbx.FbxLayerElement.eByPolygonVertex :
        if refMode == fbx.FbxLayerElement.eDirect :
            fbxVec = fbxLayer.GetDirectArray().GetAt(vertexIndex)
        elif refMode == fbx.FbxLayerElement.eIndexToDirect :
            id = fbxLayer.GetIndexArray().GetAt(vertexIndex)
            fbxVec = fbxLayer.GetDirectArray().GetAt(id)
    elif mapMode == fbx.FbxLayerElement.eByPolygon :
        raise Exception('Mapping mode is eByPolygon')
    elif mapMode == fbx.FbxLayerElement.eAllSame :
        raise Exception('Mapping mode is eAllSame')
    elif mapMode == fbx.FbxLayerElement.eNone :
        raise Exception('Mapping mode is eNone')

    if isinstance(fbxVec, fbx.FbxVector2) : 
        vec = Vector(fbxVec[0], fbxVec[1])
    else :
        vec = Vector(fbxVec[0], fbxVec[1], fbxVec[2], fbxVec[3])
    return vec

#-------------------------------------------------------------------------------
def extractGeometry(mesh, fbxNode, fbxMesh, curTriIndex) :
    '''
    Takes an FbxMesh and it's parent node, and extracts the geometry
    in the mesh to the provided drahtgitter Mesh object.
    It is assumed that the FBX mesh has been triangulated!
    '''
    print 'extractGeomtry curTriIndex = {}'.format(curTriIndex)

    # extract positions; for each polygon:
    pos0 = ('position', 0)
    for polyIndex in range(0, fbxMesh.GetPolygonCount()) :
        # for each point in polygon
        numPoints = fbxMesh.GetPolygonSize(polyIndex)
        if numPoints != 3 :
            raise Exception('FBX mesh not triangulated!')

        # add vertex positions
        for pointIndex in range(0, numPoints) :
            posIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
            fbxPos = fbxMesh.GetControlPointAt(posIndex)
            pos = Vector(fbxPos[0], fbxPos[1], fbxPos[2])
            vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
            mesh.setVertex(vertexIndex, pos0, pos)

        # add a new triangles
        startIndex = (curTriIndex + polyIndex) * 3
        mesh.setTriangle(curTriIndex + polyIndex, Triangle((startIndex, startIndex+1, startIndex+2), 0))

    # extract additional vertex elements
    # FIXME: handle vertex color, tangent, binormals
    normalLayerCount = 0
    uvLayerCount = 0
    for layerIndex in range(0, fbxMesh.GetLayerCount()) :

        # extract normals
        lNormals = fbxMesh.GetLayer(layerIndex).GetNormals()
        if lNormals :
            normalComponent = ('normal', normalLayerCount)
            normalLayerCount += 1
            for polyIndex in range(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    norm = extractLayerElement(fbxMesh, lNormals, polyIndex, pointIndex, cpIndex)
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, normalComponent, norm)

        # extract UVs
        lUVs = fbxMesh.GetLayer(layerIndex).GetUVs()
        if lUVs :
            uvComponent = ('uv', uvLayerCount)
            uvLayerCount += 1
            for polyIndex in range(0, fbxMesh.GetPolygonCount()) :
                for pointIndex in range(0, fbxMesh.GetPolygonSize(polyIndex)) :
                    cpIndex = fbxMesh.GetPolygonVertex(polyIndex, pointIndex)
                    uv = extractLayerElement(fbxMesh, lUVs, polyIndex, pointIndex, cpIndex)
                    vertexIndex = (curTriIndex + polyIndex) * 3 + pointIndex
                    mesh.setVertex(vertexIndex, uvComponent, uv)


#-------------------------------------------------------------------------------
def readMesh(path) :
    '''
    Open an FBX file and extract geometry information, returns
    a Mesh object. This loses hierarchy and material information
    and only returns a single, flattened mesh.
    '''

    print 'fbxreader: {}'.format(path)

    # setup the FBX SDK and read the FBX file
    manager = fbx.FbxManager.Create()
    importer = fbx.FbxImporter.Create(manager, 'importer')
    status = importer.Initialize(path)
    if status == False :
        raise Exception('FbxImporter initialization failed!')

    scene = fbx.FbxScene.Create(manager, 'scene')
    importer.Import(scene)
    importer.Destroy()

    conv = fbx.FbxGeometryConverter(manager)

    # make sure the scene is triangulated
    if not conv.Triangulate(scene, True) :
        raise Exception('Failed to triangulate FBX scene!')

    # detect the required vertex layout and setup a mesh object
    vertexLayout = buildVertexLayout(scene)
    numTriangles = countTriangles(scene)
    outMesh = Mesh(vertexLayout, numTriangles * 3, numTriangles)

    # iterate over nodes
    curTriIndex = 0
    for nodeIndex in range(0, scene.GetNodeCount()) :
        fbxNode = scene.GetNode(nodeIndex)
        print 'node type: {}, name: {}'.format(fbxNode.ClassId.GetName(), fbxNode.GetName())
        # iterate over node attributes
        for attrIndex in range(0, fbxNode.GetNodeAttributeCount()) :
            attr = fbxNode.GetNodeAttributeByIndex(attrIndex)
            print '    attr type: {}, name: {}'.format(attr.ClassId.GetName(), attr.GetName())

            # if current node attribute is a mesh, extract the geometry
            if attr.ClassId == fbx.FbxMesh.ClassId :
                fbxMesh = attr
                extractGeometry(outMesh, fbxNode, fbxMesh, curTriIndex)
                curTriIndex += fbxMesh.GetPolygonCount()

    return outMesh
