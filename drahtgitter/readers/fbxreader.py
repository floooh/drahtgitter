'''
FBX reader. 
You need to install the FBX Python SDK for this: 
http://docs.autodesk.com/FBX/2014/ENU/FBX-SDK-Documentation/index.html
'''
from ..core import *
import fbx as fbx

#-------------------------------------------------------------------------------
def loadScene(manager, path) :
    '''
    Load an FBX file into a FbxScene object
    '''
    importer = fbx.FbxImporter.Create(manager, 'importer')
    status = importer.Initialize(path)
    if status == False :
        raise Exception('FbxImporter: failed to load scene!')

    scene = fbx.FbxScene.Create(manager, 'scene')
    importer.Import(scene)
    importer.Destroy()

    return scene

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
            nodeAttr = node.GetNodeAttributeByIndex(attrIndex)
            # if current attr node is a mesh...
            if nodeAttr.GetAttributeType() == fbx.FbxNodeAttribute.eMesh :
                fbxMesh = nodeAttr

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
            nodeAttr = node.GetNodeAttributeByIndex(attrIndex)
            # if current attr node is a mesh...
            if nodeAttr.GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
                fbxMesh = nodeAttr
                numTriangles += fbxMesh.GetPolygonCount()

    return numTriangles

#-------------------------------------------------------------------------------
def extractLayerElement(fbxMesh, fbxLayer, polyIndex, pointIndex, controlPointIndex) :
    '''
    Extracts a layer element (normal, uv, ...) and returns the
    element as FbxVector4
    '''
    vertexIndex = polyIndex * 3 + pointIndex
    mapMode = fbxLayer.GetMappingMode()
    refMode = fbxLayer.GetReferenceMode()
    if mapMode == fbx.FbxLayerElement.eByControlPoint :
        if refMode == fbx.FbxLayerElement.eDirect :
            fbxVec = fbxLayer.GetDirectArray().GetAt(controlPointIndex)
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
        return fbx.FbxVector4(fbxVec[0], fbxVec[1], 0.0, 0.0)
    else :
        return fbxVec
 
#-------------------------------------------------------------------------------
def extractGeometry(mesh, fbxNode, fbxMesh, curTriIndex) :
    '''
    Takes an FbxMesh and it's parent node, and extracts the geometry
    in the mesh to the provided drahtgitter Mesh object.
    It is assumed that the FBX mesh has been triangulated!
    '''
    print 'extractGeomtry curTriIndex = {}'.format(curTriIndex)

    # get the current node's global transform
    affineMatrix = fbxNode.EvaluateGlobalTransform()
    pointTransform = fbx.FbxMatrix(affineMatrix)
    affineMatrix.SetT(fbx.FbxVector4(0.0, 0.0, 0.0, 0.0))
    normalTransform = fbx.FbxMatrix(affineMatrix)

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
        mesh.setTriangle(curTriIndex + polyIndex, Triangle(startIndex, startIndex+1, startIndex+2, 0))

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

#-------------------------------------------------------------------------------
def isHardwareShader(fbxMaterial) :
    '''
    Tests whether the provided material is a hardware shader
    (HLSL or CGFX)
    '''
    impl = fbx.GetImplementation(fbxMaterial, 'ImplementationHLSL')
    if not impl :
        impl = fbx.GetImplementation(fbxMaterial, 'ImplementationCGFX')
    return impl != None

#-------------------------------------------------------------------------------
def extractHardwareShaderParams(fbxMaterial) :
    '''
    Extract the shader parameters for a hardware
    shader material
    '''
    impl = fbx.GetImplementation(fbxMaterial, 'ImplementationHLSL')
    shdType = 'HLSL'
    if not impl :
        impl = fbx.GetImplementation(fbxMaterial, 'ImplementationCGFX')
        shdType = 'CGFX'
    if not impl :
        raise Exception('Not a hardware shader!')

    print 'Hardware Shader: {}'.format(fbxMaterial.GetName())
    print 'Shader Type: {}'.format(shdType)

    # parse the binding table
    table = impl.GetRootTable()
    for entryIndex in range(0, table.GetEntryCount()) :
        entry = table.GetEntry(entryIndex)

        print 'Entry Type: {}'.format(entry.GetType(True))
        print 'Entry Source: {}'.format(entry.GetSource())

        # FIXME: CONTINUE!

#-------------------------------------------------------------------------------
def isPhongShader(fbxMaterial) :
    return fbxMaterial.GetClassId().Is(fbx.FbxSurfacePhong.ClassId)

#-------------------------------------------------------------------------------
def extractPhongShaderParams(fbxMaterial) :

    print 'Phong Shader: {}'.format(fbxMaterial.GetName())

    print 'Shading Model: {}'.format(fbxMaterial.ShadingModel.Get())
    print 'Multilayer: {}'.format(fbxMaterial.MultiLayer.Get())
    print 'Emissive: {} {} {} * {}'.format(fbxMaterial.Emissive.Get()[0], fbxMaterial.Emissive.Get()[1], fbxMaterial.Emissive.Get()[2], fbxMaterial.EmissiveFactor.Get())
    print 'Ambient: {} {} {} * {}'.format(fbxMaterial.Ambient.Get()[0], fbxMaterial.Ambient.Get()[1], fbxMaterial.Ambient.Get()[2], fbxMaterial.AmbientFactor.Get())
    print 'Diffuse: {} {} {} * {}'.format(fbxMaterial.Diffuse.Get()[0], fbxMaterial.Diffuse.Get()[1], fbxMaterial.Diffuse.Get()[2], fbxMaterial.DiffuseFactor.Get())
    print 'Bump: {} {} {} * {}'.format(fbxMaterial.Bump.Get()[0], fbxMaterial.Bump.Get()[1], fbxMaterial.Bump.Get()[2], fbxMaterial.BumpFactor.Get())    
    print 'NormalMap: {} {} {}'.format(fbxMaterial.NormalMap.Get()[0], fbxMaterial.NormalMap.Get()[1], fbxMaterial.NormalMap.Get()[2])
    print 'TransparentColor: {} {} {} * {}'.format(fbxMaterial.TransparentColor.Get()[0], fbxMaterial.TransparentColor.Get()[1], fbxMaterial.TransparentColor.Get()[2], fbxMaterial.TransparencyFactor.Get())
    print 'DisplacementColor: {} {} {} * {}'.format(fbxMaterial.DisplacementColor.Get()[0], fbxMaterial.DisplacementColor.Get()[1], fbxMaterial.DisplacementColor.Get()[2], fbxMaterial.DisplacementFactor.Get())
    print 'VectorDisplacementColor: {} {} {} * {}'.format(fbxMaterial.VectorDisplacementColor.Get()[0], fbxMaterial.VectorDisplacementColor.Get()[1], fbxMaterial.VectorDisplacementColor.Get()[2], fbxMaterial.VectorDisplacementFactor.Get())
    print 'Specular: {} {} {} * {}'.format(fbxMaterial.Specular.Get()[0], fbxMaterial.Specular.Get()[1], fbxMaterial.Specular.Get()[2], fbxMaterial.SpecularFactor.Get())
    print 'Reflection: {} {} {} * {}'.format(fbxMaterial.Reflection.Get()[0], fbxMaterial.Reflection.Get()[1], fbxMaterial.Reflection.Get()[2], fbxMaterial.ReflectionFactor.Get())
    print 'Shininess: {}'.format(fbxMaterial.Shininess.Get())

#-------------------------------------------------------------------------------
def isLambertShader(fbxMaterial) :
    return fbxMaterial.GetClassId().Is(fbx.FbxSurfaceLambert.ClassId)

#-------------------------------------------------------------------------------
def extractLambertShaderParams(fbxMaterial) :
    
    print 'Lambert Shader: {}'.format(fbxMaterial.GetName())

    print 'Shading Model: {}'.format(fbxMaterial.ShadingModel.Get())
    print 'Multilayer: {}'.format(fbxMaterial.MultiLayer.Get())
    print 'Emissive: {} {} {} * {}'.format(fbxMaterial.Emissive.Get()[0], fbxMaterial.Emissive.Get()[1], fbxMaterial.Emissive.Get()[2], fbxMaterial.EmissiveFactor.Get())
    print 'Ambient: {} {} {} * {}'.format(fbxMaterial.Ambient.Get()[0], fbxMaterial.Ambient.Get()[1], fbxMaterial.Ambient.Get()[2], fbxMaterial.AmbientFactor.Get())
    print 'Diffuse: {} {} {} * {}'.format(fbxMaterial.Diffuse.Get()[0], fbxMaterial.Diffuse.Get()[1], fbxMaterial.Diffuse.Get()[2], fbxMaterial.DiffuseFactor.Get())
    print 'Bump: {} {} {} * {}'.format(fbxMaterial.Bump.Get()[0], fbxMaterial.Bump.Get()[1], fbxMaterial.Bump.Get()[2], fbxMaterial.BumpFactor.Get())    
    print 'NormalMap: {} {} {}'.format(fbxMaterial.NormalMap.Get()[0], fbxMaterial.NormalMap.Get()[1], fbxMaterial.NormalMap.Get()[2])
    print 'TransparentColor: {} {} {} * {}'.format(fbxMaterial.TransparentColor.Get()[0], fbxMaterial.TransparentColor.Get()[1], fbxMaterial.TransparentColor.Get()[2], fbxMaterial.TransparencyFactor.Get())
    print 'DisplacementColor: {} {} {} * {}'.format(fbxMaterial.DisplacementColor.Get()[0], fbxMaterial.DisplacementColor.Get()[1], fbxMaterial.DisplacementColor.Get()[2], fbxMaterial.DisplacementFactor.Get())
    print 'VectorDisplacementColor: {} {} {} * {}'.format(fbxMaterial.VectorDisplacementColor.Get()[0], fbxMaterial.VectorDisplacementColor.Get()[1], fbxMaterial.VectorDisplacementColor.Get()[2], fbxMaterial.VectorDisplacementFactor.Get())

#-------------------------------------------------------------------------------
def extractMaterials(fbxNode, fbxMesh) :
    '''
    see DisplayMaterial.py in FBX SDK importexport sample
    '''
    if fbxMesh.GetNode() != fbxNode :
        raise Excpetion('FbxNode != fbxMesh (should not happen')
    matCount = fbxNode.GetMaterialCount()

    for layerIndex in range(0, fbxMesh.GetLayerCount()) :
        lMaterials = fbxMesh.GetLayer(layerIndex).GetMaterials()
        if lMaterials: 
            if lMaterials.GetReferenceMode() == fbx.FbxLayerElement.eIndex :
                raise Exception('Material Layer ref mode is eIndex')

            for matIndex in range(0, matCount) :
                fbxMaterial = fbxNode.GetMaterial(matIndex)

                # check shader type and extract shader params
                if isHardwareShader(fbxMaterial) :
                    extractHardwareShaderParams(fbxMaterial)
                elif isPhongShader(fbxMaterial) :
                    extractPhongShaderParams(fbxMaterial)
                elif isLambertShader(fbxMaterial) :
                    extractLambertShaderParams(fbxMaterial)
                else :
                    raise Exception('Unknown material type')

#-------------------------------------------------------------------------------
def readMesh(path) :
    '''
    Open an FBX file and extract geometry information, returns
    a Mesh object. This loses hierarchy and material information
    and only returns a single, flattened mesh.
    '''

    print 'fbxreader.readMesh: {}'.format(path)

    # setup the FBX SDK and read the FBX file
    manager = fbx.FbxManager.Create()
    scene = loadScene(manager, path)
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
            nodeAttr = fbxNode.GetNodeAttributeByIndex(attrIndex)
            print '    attr type: {}, name: {}'.format(nodeAttr.ClassId.GetName(), nodeAttr.GetName())

            # if current node attribute is a mesh, extract the geometry
            if nodeAttr.GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
                fbxMesh = nodeAttr
                extractGeometry(outMesh, fbxNode, fbxMesh, curTriIndex)
                curTriIndex += fbxMesh.GetPolygonCount()

    scene.Destroy()
    manager.Destroy()

    return outMesh

#-------------------------------------------------------------------------------
def readModel(path) :
    '''
    Reads an FBX file with material information, but flattens node hierarchy.
    FIXME: use a hint attribute to decide if a node must be preserved
    '''

    print 'fbxReader.readModel: {}'.format(path)

    # setup the FBX SDK and read the FBX file
    manager = fbx.FbxManager.Create()
    scene = loadScene(manager, path)
    conv = fbx.FbxGeometryConverter(manager)

    # make sure the scene is triangulated
    if not conv.Triangulate(scene, True) :
        raise Exception('Failed to triangulate FBX scene!')

    # iterate over nodes
    curTriIndex = 0
    for nodeIndex in range(0, scene.GetNodeCount()) :
        fbxNode = scene.GetNode(nodeIndex)
        print 'node type: {}, name: {}'.format(fbxNode.ClassId.GetName(), fbxNode.GetName())
        # iterate over node attributes
        for attrIndex in range(0, fbxNode.GetNodeAttributeCount()) :
            nodeAttr = fbxNode.GetNodeAttributeByIndex(attrIndex)
            print '    attr type: {}, name: {}'.format(nodeAttr.ClassId.GetName(), nodeAttr.GetName())

            # NOTE: THIS WILL ENCOUNTER THE SAME MATERIALS MANY TIMES...
            # 
            if nodeAttr.GetAttributeType() == fbx.FbxNodeAttribute.eMesh:
                fbxMesh = nodeAttr
                extractMaterials(fbxNode, fbxMesh)

    scene.Destroy()
    manager.Destroy()
