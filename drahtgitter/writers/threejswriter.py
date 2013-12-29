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
def getFaceMask(mesh, withFaceMaterial) :
    faceMask = 0
    if mesh.vertexLayout.contains(norm0) :
        # has face-vertex normals
        faceMask |= NormalBit
    if mesh.vertexLayout.contains(uv0) :
        # has face-vertex uvs
        faceMask |= UvBit
    if mesh.vertexLayout.contains(color0) :
        # has face-vertex colors
        faceMask |= ColorBit
    if withFaceMaterial :
        # has face-materials
        faceMask |= MaterialBit
    return faceMask

#-------------------------------------------------------------------------------
def reducePositions(mesh) :
    posVertexLayout = VertexLayout()
    posVertexLayout.add(VertexComponent(pos0, 3))
    posMesh = fixVertexComponents.do(mesh, posVertexLayout)
    posMesh, posIndexMap = deflate.do(posMesh)
    if posMesh.getNumTriangles() != mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')
    return posMesh

#-------------------------------------------------------------------------------
def writePositions(f, posMesh) :
    posNumVertices = posMesh.getNumVertices()
    f.write('\t"vertices": [ ')
    for vertexIndex in range(0, posNumVertices) :
        pos = posMesh.getVertex(vertexIndex, pos0)
        f.write('{},{},{}'.format(pos.x, pos.y, pos.z))
        if vertexIndex < posNumVertices - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def reduceNormals(mesh) :
    normVertexLayout = VertexLayout()
    normVertexLayout.add(VertexComponent(norm0, 3))
    normMesh = fixVertexComponents.do(mesh, normVertexLayout)
    normMesh, normIndexMap = deflate.do(normMesh)
    if normMesh.getNumTriangles() != mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')
    return normMesh    

#-------------------------------------------------------------------------------
def writeNormals(f, normMesh) :
    normNumVertices = normMesh.getNumVertices()
    f.write('\t"normals": [ ')
    for vertexIndex in range(0, normNumVertices) :
        norm = normMesh.getVertex(vertexIndex, norm0)
        f.write('{},{},{}'.format(norm.x, norm.y, norm.z))
        if vertexIndex < normNumVertices - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def reduceUvs(mesh) :
    uvVertexLayout = VertexLayout()
    uvVertexLayout.add(VertexComponent(uv0, 2))
    uvMesh = fixVertexComponents.do(mesh, uvVertexLayout)
    uvMesh, uvIndexMap = deflate.do(uvMesh)
    if uvMesh.getNumTriangles() != mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')
    return uvMesh

#-------------------------------------------------------------------------------
def writeUvs(f, uvMesh) :
    uvNumVertices = uvMesh.getNumVertices()
    f.write('\t"uvs": [ [ ')
    for vertexIndex in range(0, uvNumVertices) :
        uv = uvMesh.getVertex(vertexIndex, uv0)
        f.write('{},{}'.format(uv.x, uv.y))
        if vertexIndex < uvNumVertices - 1 :
            f.write(',')
    f.write(' ] ]')

#-------------------------------------------------------------------------------
def reduceColors(mesh) :
    colorVertexLayout = VertexLayout()
    colorVertexLayout.add(VertexComponent(color0, 4))
    colorMesh = fixVertexComponents.do(mesh, colorVertexLayout)
    colorMesh, colorIndexMap = deflate.do(colorMesh)
    if colorMesh.getNumTriangles() != mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch')
    return colorMesh

#-------------------------------------------------------------------------------
def writeColors(f, colorMesh) :
    colorNumVertices = colorMesh.getNumVertices()
    f.write('\t"colors": [ ')
    for vertexIndex in range(0, colorNumVertices) :
        color = colorMesh.getVertex(vertexIndex, color0)
        f.write('{},{},{},{}'.format(color.x, color.y, color.z, color.w))
        if vertexIndex < colorNumVertices - 1 :
            f.write(',')
    f.write(' ]')

#-------------------------------------------------------------------------------
def writeFaceIndices(f, faceMask, srcMesh, posMesh, normMesh, uvMesh, colorMesh) :

    f.write('\t"faces": [ ')
    numFaces = srcMesh.getNumTriangles()
    for faceIndex in range(0, numFaces) :

        # lead byte
        f.write('{}'.format(faceMask))
        # 3 position vertex indices
        tri = posMesh.triangles[faceIndex]
        f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write material index 
        if faceMask & MaterialBit :
            tri = srcMesh.triangles[faceIndex]
            f.write(',{}'.format(tri.groupIndex))
        # write uv indices
        if faceMask & UvBit :
            tri = uvMesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write normal indices
        if faceMask & NormalBit :
            tri = normMesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write color indices
        if faceMask & ColorBit :
            tri = normMesh.triangles[faceIndex]
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
def writeGeneric(model, mesh, path, geomScale = 1.0) :
    '''
    Generic writer function, will be called by writeMesh and writeModels.
    If model != None materials will be written, otherwise only pure
    geometry.
    '''
    if not mesh.vertexLayout.contains(pos0) :
        raise Exception('Need at least position 0 vertex component!')

    # compute the face indices lead byte
    faceMask = getFaceMask(mesh, model != None)

    # extract vertex components and remove duplicates
    posMesh = reducePositions(mesh)
    if faceMask & NormalBit :
        normMesh = reduceNormals(mesh)
    else :
        normMesh = None
    if faceMask & UvBit :
        uvMesh = reduceUvs(mesh)
    else :
        uvMesh = None
    if faceMask & ColorBit :
        colorMesh = reduceColors(mesh)
    else :
        colorMesh = None

    # write file
    f = open(path, 'w')

    f.write('{\n')
    f.write('\t"metadata" : {\n')
    f.write('\t\t"formatVersion" : 3.1,\n') 
    f.write('\t\t"generatedBy" : "drahtgitter",\n')
    f.write('\t\t"vertices" : {:d},\n'.format(posMesh.getNumVertices()))
    f.write('\t\t"faces" : {:d},\n'.format(posMesh.getNumTriangles()))
    if normMesh: 
        f.write('\t\t"normals" : {:d},\n'.format(normMesh.getNumVertices()))
    if uvMesh:
        f.write('\t\t"uvs" : [{:d}],\n'.format(uvMesh.getNumVertices()))
    if colorMesh:
        f.write('\t\t"colors" : {:d},\n'.format(colorMesh.getNumVertices()))
    if model != None :
        f.write('\t\t"materials" : {:d}\n'.format(model.getNumMaterials()))
    f.write('\t},\n')

    # write geometry scale
    f.write('\t"scale" : {},\n'.format(1.0 / geomScale))

    # write materials
    if model != None :
        writeMaterials(f, model)
        f.write(',\n')

    writePositions(f, posMesh)
    f.write(',\n')
    if normMesh :
        writeNormals(f, normMesh)
        f.write(',\n')
    if uvMesh :
        writeUvs(f, uvMesh)
        f.write(',\n')
    if colorMesh :
        writeColors(f, colorMesh)
        f.write(',\n')
    writeFaceIndices(f, faceMask, mesh, posMesh, normMesh, uvMesh, colorMesh)
    f.write('\n')

    f.write('}\n')
    f.close()


#-------------------------------------------------------------------------------
def writeMesh(mesh, path, geomScale = 1.0) :
    '''
    Only write geometry information, loses face material indices.
    '''
    writeGeneric(None, mesh, path, geomScale)

#-------------------------------------------------------------------------------
def writeModel(model, path, geomScale = 1.0) :
    '''
    Write complete model information with per-face materials
    '''
    writeGeneric(model, model.mesh, path, geomScale)

#--- eof
