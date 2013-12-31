'''
three.js writer
https://github.com/mrdoob/three.js/wiki/JSON-Model-format-3.1
'''
from ..core import *
from ..operators import fixVertexComponents as fixVertexComponents
from ..operators import deflate as deflate
import uuid

NormalBit = 1<<5
UvBit = 1<<3
ColorBit = 1<<7
MaterialBit = 1<<1

pos0 = ('position', 0)
norm0 = ('normal', 0)
uv0 = ('texcoord', 0)
color0 = ('color', 0)

#-------------------------------------------------------------------------------
def getFaceMask(model, withFaceMaterial) :
    faceMask = 0
    if model.mesh.vertexLayout.contains(norm0) :
        # has face-vertex normals
        faceMask |= NormalBit
    if model.mesh.vertexLayout.contains(uv0) :
        # has face-vertex uvs
        faceMask |= UvBit
    if model.mesh.vertexLayout.contains(color0) :
        # has face-vertex colors
        faceMask |= ColorBit
    if withFaceMaterial :
        # has face-materials
        faceMask |= MaterialBit
    return faceMask

#-------------------------------------------------------------------------------
def reducePositions(model) :
    posVertexLayout = VertexLayout()
    posVertexLayout.add(VertexComponent(pos0, 3))
    posModel = fixVertexComponents.do(model, posVertexLayout)
    posModel, posIndexMap = deflate.do(posModel)
    if posModel.mesh.getNumTriangles() != model.mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')
    return posModel

#-------------------------------------------------------------------------------
def writePositions(f, posModel) :
    posNumVertices = posModel.mesh.getNumVertices()
    f.write('\t"vertices": [ ')
    for vertexIndex in xrange(0, posNumVertices) :
        pos = posModel.mesh.getVertex(vertexIndex, pos0)
        f.write('{},{},{}'.format(pos.x, pos.y, pos.z))
        if vertexIndex < posNumVertices - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def reduceNormals(model) :
    normVertexLayout = VertexLayout()
    normVertexLayout.add(VertexComponent(norm0, 3))
    normModel = fixVertexComponents.do(model, normVertexLayout)
    normModel, normIndexMap = deflate.do(normModel)
    if normModel.mesh.getNumTriangles() != model.mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')
    return normModel    

#-------------------------------------------------------------------------------
def writeNormals(f, normModel) :
    normNumVertices = normModel.mesh.getNumVertices()
    f.write('\t"normals": [ ')
    for vertexIndex in xrange(0, normNumVertices) :
        norm = normModel.mesh.getVertex(vertexIndex, norm0)
        f.write('{},{},{}'.format(norm.x, norm.y, norm.z))
        if vertexIndex < normNumVertices - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def reduceUvs(model) :
    uvVertexLayout = VertexLayout()
    uvVertexLayout.add(VertexComponent(uv0, 2))
    uvModel = fixVertexComponents.do(model, uvVertexLayout)
    uvModel, uvIndexMap = deflate.do(uvModel)
    if uvModel.mesh.getNumTriangles() != model.mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')
    return uvModel

#-------------------------------------------------------------------------------
def writeUvs(f, uvModel) :
    uvNumVertices = uvModel.mesh.getNumVertices()
    f.write('\t"uvs": [ [ ')
    for vertexIndex in xrange(0, uvNumVertices) :
        uv = uvModel.mesh.getVertex(vertexIndex, uv0)
        f.write('{},{}'.format(uv.x, uv.y))
        if vertexIndex < uvNumVertices - 1 :
            f.write(',')
    f.write(' ] ]')

#-------------------------------------------------------------------------------
def reduceColors(model) :
    colorVertexLayout = VertexLayout()
    colorVertexLayout.add(VertexComponent(color0, 4))
    colorModel = fixVertexComponents.do(model, colorVertexLayout)
    colorModel, colorIndexMap = deflate.do(colorModel)
    if colorModel.mesh.getNumTriangles() != model.mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch')
    return colorModel

#-------------------------------------------------------------------------------
def writeColors(f, colorModel) :
    colorNumVertices = colorModel.mesh.getNumVertices()
    f.write('\t"colors": [ ')
    for vertexIndex in xrange(0, colorNumVertices) :
        color = colorModel.mesh.getVertex(vertexIndex, color0)
        f.write('{},{},{},{}'.format(color.x, color.y, color.z, color.w))
        if vertexIndex < colorNumVertices - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def writeFaceIndices(f, faceMask, srcModel, posModel, normModel, uvModel, colorModel) :

    f.write('\t"faces": [ ')
    numFaces = srcModel.mesh.getNumTriangles()
    for faceIndex in range(0, numFaces) :

        # lead byte
        f.write('{}'.format(faceMask))
        # 3 position vertex indices
        tri = posModel.mesh.triangles[faceIndex]
        f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write material index 
        if faceMask & MaterialBit :
            tri = srcModel.mesh.triangles[faceIndex]
            f.write(',{}'.format(tri.groupIndex))
        # write uv indices
        if faceMask & UvBit :
            tri = uvModel.mesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write normal indices
        if faceMask & NormalBit :
            tri = normModel.mesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write color indices
        if faceMask & ColorBit :
            tri = normModel.mesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        if faceIndex < numFaces - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def asThreeJsColor(material, paramName) :
    vec = material.getParam(paramName).value
    color = (int(vec.x * 255.0) & 255) << 16
    color |= (int(vec.y * 255.0) & 255) << 8
    color |= (int(vec.z * 255.0) & 255)
    return color

#-------------------------------------------------------------------------------
def writeMaterials(f, model) :
    '''
    Writes the materials in the Model object to the threejs file
    '''
    f.write('\t"materials": [\n')
    for matIndex in range(0, model.getNumMaterials()) :
        mat = model.materials[matIndex]

        f.write('\t\t{\n')
        f.write('\t\t\t"DbgColor" : 15658734,\n')
        f.write('\t\t\t"DbgIndex" : {:d},\n'.format(matIndex))
        f.write('\t\t\t"DbgName" : "{}",\n'.format(mat.name))
        f.write('\t\t\t"shading" : "{}",\n'.format(mat.type))
        if mat.hasParam('Diffuse') :
            val = mat.get('Diffuse')            
            f.write('\t\t\t"colorDiffuse" : [{},{},{}],\n'.format(val.x, val.y, val.z))
        if mat.hasParam('Ambient') :
            val = mat.get('Ambient')
            f.write('\t\t\t"colorAmbient" : [{},{},{}],\n'.format(val.x, val.y, val.z))
        if mat.hasParam('Emissive') :
            val = mat.get('Emissive')
            f.write('\t\t\t"colorEmissive" : [{},{},{}],\n'.format(val.x, val.y, val.z))
        if mat.hasParam('Specular') :
            val = mat.get('Specular')
            f.write('\t\t\t"colorSpecular" : [{},{},{}],\n'.format(val.x, val.y, val.z))
        if mat.hasParam('Shininess') :
            f.write('\t\t\t"shininess" : {},\n'.format(mat.get('Shininess')))
        if mat.hasParam('TransparentColor') :
            val = 1.0 - mat.get('TransparentColor').x
            f.write('\t\t\t"transparency" : {},\n'.format(val))
            if val < 1.0 :
                f.write('\t\t\t"transparent" : true\n')
            else :
                f.write('\t\t\t"transparent" : false\n')
        f.write('\t\t}')
        if matIndex < len(model.materials) - 1 :
            f.write(',')
        f.write('\n')
    f.write('\t]')

#-------------------------------------------------------------------------------
def writeGeneric(model, path, geomScale = 1.0) :
    '''
    Generic writer function, will be called by writeMesh and writeModels.
    If model != None materials will be written, otherwise only pure
    geometry.
    '''
    if not model.mesh.vertexLayout.contains(pos0) :
        raise Exception('Need at least position 0 vertex component!')

    # compute the face indices lead byte
    faceMask = getFaceMask(model, True)

    # extract vertex components and remove duplicates
    posModel = reducePositions(model)
    if faceMask & NormalBit :
        normModel = reduceNormals(model)
    else :
        normModel = None
    if faceMask & UvBit :
        uvModel = reduceUvs(model)
    else :
        uvModel = None
    if faceMask & ColorBit :
        colorModel = reduceColors(model)
    else :
        colorModel = None

    # write file
    f = open(path, 'w')

    f.write('{\n')
    f.write('\t"metadata" : {\n')
    f.write('\t\t"formatVersion" : 3.1,\n') 
    f.write('\t\t"generatedBy" : "drahtgitter",\n')
    f.write('\t\t"vertices" : {:d},\n'.format(posModel.mesh.getNumVertices()))
    f.write('\t\t"faces" : {:d},\n'.format(posModel.mesh.getNumTriangles()))
    if normModel: 
        f.write('\t\t"normals" : {:d},\n'.format(normModel.mesh.getNumVertices()))
    if uvModel:
        f.write('\t\t"uvs" : [{:d}],\n'.format(uvModel.mesh.getNumVertices()))
    if colorModel:
        f.write('\t\t"colors" : {:d},\n'.format(colorModel.mesh.getNumVertices()))
    if model != None :
        f.write('\t\t"materials" : {:d}\n'.format(model.getNumMaterials()))
    f.write('\t},\n')

    # write geometry scale
    f.write('\t"scale" : {},\n'.format(1.0 / geomScale))

    # write materials
    writeMaterials(f, model)
    f.write(',\n')

    writePositions(f, posModel)
    f.write(',\n')
    if normModel :
        writeNormals(f, normModel)
        f.write(',\n')
    if uvModel :
        writeUvs(f, uvModel)
        f.write(',\n')
    if colorModel :
        writeColors(f, colorModel)
        f.write(',\n')
    writeFaceIndices(f, faceMask, model, posModel, normModel, uvModel, colorModel)
    f.write('\n')

    f.write('}\n')
    f.close()


#-------------------------------------------------------------------------------
def write(model, path, geomScale = 1.0) :
    '''
    Write complete model information with per-face materials
    '''
    dgLogger.debug('writers.threejswriter.writeModel: model={}, path={}, geomScale={}'.format(model.name, path, geomScale))
    writeGeneric(model, path, geomScale)

#--- eof
