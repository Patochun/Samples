import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
import numpy as np
import math
import random

# ********************************************************************
# Sieve_of_Erathostene
# Blender version = 2.8
# Author = Doc OuatZat (DOZ) and by the way is creator (Patrick M)
# Web Site = docouatzat.com
# Mail = docouatzat@gmail.com
#
# Licence used = Creative Commons CC BY
# Check licence here : https://creativecommons.org
#
# Generate animation of Sieve of Erathostene
# Master variables :
#   BigCubeEdge = Mean the number of cubes by edge of the big cube.
#                 4 is the default value. Feel free to choose yours.
#                 but keep in mind the consumed ressource and time.
# ********************************************************************

BigCubeEdge = 4
CubesCount = BigCubeEdge ** 3
ArrayOfCube = np.zeros((CubesCount + 2), dtype=int)


# Research about a collection
def find_collection(context, item):
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection


# Create collection
def create_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection)
        return new_collection


# Create a text mesh
def Add_Text(collect, Name, x, y, z, Texte, mat1, mat2, mat3):
    bpy.ops.object.text_add()
    ot = bpy.context.active_object
    ot.name = 't_' + Name
    ot.data.body = Texte
    ot.data.extrude = 0.1
    ot.location.x = (x * 2.5) - (len(Texte)/4)
    ot.location.y = (y * 2.5) - 0.4
    ot.location.z = (z * 2.5) + 1.0

    o = bpy.context.object
    bpy.ops.object.convert(target='MESH', keep_original=False)

    # assign to material slots - Both cube and text for union later
    o.data.materials.append(mat1)
    o.data.materials.append(mat2)
    o.data.materials.append(mat3)

    collect_to_unlink = find_collection(bpy.context, o)
    collect.objects.link(o)
    collect_to_unlink.objects.unlink(o)

    return ot


# Create a Cube Mesh
def Add_Cube(collect, Name, x, y, z, mat1, mat2, mat3):
    bpy.ops.mesh.primitive_cube_add()
    oc = bpy.context.active_object
    oc.name = 'c_' + Name
    oc.location.x = x * 2.5
    oc.location.y = y * 2.5
    oc.location.z = z * 2.5

    o = bpy.context.object

    # assign to material slots - Both cube and text for union later
    o.data.materials.append(mat1)
    o.data.materials.append(mat2)
    o.data.materials.append(mat3)

    # Little bevel is always a nice idea for a cube
    bpy.ops.object.modifier_add(type="BEVEL")
    bpy.ops.object.modifier_apply(modifier="BEVEL")

    collect_to_unlink = find_collection(bpy.context, o)
    collect.objects.link(o)
    collect_to_unlink.objects.unlink(o)

    return oc


# Boolean operation between two objects
# Type =  [INTERSECT, UNION, DIFFERENCE]
def applyBoolean(obj_A, obj_B, Type):
    boo = obj_A.modifiers.new(type='BOOLEAN', name="booh")
    boo.object = obj_B
    boo.operation = Type
    bpy.ops.object.modifier_apply(modifier="booh")
    bpy.ops.object.select_all(action='DESELECT')
    bpy.data.objects[obj_B.name].select_set(True)
    bpy.ops.object.delete()


# ------------------
# Change cube scale
# ------------------
def EditScale(scn, n, sc):
    Obj_Name = 'c_' + str(n)
    obj = bpy.data.objects[Obj_Name]
    a = scn.frame_current
    obj.keyframe_insert('scale')
    scn.frame_current += 10
    obj.scale = sc, sc, sc
    obj.keyframe_insert('scale')
    scn.frame_current = a


# ------------------
# Highlight cube text
# ------------------
def Highlight_Cube(scn, n):
    Obj_Name = 'c_' + str(n)
    obj = bpy.data.objects[Obj_Name]

    a = scn.frame_current
    # Mem state at pos-1 to avoid changing in middle latter
    scn.frame_current -= 1
    mesh = obj.data
    for f in mesh.polygons:  # iterate over faces
        f.keyframe_insert('material_index')

    # Change lighting of text by changing material_index
    scn.frame_current += 1
    for f in mesh.polygons:  # iterate over faces
        if (f.material_index == 2):
            f.material_index = 1
            f.keyframe_insert('material_index')
    scn.frame_current = a

# ------------------
# MAIN
# ------------------

bpy.ops.transform.translate(value=(1, 1, 1))

# Create a new collection
nCol = create_collection("Big_Cube", bpy.context.scene.collection)

# Create materials for cubes
# Cube body
mat_c = bpy.data.materials.new(name="Material_Cube")
mat_c.use_nodes = True
principled = PrincipledBSDFWrapper(mat_c, is_readonly=False)
principled.base_color = (0.8, 0.4, 0.2)

# Highlight Text
mat_ch = bpy.data.materials.new(name="Material_Highlight")
mat_ch.use_nodes = True
principled = PrincipledBSDFWrapper(mat_ch, is_readonly=False)
principled.base_color = (0.4, 1.0, 0.2)

# Normal Text
mat_t = bpy.data.materials.new(name="Material_Highlight")
mat_t.use_nodes = True
principled = PrincipledBSDFWrapper(mat_t, is_readonly=False)
principled.base_color = (1.0, 0.0, 0.0)

# Create the 3D array of cube
k = 0
for z in range(BigCubeEdge, 0, -1):
    for y in range(BigCubeEdge, 0, -1):
        for x in range(0, BigCubeEdge):
            k += 1
            ot = Add_Text(nCol, str(k), x, y, z, str(k), mat_t, mat_c, mat_ch)
            oc = Add_Cube(nCol, str(k), x, y, z, mat_c, mat_ch, mat_t)
            applyBoolean(oc, ot, "UNION")

# Set animation start
scn = bpy.context.scene
scn.frame_current = 1

# Freeze all objects in start state
for num in range(1, CubesCount):
    Obj_Name = 'c_' + str(num)
    obj = bpy.data.objects[Obj_Name]
    obj.scale = 1.0, 1.0, 1.0
    obj.keyframe_insert('scale')

# Leave 4 second before start
    scn.frame_current = 100

# Freeze all objects in start state (again)
for num in range(1, CubesCount):
    Obj_Name = 'c_' + str(num)
    obj = bpy.data.objects[Obj_Name]
    obj.scale = 1.0, 1.0, 1.0
    obj.keyframe_insert('scale')

# Play the Sieve of Erathostene
ArrayOfCube.fill(1)
ArrayOfCube[0] = 0  # Do not use the 0
ArrayOfCube[CubesCount+1] = 0  # Mark the last+1

# Main loop of Sieve
for i in range(1, CubesCount, 1):

    # Do not treat the one
    if (i == 1):
        ArrayOfCube[i] = 0
        EditScale(scn, i, 0.0)
        continue

    # Do not treat if already treated
    if (ArrayOfCube[i] == 0):
        continue

    # Highlight running number
    scn.frame_current += 2
    Highlight_Cube(scn, i)
    EditScale(scn, i, 2.0)

    # Sieve all N since 2xN
    for j in range(i*2, CubesCount+1, i):
        # Do not treat if already treated (also here)
        if (ArrayOfCube[j] == 0):
            continue
        ArrayOfCube[j] = 0
        scn.frame_current += 2
        EditScale(scn, j, 0.0)

    # Downlight running number
    scn.frame_current += 2
    EditScale(scn, i, 1.0)

# Leave 4 seconds after Sieve
scn.frame_end = scn.frame_current + 100

# Return to frame 1
scn.frame_current = 1

# End of script - Enjoy
