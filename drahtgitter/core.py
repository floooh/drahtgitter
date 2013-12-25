'''
Defines the drahtgitter core classes like Mesh, Material, Bone, ...
'''

from array import array
import math
import copy

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
        bw = abs(v1.w - v0.z) < tolerance
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
    def __init__(self, vertexIndices=(0,0,0), matIndex=0) :
        if len(vertexIndices) != 3 :
            raise Exception('Invalid number of vertexIndices, must be 3')
        self.vertexIndices = vertexIndices
        self.materialIndex = matIndex
        self.normal = Vector(0.0, 0.0, 0.0)

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
        self.validNames = ('position', 'texcoord', 'normal', 'tangent', 'binormal', 'color', 'weights', 'indices', 'custom')
        self.nameAndIndex = nameAndIndex
        self.offset = 0
        self.size   = size

    def validate(self) :
        if not self.nameAndIndex[0] in self.validNames :
            raise Exception('Invalid vertex component name: ' + self.nameAndIndex[0])
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
        self.currentOffset = 0
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
        if not isinstance(comp, VertexComponent) :
            raise TypeError('Component must be of class VertexComponent!')
        if self.contains(comp.nameAndIndex) :
            raise Exception('Component already exists!')
        comp.offset = self.currentOffset
        self.currentOffset += comp.size
        self.vertexComponents[comp.nameAndIndex] = comp;

    def validate(self) :
        '''
        Tests whether the vertex layout is valid.
        '''
        # must contain position with stream index 0
        if not ('position', 0) in self.vertexComponents:
            raise Exception('VertexLayout must contain a position with stream index 0')

        # sizes must add up
        size = 0
        for c in self.vertexComponents.values() :
            size += c.size
        if not size == self.currentOffset :
            raise Exception("Vertex component sizes don't add up")

    def getComponent(self, nameAndIndex) :
        '''
        Get a component object by its nameAndIndex type
        '''
        if not self.contains(nameAndIndex) :
            raise Exception('Invalid vertex component type ' + nameAndIndex)
        return self.vertexComponents[nameAndIndex] 

    def size(self) :
        '''
        Gets the size of the vertex layout
        '''
        return self.currentOffset


#-------------------------------------------------------------------------------
class Mesh :
    def __init__(self, layout=VertexLayout(), numVertices=0, numTriangles=0) :
        '''
        Holds everything for describing geometry.
        '''
        self.vertexBuffer = array('f', [0.0] * numVertices * layout.size())
        self.vertexLayout = layout
        self.triangles    = [Triangle() for _ in range(0, numTriangles)]

    def addVertices(self, num) :
        '''
        Make room for n vertices
        '''
        for i in range(0, num * self.vertexLayout.size()) :
            self.vertexBuffer.append(0.0)

    def addTriangles(self, num) :
        '''
        Make room for n triangles
        '''
        for i in range(0, num) :
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
        return len(self.vertexBuffer) / self.vertexLayout.size()

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
        '''
        if self.vertexLayout.contains(nameAndIndex) :
            comp = self.vertexLayout.getComponent(nameAndIndex)
            vbOffset = comp.offset + vertexIndex * self.vertexLayout.size()
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
        '''
        vec = Vector()
        if self.vertexLayout.contains(nameAndIndex) :
            comp = self.vertexLayout.getComponent(nameAndIndex)
            vbOffset = comp.offset + vertexIndex * self.vertexLayout.size()
            vec.x = self.vertexBuffer[vbOffset]
            if comp.size > 1 :
                vec.y = self.vertexBuffer[vbOffset + 1]
            if comp.size > 2 :
                vec.z = self.vertexBuffer[vbOffset + 2]
            if comp.size > 3 :
                vec.w = self.vertexBuffer[vbOffset + 3]
        return vec

#-------------------------------------------------------------------------------
class VertexKey :
    ''' 
    A key class for sorting vertices.
    '''
    def __init__(self, mesh, index) :
        self.index = index
        self.mesh  = mesh;

    def cmp(self, other) :

        selfSize = self.mesh.vertexLayout.size()
        otherSize = other.mesh.vertexLayout.size()
        if selfSize != otherSize :
            raise Exception('comparison meshes must be identical')
        selfIndex = self.index * selfSize
        otherIndex = other.index * otherSize
        for i in range(0, selfSize) :
            selfValue  = self.mesh.vertexBuffer[selfIndex + i]
            otherValue = other.mesh.vertexBuffer[otherIndex + i]
            if selfValue < otherValue :
                return -1
            elif selfValue > otherValue :
                return 1
        # fallthrough: vertices are identical
        return 0

    def __lt__(self, other) :
        return self.cmp(other) < 0
    def __gt__(self, other) :
        return self.cmp(other) > 0
    def __eq__(self, other) :
        return self.cmp(other) == 0
    def __le__(self, other) :
        return self.cmp(other) <= 0
    def __ge__(self, other) :
        return self.cmp(other) >= 0
    def __ne__(self, other) :
        return self.cmp(other) != 0

#-------------------------------------------------------------------------------
class VertexKeyMap :
    '''
    Holds a mesh reference and a list of (usually sorted) VertexKeys. Mainly
    used to find and remove duplicate vertices from a mesh
    '''
    def __init__(self, mesh=None) :
        self.mesh = mesh
        if mesh != None :
            self.keys = [VertexKey(mesh, i) for i in range(0, mesh.getNumVertices())]
        else :
            self.keys = None

    def sort(self) :
        '''
        Sort the contained vertex key
        '''
        self.keys = sorted(self.keys)

#--- eof

