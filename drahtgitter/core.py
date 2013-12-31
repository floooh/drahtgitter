'''
Defines the drahtgitter core classes like Mesh, Material, Bone, ...
'''

from array import array
import logging
import math
import copy
import sys

'''
Initialize the drahtgitter logger object
'''
logging.basicConfig(stream=sys.stdout)
dgLogger = logging.getLogger('dg')
dgLogger.setLevel(logging.DEBUG)

# NOTE: this tolerance is for ALL vertex components!
DG_TOLERANCE = 0.00000001

#-------------------------------------------------------------------------------
class Vector :
    '''
    A very simple 1..4D vector class 
    '''
    def __init__(self, _x=0.0, _y=0.0, _z=0.0, _w=0.0) :
        '''
        Construct from 0..4 values
        '''
        self.x = _x;
        self.y = _y;
        self.z = _z;
        self.w = _w;

    def __eq__(self, rhs) :
        '''
        Equality operator
        '''
        return self.x == rhs.x and self.y == rhs.y and self.z == rhs.z and self.w == rhs.w

    def __ne__(self, rhs) :
        '''
        Inequality operator
        '''
        return self.x != rhs.x or self.y != rhs.y or self.z != rhs.z or self.w != rhs.w

    def __lt__(self, rhs) :
        return NotImplemented
    def __le__(self, rhs) :
        return NotImplemented
    def __gt__(self, rhs) :
        return NotImplemented
    def __ge__(self, rhs) :
        return NotImplemented

    def __add__(self, rhs) :
        return Vector(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z, self.w + rhs.w)

    def __sub__(self, rhs) :
        return Vector(self.x - rhs.x, self.y - rhs.y, self.z - rhs.z, self.w - rhs.w)

    def __mul__(self, rhs) :
        return Vector(self.x * rhs.x, self.y * rhs.y, self.z * rhs.z, self.w * rhs.w)

    @staticmethod
    def equal(v0, v1, tolerance) :
        bx = abs(v1.x - v0.x) < tolerance
        by = abs(v1.y - v0.y) < tolerance
        bz = abs(v1.z - v0.z) < tolerance
        bw = abs(v1.w - v0.w) < tolerance
        return bx and by and bz and bw

    @staticmethod
    def scale(v, s) :
        return Vector(v.x * s, v.y * s, v.z * s, v.w * s)

    @staticmethod
    def length(v) :
        return math.sqrt(v.x * v.x + v.y * v.y + v.z * v.z + v.w * v.w)

    @staticmethod
    def cross3(v0, v1) :
        x = v0.y * v1.z - v0.z * v1.y
        y = v0.z * v1.x - v0.x * v1.z
        z = v0.x * v1.y - v0.y * v1.x
        return Vector(x, y, z)

    @staticmethod
    def dot3(v0, v1) :
        return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

    @staticmethod
    def normalize(v) :
        l = Vector.length(v)
        return Vector(v.x / l, v.y / l, v.z / l, v.w / l)

#-------------------------------------------------------------------------------
class Triangle :
    '''
    A triangle in a Mesh object
    '''
    def __init__(self, vi0=0, vi1=0, vi2=0, groupIndex=0) :
        self.vertexIndex0 = vi0
        self.vertexIndex1 = vi1
        self.vertexIndex2 = vi2
        self.groupIndex = groupIndex
        self.normalX = 0.0
        self.normalY = 0.0
        self.normalZ = 0.0

    def getNormal(self) :
        return Vector(self.normalX, self.normalY, self.normalZ)

    def isDegenerate(self, vertexLayout, vertexBuffer) :
        '''
        Checks whether this triangle is degenerate.
        '''

        # check vertex indices
        if self.vertexIndex0 == self.vertexIndex1 or self.vertexIndex0 == self.vertexIndex2 or self.vertexIndex1 == self.vertexIndex2 :
            return True

        # check for identical vertices (within DG_TOLERANCE)
        posOffset = vertexLayout.getComponent(('position', 0)).offset
        index0 = self.vertexIndex0 * vertexLayout.size + posOffset
        v0 = Vector(vertexBuffer[index0 + 0], vertexBuffer[index0 + 1], vertexBuffer[index0 + 2])
        index1 = self.vertexIndex1 * vertexLayout.size + posOffset
        v1 = Vector(vertexBuffer[index1 + 0], vertexBuffer[index1 + 1], vertexBuffer[index1 + 2])
        index2 = self.vertexIndex2 * vertexLayout.size + posOffset
        v2 = Vector(vertexBuffer[index2 + 0], vertexBuffer[index2 + 1], vertexBuffer[index2 + 2])
        if Vector.equal(v0, v1, DG_TOLERANCE) or Vector.equal(v1, v2, DG_TOLERANCE) or Vector.equal(v0, v2, DG_TOLERANCE) :
            return True

        # check the cross product
        v10 = v1 - v0
        v20 = v2 - v0
        cross = Vector.cross3(v10, v20)
        if Vector.equal(cross, Vector(0.0, 0.0, 0.0), 0.0000001) :
            return True

        return False

#-------------------------------------------------------------------------------
class VertexComponent :
    '''
    A single entry in a VertexLayout, describes one vertex component
    '''
    def __init__(self, nameAndIndex, size) :
        '''
        NOTE: The index is the "stream index", for instance the
        first set of uv coords would have an index=0, the second index=1.
        The offset is the offset of the float data in a vertex (0 is start of
        vertex), size if the number of floats in the vertex (must be between 1 and 4)
        '''
        self.nameAndIndex = nameAndIndex
        self.offset = 0
        self.size   = size

    def validate(self) :
        if self.nameAndIndex[1] < 0 or self.nameAndIndex[1] > 8 :
            raise Exception('Stream index must be between 0 and 8')
        if self.size < 1 or self.size > 4 :
            raise Exception('Component size must be between 1 and 4')


#-------------------------------------------------------------------------------
class VertexLayout :
    '''
    Describe vertex components and their offset and size in a 
    plain array of floats.
    '''
    def __init__(self) :
        self.size = 0
        self.vertexComponents = dict()

    def contains(self, nameAndIndex) :
        ''' 
        Test if a component with name and stream index already exists
        '''
        return nameAndIndex in self.vertexComponents

    def add(self, comp) :
        '''
        Add a vertex component definition to the vertex layout
        '''
        comp.validate()
        if self.contains(comp.nameAndIndex) :
            raise Exception('Component already exists!')
        comp.offset = self.size
        self.size += comp.size
        self.vertexComponents[comp.nameAndIndex] = comp;

    def validate(self) :
        '''
        Tests whether the vertex layout is valid.
        '''
        # sizes must add up
        size = 0
        for c in self.vertexComponents.values() :
            size += c.size
        if not size == self.size :
            raise Exception("Vertex component sizes don't add up")

    def getComponent(self, nameAndIndex) :
        '''
        Get a component object by its nameAndIndex type, returns 
        None if not found.
        '''
        if self.contains(nameAndIndex) :
            return self.vertexComponents[nameAndIndex] 
        else :
            return None

#-------------------------------------------------------------------------------
class Mesh :
    def __init__(self, layout=VertexLayout(), numVertices=0, numTriangles=0) :
        '''
        Holds everything for describing geometry.
        '''
        self.vertexBuffer = [0.0] * numVertices * layout.size
        self.vertexLayout = layout
        self.triangles    = [Triangle() for _ in xrange(0, numTriangles)]

    def reserveVertices(self, num) :
        '''
        Make room for n vertices
        '''
        for i in xrange(0, num * self.vertexLayout.size) :
            self.vertexBuffer.append(0.0)

    def reserveTriangles(self, num) :
        '''
        Make room for n triangles
        '''
        for i in xrange(0, num) :
            self.triangles.append(Triangle())

    def setTriangle(self, triangleIndex, triangle) :
        '''
        Add a triangle to the mesh
        '''
        self.triangles[triangleIndex] = triangle

    def getNumVertices(self) :
        '''
        Get number of vertices
        '''
        return len(self.vertexBuffer) / self.vertexLayout.size

    def getNumTriangles(self) :
        '''
        Get number of triangles
        '''
        return len(self.triangles)
        
    def getComponent(self, nameAndIndex) :
        '''
        Get a component in the vertex layout
        ''' 
        return self.vertexLayout.getComponent(nameAndIndex)

    def getComponentOffset(self, nameAndIndex) :
        '''
        Get the offset of a vertex component into the vertex
        '''
        return self.vertexLayout.getComponent(nameAndIndex).offset
        
    def getComponentSize(self, nameAndIndex) :
        '''
        Get the size of a vertex component
        '''
        return self.vertexLayout.getComponent(nameAndIndex).size

    def setVertex(self, vertexIndex, nameAndIndex, vec) :
        '''
        Set the float values of a vertex component from a vector object.
        This is convenient but slow.
        '''
        if self.vertexLayout.contains(nameAndIndex) :
            comp = self.vertexLayout.getComponent(nameAndIndex)
            vbOffset = comp.offset + vertexIndex * self.vertexLayout.size
            self.vertexBuffer[vbOffset] = vec.x
            if comp.size > 1 :
                self.vertexBuffer[vbOffset + 1] = vec.y
            if comp.size > 2 :
                self.vertexBuffer[vbOffset + 2] = vec.z
            if comp.size > 3 :
                self.vertexBuffer[vbOffset + 3] = vec.w

    def getVertex(self, vertexIndex, nameAndIndex) :
        '''
        Return a Vector object with the values of a vertex component
        This is convenient but slow.
        '''
        vec = Vector()
        if self.vertexLayout.contains(nameAndIndex) :
            comp = self.vertexLayout.getComponent(nameAndIndex)
            vbOffset = comp.offset + vertexIndex * self.vertexLayout.size
            vec.x = self.vertexBuffer[vbOffset]
            if comp.size > 1 :
                vec.y = self.vertexBuffer[vbOffset + 1]
            if comp.size > 2 :
                vec.z = self.vertexBuffer[vbOffset + 2]
            if comp.size > 3 :
                vec.w = self.vertexBuffer[vbOffset + 3]
        return vec

    def setData1(self, vertexIndex, compOffset, x) :
        '''
        Directly set 1D vertex data with component-offset.
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        self.vertexBuffer[bufIndex] = x

    def setData2(self, vertexIndex, compOffset, x, y) :
        '''
        Directly set 2D vertex data with component-offset.
        This is faster but less convenient then setVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        self.vertexBuffer[bufIndex] = x
        self.vertexBuffer[bufIndex + 1] = y

    def setData3(self, vertexIndex, compOffset, x, y, z) :
        '''
        Directly set 3D vertex data with component-offset.
        This is faster but less convenient then setVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        self.vertexBuffer[bufIndex] = x
        self.vertexBuffer[bufIndex + 1] = y
        self.vertexBuffer[bufIndex + 2] = z

    def setData4(self, vertexIndex, compOffset, x, y, z, w) :
        '''
        Directly set 4D vertex data with component-offset.
        This is faster but less convenient then setVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        self.vertexBuffer[bufIndex] = x
        self.vertexBuffer[bufIndex + 1] = y
        self.vertexBuffer[bufIndex + 2] = z
        self.vertexBuffer[bufIndex + 4] = w

    def getData1(self, vertexIndex, compOffset) :
        '''
        Directly get 1D vertex data with component-offset.
        This is faster but less convenient then getVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        return self.vertexBuffer[bufIndex]

    def getData2(self, vertexIndex, compOffset) :
        '''
        Directly get 2D vertex data with component-offset.
        This is faster but less convenient then getVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        return self.vertexBuffer[bufIndex], self.vertexBuffer[bufIndex+1]

    def getData3(self, vertexIndex, compOffset) :
        '''
        Directly get 3D vertex data with component-offset.
        This is faster but less convenient then getVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        return self.vertexBuffer[bufIndex], self.vertexBuffer[bufIndex+1], self.vertexBuffer[bufIndex+2]

    def getData4(self, vertexIndex, compOffset) :
        '''
        Directly get 4D vertex data with component-offset.
        This is faster but less convenient then getVertex()
        '''
        bufIndex = vertexIndex * self.vertexLayout.size + compOffset
        return self.vertexBuffer[bufIndex], self.vertexBuffer[bufIndex+1], self.vertexBuffer[bufIndex+2], self.vertexBuffer[bufIndex+3]

    def dumpVertices(self, nameAndIndex):
        '''
        Debug-print vertices
        '''
        compOffset = self.vertexLayout.getComponent(nameAndIndex).offset
        compSize   = self.vertexLayout.getComponent(nameAndIndex).size
        vertexSize = self.vertexLayout.size
        for vertexIndex in xrange(0, self.getNumVertices()) :
            sys.stdout.write('{} {}{}: '.format(vertexIndex, nameAndIndex[0], nameAndIndex[1]))
            bufferIndex = vertexSize * vertexIndex + compOffset
            for i in range(bufferIndex, bufferIndex + compSize) :
                sys.stdout.write('{} '.format(self.vertexBuffer[i]))
            sys.stdout.write('\n')

#-------------------------------------------------------------------------------
class VertexKey :
    ''' 
    A key class for sorting vertices.
    ''' 
    def __init__(self, index, vertexLayoutSize) :
        self.vertexIndex = index
        self.bufferIndex = index * vertexLayoutSize

    @staticmethod
    def init(mesh) :
        ''' 
        this must be called before sorting to setup a few
        static variables used in the cmp method
        '''
        VertexKey.vertexBuffer = mesh.vertexBuffer
        VertexKey.layoutSize   = mesh.vertexLayout.size

    def cmp(self, other) :
        i = 0
        while i < VertexKey.layoutSize:
            selfValue  = VertexKey.vertexBuffer[self.bufferIndex + i]
            otherValue = VertexKey.vertexBuffer[other.bufferIndex + i]
            if (selfValue+DG_TOLERANCE) < otherValue :
                return -1
            elif selfValue > (otherValue+DG_TOLERANCE) :
                return 1
            i += 1
        # fallthrough: vertices are identical
        return 0

    def __lt__(self, other) :
        # inlined for performance (only __lt__ is called as sort hook)
        i = 0
        while i < VertexKey.layoutSize:
            selfValue  = VertexKey.vertexBuffer[self.bufferIndex + i]
            otherValue = VertexKey.vertexBuffer[other.bufferIndex + i]
            if (selfValue+DG_TOLERANCE) < otherValue :
                return True
            elif selfValue > (otherValue+DG_TOLERANCE) :
                return False
            i += 1
        # fallthrough: vertices are identical
        return False
    def __gt__(self, other) :
        return self.cmp(other) > 0
    def __eq__(self, other) :
        return self.cmp(other) == 0
    def __le__(self, other) :
        return self.cmp(other) <= 0
    def __ge__(self, other) :
        return self.cmp(other) >= 0
    def __ne__(self, other) :
        # inlined for performance
        i = 0
        while i < VertexKey.layoutSize:
            selfValue  = VertexKey.vertexBuffer[self.bufferIndex + i]
            otherValue = VertexKey.vertexBuffer[other.bufferIndex + i]
            if abs(selfValue - otherValue) >= DG_TOLERANCE :
                return True
            i += 1
        # fallthrough: vertices are identical
        return False

#-------------------------------------------------------------------------------
class VertexKeyMap :
    '''
    Holds a mesh reference and a list of (usually sorted) VertexKeys. Mainly
    used to find and remove duplicate vertices from a mesh
    '''
    def __init__(self, mesh) :
        self.mesh = mesh
        vertexLayoutSize = mesh.vertexLayout.size
        self.keys = [VertexKey(i, vertexLayoutSize) for i in xrange(0, mesh.getNumVertices())]

    def sort(self) :
        '''
        Sort the contained vertex key
        '''
        if len(self.keys) > 1 and self.keys[1].bufferIndex != self.mesh.vertexLayout.size :
            raise Exception('Vertex layout size has changed!')
        VertexKey.init(self.mesh)
        self.keys.sort()

#-------------------------------------------------------------------------------
class MatParam :
    '''
    A material parameter (a key, a type and a value).
    '''

    # param types
    Float = 1
    Float2 = 2
    Float3 = 3
    Float4 = 4
    Int = 6
    Bool = 7
    String = 8
    Texture = 9

    def __init__(self, name=None, type=None, value=None) :
        self.name = name
        self.type = type
        self.value = value

    def valueAsString(self, sep=',') :
        if self.type == MatParam.Float :
            return '{}'.format(self.value)
        elif self.type == MatParam.Float2 :
            return '{}{}{}'.format(self.value.x, sep, self.value.y)
        elif self.type == MatParam.Float3 :
            return '{}{}{}{}{}'.format(self.value.x, sep, self.value.y, sep, self.value.z)
        elif self.type == MatParam.Float4:
            return '{}{}{}{}{}{}{}'.format(self.value.x, sep, self.value.y, sep, self.value.z, sep, self.value.w)
        elif self.type == MatParam.Int :
            return '{:d}'.format(self.value)
        elif self.type == MatParam.Bool :
            if self.value :
                return 'true'
            else :
                return 'false'
        elif self.type == MatParam.String or self.type == MatParam.Texture :
            return self.value

    def typeAsString(self) :
        if self.type == MatParam.Float: 
            return 'Float'
        elif self.type == MatParam.Float2:
            return 'Float2'
        elif self.type == MatParam.Float3:
            return 'Float3'
        elif self.type == MatParam.Float4:
            return 'Float4'
        elif self.type == MatParam.Int:
            return 'Int'
        elif self.type == MatParam.Bool:
            return 'Bool'
        elif self.type == MatParam.String:
            return 'String'
        elif self.type == MatParam.Texture:
            return 'Texture'
        else :
            raise Exception('Invalid type!')

    def dump(self) :
        '''
        Dump content to stdout for debugging
        '''
        dgLogger.info('    Name: {}, Type: {}, Value: {}'.format(self.name, self.typeAsString(), self.valueAsString()))

#-------------------------------------------------------------------------------
class Material :
    '''
    Describes a material of a 3D model, basically just a collection
    of MaterialParam objects.
    '''
    def __init__(self, name='undefined', type='undefined') :
        self.name = name
        self.type = type
        self.shaderName = 'None'
        self.params = []
        self.useCount = 0

    @staticmethod
    def createDefaultMaterial() :
        '''
        Returns a material object initialized with default params
        '''
        mat = Material('default', 'Lambert')
        mat.addParam(MatParam('Emissive', MatParam.Float4, Vector(0.0, 0.0, 0.0)))
        mat.addParam(MatParam('Ambient', MatParam.Float4, Vector(0.2, 0.2, 0.2)))
        mat.addParam(MatParam('Diffuse', MatParam.Float4, Vector(0.8, 0.8, 0.8)))
        mat.addParam(MatParam('Bump', MatParam.Float4, Vector(0.0, 0.0, 0.0)))
        mat.addParam(MatParam('NormalMap', MatParam.Float4, Vector(0.0, 0.0, 0.0)))
        mat.addParam(MatParam('TransparentColor', MatParam.Float4, Vector(0.0, 0.0, 0.0)))
        mat.addParam(MatParam('DisplacementColor', MatParam.Float4, Vector(0.0, 0.0, 0.0)))
        return mat

    def hasParam(self, paramName) :
        '''
        Test if the material already contains a parameter
        '''
        for param in self.params :
            if param.name == paramName :
                return True
        else :
            return False

    def addParam(self, param) :
        '''
        Add a material param to the material
        '''
        if self.hasParam(param.name) :
            dgLogger.warning('Param {} already exists on material {}'.format(self.name, param.name))
        else :
            self.params.append(param)

    def getParam(self, name) :
        '''
        Get a param by name, returns None if not found
        '''
        for param in self.params :
            if param.name == name :
                return param
        else :
            return None

    def get(self, name) :
        '''
        Short-cut method to directly get the value of a param.
        '''
        if self.hasParam(name) :
            return self.getParam(name).value
        else :
            return None

    def dump(self) :
        '''
        Dump debug info to stdout.
        '''
        dgLogger.info('  Name: {}'.format(self.name))
        dgLogger.info('  ShaderName: {}'.format(self.shaderName))
        dgLogger.info('  Type: {}'.format(self.type))
        dgLogger.info('  UseCount: {:d}'.format(self.useCount))
        dgLogger.info('  Params:')
        for param in self.params :
            param.dump()

#-------------------------------------------------------------------------------
class Model :
    '''
    Top-level object which holds all elements required for a 3D object:
        1..N Mesh objects
        1..N Material objects
        1..N Bone objects
        a hierarchy of Node objects with references into Mesh, Material, Bone array

    TODO: animation support, probably specific character stuff
    '''
    def __init__(self, name) :
        self.name = name
        self.mesh = None
        self.materials = []

    def getNumMaterials(self) :
        return len(self.materials)

    def findMaterial(self, name) :
        '''
        Return material by name, or None if not exists
        '''
        for mat in self.materials :
            if mat.name == name :
                return mat
        else :
            return None

    def findMaterialIndex(self, name) :
        '''
        Return material index by name, or None if not exists
        '''
        i = 0
        for mat in self.materials :
            if mat.name == name :
                return i
            i += 1
        else :
            return None

    def addMaterial(self, material) :
        '''
        Add a new material, the material must not yet exist
        '''
        if self.findMaterial(material.name) != None :
            dgLogger.warning('Material {} already exists on Model {}!'.format(material.name, self.name))
        else :
            self.materials.append(material)

    def dumpMaterials(self) :
        '''
        Dump materials to stdout for debugging
        '''
        for i in range(0, len(self.materials)) :
            dgLogger.info('Material {:d}'.format(i))
            self.materials[i].dump()

#--- eof

