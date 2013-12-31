#!/usr/bin/env python
'''
    Test drahtgitter functionality.
'''

import unittest
from drahtgitter.core import *
import drahtgitter.generators.cube as cube
import drahtgitter.generators.cylinder as cylinder
import drahtgitter.generators.sphere as sphere
import drahtgitter.generators.torus as torus
import drahtgitter.operators.computeTriangleNormals as computeTriangleNormals
import drahtgitter.operators.fixVertexComponents as fixVertexComponents
import drahtgitter.operators.deflate as deflate
import drahtgitter.writers.stlasciiwriter as stlasciiwriter
import drahtgitter.writers.threejswriter as threejswriter

class TestMath(unittest.TestCase) :

    def test_Vector(self) :

        v0 = Vector()
        v1 = Vector(1.0)
        v2 = Vector(1.0, 2.0)
        v3 = Vector(1.0, 2.0, 3.0)
        v4 = Vector(1.0, 2.0, 3.0, 4.0)
        self.assertTrue(v0.x == 0.0 and v0.y == 0.0 and v0.z == 0.0 and v0.w == 0.0)
        self.assertTrue(v1.x == 1.0 and v1.y == 0.0 and v1.z == 0.0 and v1.w == 0.0)
        self.assertTrue(v2.x == 1.0 and v2.y == 2.0 and v2.z == 0.0 and v2.w == 0.0)
        self.assertTrue(v3.x == 1.0 and v3.y == 2.0 and v3.z == 3.0 and v3.w == 0.0)
        self.assertTrue(v4.x == 1.0 and v4.y == 2.0 and v4.z == 3.0 and v4.w == 4.0)

        v0 = Vector(1.0, 2.0, 3.0, 4.0)
        v1 = Vector(1.0, 2.0, 3.0, 4.0)
        v2 = Vector(2.0, 3.0, 4.0, 5.0)
        v3 = Vector(1.0, 2.0, 1.0, 4.0)
        self.assertTrue(v0 == v1)
        self.assertTrue(v0 != v2)
        self.assertTrue(v0 != v3)

        v4 = v0 + v2
        self.assertTrue(v4 == Vector(3.0, 5.0, 7.0, 9.0))
        v5 = v4 - v2
        self.assertTrue(v5 == v0)
        v6 = v2 * v3
        self.assertTrue(v6 == Vector(2.0, 6.0, 4.0, 20.0))
        v7 = Vector.scale(v2, 3.0)
        self.assertTrue(v7 == Vector(6.0, 9.0, 12.0, 15.0))
        self.assertEqual(Vector.length(Vector(3.0, 4.0, 0.0, 0.0)), 5.0)
        self.assertEqual(Vector.cross3(Vector(1.0, 0.0, 0.0), Vector(0.0, 1.0, 0.0)), Vector(0.0, 0.0, 1.0))
        v0 = Vector(1.0, 0.0, 0.0)
        v1 = Vector(1.0, 0.0, 0.0)
        v2 = Vector(0.0, 1.0, 0.0)
        v3 = Vector(-1.0, 0.0, 0.0)
        self.assertEqual(Vector.dot3(v0, v1), 1.0)
        self.assertEqual(Vector.dot3(v0, v2), 0.0)
        self.assertEqual(Vector.dot3(v0, v3), -1.0)
        self.assertTrue(abs(Vector.length(Vector.normalize(Vector(1.0, 2.0, 3.0, 4.0))) - 1.0) < 0.00001)

pos0 = ('position', 0)
norm0 = ('normal', 0)
tex0 = ('texcoord', 0)

class TestMesh(unittest.TestCase) :

    def _buildVertexLayout(self) :
        vl = VertexLayout()
        vl.add(VertexComponent(pos0, 3))
        vl.add(VertexComponent(norm0, 3))
        vl.add(VertexComponent(tex0, 2))
        return vl        

    def test_VertexComponent(self) :
        # create a few valid vertex component objects
        vc = VertexComponent(('position', 0), 3)
        self.assertEqual(vc.nameAndIndex[0], 'position')
        self.assertEqual(vc.nameAndIndex[1], 0)
        self.assertEqual(vc.size, 3)
        self.assertEqual(vc.offset, 0)

        vc = VertexComponent(('texcoord', 3), 2)
        self.assertEqual(vc.nameAndIndex[0], 'texcoord')
        self.assertEqual(vc.nameAndIndex[1], 3)
        self.assertEqual(vc.size, 2)
        self.assertEqual(vc.offset, 0)
        vc.validate()

        # vertex layout with invalid offset
        vc = VertexComponent(('position', -1), 3)
        self.assertRaises(Exception, vc.validate)
        vc = VertexComponent(('position', 17), 3)
        self.assertRaises(Exception, vc.validate)

        # vertex layout with invalid size
        vc = VertexComponent(('position', 0), 0)
        self.assertRaises(Exception, vc.validate)
        vc = VertexComponent(('position', 5), 0)
        self.assertRaises(Exception, vc.validate)

    def test_VertexLayout(self) :
        # create an empty vertex layout object
        vl = VertexLayout()
        self.assertEqual(vl.size, 0)

        # add a few vertex components (position, normal and 2 texcoord sets)
        pos0 = ('position', 0)
        norm0 = ('normal', 0)
        tex0 = ('texcoord', 0)
        tex1 = ('texcoord', 1)
        vl.add(VertexComponent(pos0, 3))
        vl.add(VertexComponent(norm0, 3))
        vl.add(VertexComponent(tex0, 2))
        vl.add(VertexComponent(tex1, 2))

        self.assertEqual(vl.size, 10)
        self.assertEqual(len(vl.vertexComponents), 4)

        self.assertTrue(vl.contains(pos0))
        self.assertTrue(vl.contains(norm0))
        self.assertTrue(vl.contains(tex0))
        self.assertTrue(vl.contains(tex1))
        self.assertFalse(vl.contains( ('position', 1) ))
        self.assertFalse(vl.contains( ('bla', 0) ))

        self.assertEqual(vl.vertexComponents[pos0].offset, 0)
        self.assertEqual(vl.vertexComponents[norm0].offset, 3)
        self.assertEqual(vl.vertexComponents[tex0].offset, 6)
        self.assertEqual(vl.vertexComponents[tex1].offset, 8)
        vl.validate()

        self.assertEqual(vl.getComponent(pos0).nameAndIndex[0], 'position')
        self.assertEqual(vl.getComponent(pos0).nameAndIndex[1], 0)

        self.assertEqual(vl.size, 10)

    def test_Mesh(self) :

        # create mesh with a simple vertex layout 
        vl = self._buildVertexLayout()
        mesh = Mesh(vl, 3)

        self.assertEqual(mesh.getComponent(pos0).nameAndIndex[0], 'position')
        self.assertEqual(mesh.getComponent(pos0).nameAndIndex[1], 0)
        self.assertEqual(mesh.getComponent(norm0).offset, 3)
        self.assertEqual(mesh.getComponent(tex0).size, 2)

        self.assertEqual(mesh.getComponentOffset(norm0), 3)
        self.assertEqual(mesh.getComponentSize(norm0), 3)

        # add 3 vertices
        mesh.setVertex(0, pos0, Vector(1.0, 2.0, 3.0))
        mesh.setVertex(0, norm0,  Vector(1.0, 0.0, 0.0))
        mesh.setVertex(0, tex0, Vector(0.0, 0.0))

        mesh.setVertex(1, pos0, Vector(2.0, 3.0, 4.0))
        mesh.setVertex(1, norm0, Vector(0.0, 1.0, 0.0))
        mesh.setVertex(1, tex0, Vector(1.0, 0.0))

        mesh.setVertex(2, pos0, Vector(3.0, 4.0, 5.0))
        mesh.setVertex(2, norm0, Vector(0.0, 0.0, 1.0))
        mesh.setVertex(2, tex0, Vector(1.0, 1.0))

        self.assertEqual(mesh.getVertex(0, pos0), Vector(1.0, 2.0, 3.0))
        self.assertEqual(mesh.getVertex(1, pos0), Vector(2.0, 3.0, 4.0))
        self.assertEqual(mesh.getVertex(2, pos0), Vector(3.0, 4.0, 5.0))

        self.assertEqual(mesh.getVertex(0, norm0), Vector(1.0, 0.0, 0.0))
        self.assertEqual(mesh.getVertex(1, norm0), Vector(0.0, 1.0, 0.0))
        self.assertEqual(mesh.getVertex(2, norm0), Vector(0.0, 0.0, 1.0))

        self.assertEqual(mesh.getVertex(0, tex0), Vector(0.0, 0.0))
        self.assertEqual(mesh.getVertex(1, tex0), Vector(1.0, 0.0))
        self.assertEqual(mesh.getVertex(2, tex0), Vector(1.0, 1.0))

        self.assertEqual(mesh.vertexBuffer[0], 1.0)
        self.assertEqual(mesh.vertexBuffer[1], 2.0)
        self.assertEqual(mesh.vertexBuffer[2], 3.0)
        self.assertEqual(mesh.vertexBuffer[3], 1.0)
        self.assertEqual(mesh.vertexBuffer[4], 0.0)
        self.assertEqual(mesh.vertexBuffer[5], 0.0)
        self.assertEqual(mesh.vertexBuffer[6], 0.0)
        self.assertEqual(mesh.vertexBuffer[7], 0.0)

        self.assertEqual(mesh.vertexBuffer[8], 2.0)
        self.assertEqual(mesh.vertexBuffer[9], 3.0)
        self.assertEqual(mesh.vertexBuffer[10], 4.0)
        self.assertEqual(mesh.vertexBuffer[11], 0.0)
        self.assertEqual(mesh.vertexBuffer[12], 1.0)
        self.assertEqual(mesh.vertexBuffer[13], 0.0)
        self.assertEqual(mesh.vertexBuffer[14], 1.0)
        self.assertEqual(mesh.vertexBuffer[15], 0.0)

        self.assertEqual(mesh.vertexBuffer[16], 3.0)
        self.assertEqual(mesh.vertexBuffer[17], 4.0)
        self.assertEqual(mesh.vertexBuffer[18], 5.0)
        self.assertEqual(mesh.vertexBuffer[19], 0.0)
        self.assertEqual(mesh.vertexBuffer[20], 0.0)
        self.assertEqual(mesh.vertexBuffer[21], 1.0)
        self.assertEqual(mesh.vertexBuffer[22], 1.0)
        self.assertEqual(mesh.vertexBuffer[23], 1.0)

        self.assertRaises(IndexError, lambda: mesh.vertexBuffer[24])
        self.assertRaises(IndexError, mesh.getVertex, 3, pos0);

    def test_CubeGenerator(self) :

        vl = self._buildVertexLayout()
        model = cube.generate(vl, Vector(2.0, 2.0, 2.0))
        self.assertEqual(model.mesh.getNumVertices(), 24)
        self.assertEqual(model.mesh.getNumTriangles(), 12)
        model = computeTriangleNormals.do(model)
        
        self.assertEqual(model.mesh.triangles[0].getNormal(), model.mesh.triangles[1].getNormal())
        self.assertEqual(model.mesh.triangles[2].getNormal(), model.mesh.triangles[3].getNormal())
        self.assertEqual(model.mesh.triangles[4].getNormal(), model.mesh.triangles[5].getNormal())
        self.assertEqual(model.mesh.triangles[6].getNormal(), model.mesh.triangles[7].getNormal())
        self.assertEqual(model.mesh.triangles[8].getNormal(), model.mesh.triangles[9].getNormal())
        self.assertEqual(model.mesh.triangles[10].getNormal(), model.mesh.triangles[11].getNormal())

        self.assertEqual(model.mesh.triangles[0].getNormal(), model.mesh.getVertex(0, norm0))
        self.assertEqual(model.mesh.triangles[2].getNormal(), model.mesh.getVertex(4, norm0))
        self.assertEqual(model.mesh.triangles[4].getNormal(), model.mesh.getVertex(8, norm0))
        self.assertEqual(model.mesh.triangles[6].getNormal(), model.mesh.getVertex(12, norm0))
        self.assertEqual(model.mesh.triangles[8].getNormal(), model.mesh.getVertex(16, norm0))
        self.assertEqual(model.mesh.triangles[10].getNormal(), model.mesh.getVertex(20, norm0))

        stlasciiwriter.write(model, 'data/cube.ascii.stl')
        threejswriter.write(model, 'data/cube.model.js', 50.0)

    def test_CylinderGenerator(self) :

        vl = self._buildVertexLayout()
        model = cylinder.generate(vl, 1.0, 1.0, 4.0, 36, 1)
        model = computeTriangleNormals.do(model)
        stlasciiwriter.write(model, 'data/cylinder.ascii.stl')
        threejswriter.write(model, 'data/cylinder.model.js', 50.0)

        model = cylinder.generate(vl, 2.0, 0.5, 4.0, 18, 4)
        model = computeTriangleNormals.do(model)
        stlasciiwriter.write(model, 'data/complex_cylinder.ascii.stl')
        threejswriter.write(model, 'data/complex_cylinder.model.js', 50.0)

    def test_SphereGenerator(self) :

        vl = self._buildVertexLayout()
        model = sphere.generate(vl, 2.0, 38, 18)
        model = computeTriangleNormals.do(model)
        stlasciiwriter.write(model, 'data/sphere.ascii.stl')
        threejswriter.write(model, 'data/sphere.model.js', 50.0)

    def test_TorusGenerator(self) :

        vl = self._buildVertexLayout()
        model = torus.generate(vl, 1.0, 3.0, 18, 36)
        model = computeTriangleNormals.do(model)
        stlasciiwriter.write(model, 'data/torus.ascii.stl')
        threejswriter.write(model, 'data/torus.model.js', 100.0)

    def test_Deflate(self) :

        # generate a cube
        vl = self._buildVertexLayout()
        model = cube.generate(vl, Vector(2.0, 2.0, 2.0))
        model = computeTriangleNormals.do(model)

        # reduce to only positions
        reducedVl = VertexLayout()
        reducedVl.add(VertexComponent(pos0, 3))
        fixedModel = fixVertexComponents.do(model, reducedVl)
        self.assertTrue(fixedModel.mesh.vertexLayout.contains(pos0))
        self.assertFalse(fixedModel.mesh.vertexLayout.contains(norm0))
        self.assertFalse(fixedModel.mesh.vertexLayout.contains(tex0))

        # remove duplicate vertices
        reducedModel, indexMap = deflate.do(fixedModel)

        self.assertEqual(len(indexMap), 24)
        self.assertEqual(reducedModel.mesh.getNumVertices(), 8)

        stlasciiwriter.write(reducedModel, 'data/cube_reduced.ascii.stl')
        threejswriter.write(reducedModel, 'data/cube_reduced.model.js', 50.0)

if __name__ == '__main__':
    unittest.main()
#--- eof
