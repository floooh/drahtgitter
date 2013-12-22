'''
Defines the drahtgitter core classes like Mesh, Material, Bone, ...
'''

from array import array

#-------------------------------------------------------------------------------
class VertexComponent :
    '''
    A single entry in a VertexLayout, describes one vertex component
    '''
    def __init__(self, name, index, size) :
        '''
        NOTE: The index is the "stream index", for instance the
        first set of uv coords would have an index=0, the second index=1.
        The offset is the offset of the float data in a vertex (0 is start of
        vertex), size if the number of floats in the vertex (must be between 1 and 4)
        '''
        self.validNames = ('position', 'texcoord', 'normal', 'tangent', 'binormal', 'color', 'weights', 'indices', 'custom')
        self.name   = name
        self.index  = index
        self.offset = 0
        self.size   = size

    def validate(self) :
        if not self.name in self.validNames :
            raise Exception('Invalid vertex component name: ' + self.name)
        if self.index < 0 or self.index > 8 :
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
        self.current_offset = 0
        self.vertexComponents = dict()

    def contains(self, name, index) :
        ''' 
        Test if a component with name and stream index already exists
        '''
        return (name, index) in self.vertexComponents

    def add(self, comp) :
        '''
        Add a vertex component definition to the vertex layout
        '''
        comp.validate()
        if not isinstance(comp, VertexComponent) :
            raise TypeError('Component must be of class VertexComponent!')
        if self.contains(comp.name, comp.index) :
            raise Exception('Component already exists!')
        comp.offset = self.current_offset
        self.current_offset += comp.size
        self.vertexComponents[(comp.name,comp.index)] = comp;

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
        if not size == self.current_offset :
            raise Exception("Vertex component sizes don't add up")

#-------------------------------------------------------------------------------
class Mesh :
    '''
    Holds everything for describing geometry.
    '''
    def __init__(self) :
        self.vertexBuffer = array('f')
        self.vertexLayout = VertexLayout()
        self.triangles    = []

#--- eof

