'''
three.js writer
https://github.com/mrdoob/three.js/wiki/JSON-Model-format-3.1
'''
from ..core import *
from ..operators import fixVertexComponents as fixVertexComponents
from ..operators import deflate as deflate

#-------------------------------------------------------------------------------
def writeMesh(mesh, path, geomScale = 1.0) :
    '''
    Only write geometry information, loses face material indices.
    '''
    pos0   = ('position', 0)
    norm0  = ('normal', 0)
    uv0    = ('texcoord', 0)
    color0 = ('color', 0)

    if not mesh.vertexLayout.contains(pos0) :
        raise Exception('Need at least position 0 vertex component!')

    # compute the face indices lead byte
    # triangles, no face material, 
    faceMask = 0
    normalBit = 1<<5
    uvBit = 1<<3
    colorBit = 1<<7
    if mesh.vertexLayout.contains(norm0) :
        # has face-vertex normals
        faceMask |= normalBit
    if mesh.vertexLayout.contains(uv0) :
        # has face-vertex uvs
        faceMask |= uvBit
    if mesh.vertexLayout.contains(color0) :
        # has face-vertex colors
        faceMask |= colorBit

    # write file
    f = open(path, 'w')
    f.write('{\n'
            '    "metadata": {\n'
            '        "version": 4,\n' 
            '        "type": "geometry",\n'
            '        "generator": "drahtgitter"\n'
            '    },\n')

    # extract positions from mesh and remove duplicates
    posVertexLayout = VertexLayout()
    posVertexLayout.add(VertexComponent(pos0, 3))
    posMesh = fixVertexComponents.do(mesh, posVertexLayout)
    posMesh, posIndexMap = deflate.do(posMesh)
    if posMesh.getNumTriangles() != mesh.getNumTriangles() :
        raise Exception('Triangle count mismatch!')

    # write positions
    posNumVertices = posMesh.getNumVertices()
    f.write('    "vertices": [ ')
    for vertexIndex in range(0, posNumVertices) :
        pos = Vector.scale(posMesh.getVertex(vertexIndex, pos0), geomScale)
        f.write('{},{},{}'.format(pos.x, pos.y, pos.z))
        if vertexIndex < posNumVertices - 1 :
            f.write(',')
    f.write(' ],\n')

    if faceMask & normalBit :
        # if mesh has normals, extract and remove dups
        normVertexLayout = VertexLayout()
        normVertexLayout.add(VertexComponent(norm0, 3))
        normMesh = fixVertexComponents.do(mesh, normVertexLayout)
        normMesh, normIndexMap = deflate.do(normMesh)
        if normMesh.getNumTriangles() != mesh.getNumTriangles() :
            raise Exception('Triangle count mismatch!')

        # write reduced normals
        normNumVertices = normMesh.getNumVertices()
        f.write('    "normals": [ ')
        for vertexIndex in range(0, normNumVertices) :
            norm = normMesh.getVertex(vertexIndex, norm0)
            f.write('{},{},{}'.format(norm.x, norm.y, norm.z))
            if vertexIndex < normNumVertices - 1 :
                f.write(',')
        f.write(' ],\n')

    if faceMask & uvBit :
        # if mesh has uvs, extract and remove dups
        uvVertexLayout = VertexLayout()
        uvVertexLayout.add(VertexComponent(uv0, 2))
        uvMesh = fixVertexComponents.do(mesh, uvVertexLayout)
        uvMesh, uvIndexMap = deflate.do(uvMesh)
        if uvMesh.getNumTriangles() != mesh.getNumTriangles() :
            raise Exception('Triangle count mismatch!')

        # write reduced uvs
        # FIXME: why the [ [ ] ], instead of [ ] ?
        uvNumVertices = uvMesh.getNumVertices()
        f.write('    "uvs": [ [ ')
        for vertexIndex in range(0, uvNumVertices) :
            uv = uvMesh.getVertex(vertexIndex, uv0)
            f.write('{},{}'.format(uv.x, uv.y))
            if vertexIndex < uvNumVertices - 1 :
                f.write(',')
        f.write(' ] ],\n')

    if faceMask & colorBit :
        # if mesh has colors, extract and remove dups
        colorVertexLayout = VertexLayout()
        colorVertexLayout.add(VertexComponent(color0, 4))
        colorMesh = fixVertexComponents.do(mesh, colorVertexLayout)
        colorMesh, colorIndexMap = deflate.do(colorMesh)
        if colorMesh.getNumTriangles() != mesh.getNumTriangles() :
            raise Exception('Triangle count mismatch')

        # write reduced colors
        colorNumVertices = colorMesh.getNumVertices()
        f.write('    "colors": [ ')
        for vertexIndex in range(0, colorNumVertices) :
            color = colorMesh.getVertex(vertexIndex, color0)
            f.write('{},{},{},{}'.format(color.x, color.y, color.z, color.w))
            if vertexIndex < colorNumVertices - 1 :
                f.write(',')
        f.write(' ],\n')

    # write face indices
    f.write('    "faces": [ ')
    numFaces = mesh.getNumTriangles()
    for faceIndex in range(0, numFaces) :

        # lead byte
        f.write('{}'.format(faceMask))
        # 3 position vertex indices
        tri = posMesh.triangles[faceIndex]
        f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write uv indices
        if faceMask & uvBit :
            tri = uvMesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write normal indices
        if faceMask & normalBit :
            tri = normMesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        # write color indices
        if faceMask & colorBit :
            tri = normMesh.triangles[faceIndex]
            f.write(',{},{},{}'.format(tri.vertexIndex0, tri.vertexIndex1, tri.vertexIndex2))
        if faceIndex < numFaces - 1 :
            f.write(',')
    f.write(' ]\n')

    # and we're done
    f.write('}\n')

#--- eof
