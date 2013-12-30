drahtgitter
===========

A python package for converting and processing 3d data.

This is one of several competing weekend projects, so don't expect quick progress ;)

Currently requires python 2.7.x

#### Overview

Drahtgitter aims to be a modular conversion and processing framework for 3D data written in python, with focus on getting data from 3D-DCC-tools into 3D-engines.

Modularity is achieved by separating the importing, processing and exporting steps:

- **Readers**: reader modules know how to load a specific input file format (for instance FBX) into a generic internal representation
- **Operators**: operators do some computation on the internal representation (for instance removing redundant vertices, computing normals, adding or removing vertex components, and so on)
- **Writers**: writer modules know how to convert the internal representation into a specific output file format (for instance a three.js JSON dump, or another 3D engine specific file format)

In general, a tool pipeline shouldn't put too many restrictions on the 3D artist. For instance the artist should only be concerned about overall vertex count and number of unique materials in the scene (since these affect rendering performance), but not about triangulation or the number of transform- or mesh-nodes in the scene (since these should be optimized by the tool pipeline)

#### Features 

Most of this is work-in-progress!!

- **extensibility:** it should be as simple as possible to add new reader-, operator- and writer-modules (some input file formats are complex beasts though (for instance FBX), so supporting new input file formats of this complexity level will never be a trivial task)
- **automatic triangulation:** geometry will be triangulated on-the-fly by the reader modules
- **geometry cleanup and optimization:** remove redundant vertices and degenerate triangles, sort vertices for better vertex-cache efficiency
- **compute missing vertex components:** if the input file doesn't provide normals, tangents or binormals, drahtgitter provides operators to compute them
- **flexible material parsing**: most modern 3D engines have a powerful shader-based material system without hardwired material parameters, drahtgitter supports this by providing hooks to customize the material importing process and material-"transformation" operators 
- *flexible vertex component system*: a vertex is "just a bunch of floats", split into vertex components, a vertex component has a name (e.g. 'position', 'normal', or 'texcoord'), a size (1..4 floats) and a stream index (normally used for multiple texture coordinate sets), some vertex components names have special meanings for readers, operators and writers (e.g. 'position'), but unknown components are preserved throughout the pipeline
- **vertex component packing**: modern 3D engines use packed vertex formats to save memory bandwidth (e.g. packing a normal as an UBYTE4N instead of
3 floats), drahtgitter supports this by providing helper functions to 
pack and unpack vertex components
- **per-material triangle groups:** an input 3D scene could be made of hundreds of mesh objects which have only a handful of materials assigned, drahtgitter will ignore the original mesh structure and group the triangles by their unique material index instead. This usually saves draw-calls in the 3D engine.
- **hierarchy node optimizaton:** just as with meshes, a DCC tool 3D scene could be made of hundreds of transform nodes (because it might be more convenient for the 3D artist to work this way), but none or very few of those transform nodes are actually needed at run-time in the 3D engine (a "static" 3D object doesn't need a transform node hierarchy at all, but imagine a tank where the gun turret and the wheels should be animated, the transform nodes which need to perform this animation must be preserved). Drahtgitter will preserve transform nodes which are flagged as dynamic (or have an animation attached), and drop all other transform nodes.

#### Usage
TODO

#### Running tests

Simply execute the test.py file in the root directory.

For the FBX tests (test_fbx.py) the Python FBX python SDK must be properly installed!


