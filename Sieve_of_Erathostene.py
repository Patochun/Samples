import bpy
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper
import numpy as np

# ********************************************************************
# Sieve_of_Erathostene
# Blender version = 2.8 to 4.2
# Author = Patochun (Patrick M)
# YT : https://www.youtube.com/channel/UCCNXecgdUbUChEyvW3gFWvw
# Mail = ptkmgr@gmail.com
#
# Licence used = Creative Commons CC BY
# Check licence here : https://creativecommons.org
#
# Generate animation of Sieve of Erathostene
# Master variables :
#   bigCubeEdge = Mean the number of cubes by edge of the big cube.
#                 5 is the default value. Feel free to choose yours.
#                 but keep in mind the consumed ressource and time.
#
# Notes : The frame rate chosen for the animation is 25 frames per second.
# ********************************************************************

bigCubeEdge = 5
cubesCount = bigCubeEdge ** 3
arrayOfCube = np.zeros((cubesCount + 2), dtype=int)


# Research about a collection
def find_collection(context, item):
    collections = item.users_collection
    if len(collections) > 0:
        return collections[0]
    return context.scene.collection


# Create collection
def create_collection(collection_name, parent_collection):
    # delete if exist
    if collection_name in bpy.data.collections:
        collection = bpy.data.collections[collection_name]
        for ob in collection.objects:
            bpy.data.objects.remove(ob, do_unlink=True)
        bpy.data.collections.remove(collection)
    # create a new one
    new_collection = bpy.data.collections.new(collection_name)
    parent_collection.children.link(new_collection)
    return new_collection


# Create a text mesh
def add_text(collect, name, mat1, mat2):
    bpy.ops.object.text_add()
    ot = bpy.context.active_object
    ot.name = 't_' + name
    ot.data.body = name
    ot.data.extrude = 0.1
    ot.location.x = -(len(name)/4)
    ot.location.y = -0.4
    ot.location.z = 1.0

    o = bpy.context.object
    bpy.ops.object.convert(target='MESH', keep_original=False)

    # assign to material slots - Both cube and text for union later
    o.data.materials.append(mat1) # index 0
    o.data.materials.append(mat2) # index 1

    collect_to_unlink = find_collection(bpy.context, o)
    collect.objects.link(o)
    collect_to_unlink.objects.unlink(o)

    return ot


# Create a Cube Mesh
def add_cube(collect, name, x, y, z, mat1):
    bpy.ops.mesh.primitive_cube_add()
    oc = bpy.context.active_object
    oc.name = 'c_' + name
    oc.location.x = x * 2.5
    oc.location.y = y * 2.5
    oc.location.z = z * 2.5

    o = bpy.context.object

    # assign to material slots - Both cube and text for union later
    o.data.materials.append(mat1)

    # Little bevel is always a nice idea for a cube
    bpy.ops.object.modifier_add(type="BEVEL")
    bpy.ops.object.modifier_apply(modifier="BEVEL")

    collect_to_unlink = find_collection(bpy.context, o)
    collect.objects.link(o)
    collect_to_unlink.objects.unlink(o)

    return oc

# ------------------
# Change cube scale
# ------------------
def edit_scale(scn, n, sc):
    objName = 'c_' + str(n)
    obj = bpy.data.objects[objName]
    a = scn.frame_current
    obj.keyframe_insert('scale')
    scn.frame_current += 10
    obj.scale = sc, sc, sc
    obj.keyframe_insert('scale')
    scn.frame_current = a


# ------------------
# Highlight cube text
# ------------------
def highlight_cube(scn, n):
    objName = 't_' + str(n)
    obj = bpy.data.objects[objName]

    a = scn.frame_current
    # Mem state at pos-1 to avoid changing in middle latter
    scn.frame_current -= 1
    mesh = obj.data
    for f in mesh.polygons:  # iterate over faces
        f.keyframe_insert('material_index')

    # Change lighting of text by changing material_index
    scn.frame_current += 1
    for f in mesh.polygons:  # iterate over faces
        if (f.material_index == 0):
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
matCube = bpy.data.materials.new(name="matCube")
matCube.use_nodes = True
principled = PrincipledBSDFWrapper(matCube, is_readonly=False)
principled.base_color = (0.8, 0.4, 0.2)

# Highlight Text
matTextHighLight = bpy.data.materials.new(name="matTextHighlight")
matTextHighLight.use_nodes = True
principled = PrincipledBSDFWrapper(matTextHighLight, is_readonly=False)
principled.base_color = (0.4, 1.0, 0.2)

# Normal Text
matTextNormal = bpy.data.materials.new(name="matTextNormal")
matTextNormal.use_nodes = True
principled = PrincipledBSDFWrapper(matTextNormal, is_readonly=False)
principled.base_color = (1.0, 0.0, 0.0)

# Create the 3D array of cube
k = 0
for z in range(bigCubeEdge, 0, -1):
    for y in range(bigCubeEdge, 0, -1):
        for x in range(0, bigCubeEdge):
            k += 1
            kString = str(k)
            ot = add_text(nCol, kString, matTextNormal, matTextHighLight)
            oc = add_cube(nCol, kString, x, y, z, matCube)
            ot.parent = oc

# Set animation start
scn = bpy.context.scene
scn.frame_current = 1

# Freeze all objects in start state
for num in range(1, cubesCount):
    objName = 'c_' + str(num)
    obj = bpy.data.objects[objName]
    obj.scale = 1.0, 1.0, 1.0
    obj.keyframe_insert('scale')

# Leave 4 second before start
    scn.frame_current = 100

# Freeze all objects in start state (again)
for num in range(1, cubesCount):
    objName = 'c_' + str(num)
    obj = bpy.data.objects[objName]
    obj.scale = 1.0, 1.0, 1.0
    obj.keyframe_insert('scale')

# Play the Sieve of Erathostene
arrayOfCube.fill(1)
arrayOfCube[0] = 0  # Do not use the 0
arrayOfCube[cubesCount+1] = 0  # Mark the last+1

# Main loop of Sieve
for i in range(1, cubesCount, 1):

    # Do not treat the one
    if (i == 1):
        arrayOfCube[i] = 0
        edit_scale(scn, i, 0.0)
        continue

    # Do not treat if already treated
    if (arrayOfCube[i] == 0):
        continue

    # Highlight running number
    scn.frame_current += 2
    highlight_cube(scn, i)
    edit_scale(scn, i, 2.0)

    # Sieve all N since 2xN
    for j in range(i*2, cubesCount+1, i):
        # Do not treat if already treated (also here)
        if (arrayOfCube[j] == 0):
            continue
        arrayOfCube[j] = 0
        scn.frame_current += 2
        edit_scale(scn, j, 0.0)

    # Downlight running number
    scn.frame_current += 2
    edit_scale(scn, i, 1.0)

# Leave 4 seconds after Sieve
scn.frame_end = scn.frame_current + 100

# Return to frame 1
scn.frame_current = 1

# End of script - Enjoy
