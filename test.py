#!/usr/bin/env python
'''
    Test drahtgitter functionality.
'''

import unittest
import drahtgitter.core as dg

class TestMesh(unittest.TestCase) :

    def test_VertexComponent(self) :
        # create a few valid vertex component objects
        vc = dg.VertexComponent('position', 0, 3)
        self.assertEqual(vc.name, 'position')
        self.assertEqual(vc.index, 0)
        self.assertEqual(vc.size, 3)
        self.assertEqual(vc.offset, 0)

        vc = dg.VertexComponent('texcoord', 3, 2)
        self.assertEqual(vc.name, 'texcoord')
        self.assertEqual(vc.index, 3)
        self.assertEqual(vc.size, 2)
        self.assertEqual(vc.offset, 0)
        vc.validate()

        # vertex layout with invalid name
        vc = dg.VertexComponent('bla', 0, 1)
        self.assertRaises(Exception, vc.validate)

        # vertex layout with invalid offset
        vc = dg.VertexComponent('position', -1, 3)
        self.assertRaises(Exception, vc.validate)
        vc = dg.VertexComponent('position', 17, 3)
        self.assertRaises(Exception, vc.validate)

        # vertex layout with invalid size
        vc = dg.VertexComponent('position', 0, 0)
        self.assertRaises(Exception, vc.validate)
        vc = dg.VertexComponent('position', 5, 0)
        self.assertRaises(Exception, vc.validate)

    def test_VertexLayout(self) :
        # create an empty vertex layout object
        vl = dg.VertexLayout()
        self.assertEqual(vl.current_offset, 0)

        # add a few vertex components (position, normal and 2 texcoord sets)
        vl.add(dg.VertexComponent('position', 0, 3))
        vl.add(dg.VertexComponent('normal', 0, 3))
        vl.add(dg.VertexComponent('texcoord', 0, 2))
        vl.add(dg.VertexComponent('texcoord', 1, 2))
        self.assertEqual(vl.current_offset, 10)
        self.assertEqual(len(vl.vertexComponents), 4)
        self.assertTrue(vl.contains('position', 0))
        self.assertTrue(vl.contains('normal', 0))
        self.assertTrue(vl.contains('texcoord', 0))
        self.assertTrue(vl.contains('texcoord', 1))
        self.assertFalse(vl.contains('position', 1))
        self.assertFalse(vl.contains('bla', 0))
        self.assertEqual(vl.vertexComponents[('position', 0)].offset, 0)
        self.assertEqual(vl.vertexComponents[('normal', 0)].offset, 3)
        self.assertEqual(vl.vertexComponents[('texcoord', 0)].offset, 6)
        self.assertEqual(vl.vertexComponents[('texcoord', 1)].offset, 8)
        vl.validate()

if __name__ == '__main__':
    unittest.main()
#--- eof

