import bpy
import bmesh
import math
import time
import random

# ********************************************************************
# X_Modulo_2D
# Blender version = 2.8 to 3.5
# Author = Patochun (Patrick M)
# Web Site = patochun.wordpress.com
# Mail = ptkmgr@gmail.com
#
# Licence used = Creative Commons CC BY
# Check licence here : https://creativecommons.org
#
# Generate Multiplication by Modulo version 2D
# Master variables :
#   Nb_Modulo     Modulo apply to multiplication
#   TableMulti    Multiplication table
#   (bpy.context.object.data.bevel_depth) line for choosing your bevel
# ********************************************************************

Nb_Modulo = 200
TableMulti = 2

# Create collection
def create_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection)
        return new_collection


# Create circle of points (vertices)
def circle(size, samples):
    points = []
    z = 0
    theta = math.radians(360)  # 2Pi
    alpha = theta / samples
    for a in range(0, samples, 1):
        angle = a * alpha
        x = size * math.cos(angle)
        y = size * math.sin(angle)
        points.append([x, y, z])
        rot = math.radians(270 + (a*(360/samples)))
    return points

# ------------------
# MAIN
# ------------------

# Create a new collection
newCol = create_collection("XModulo2D", bpy.context.scene.collection)

# Create vertices arround the circle
verts = circle(size=2, samples=Nb_Modulo)

tbedges = []
tbfaces = []

# Link vertices to create edges with multiplication table
for i in range(1, Nb_Modulo, 1):
    newedge = (i, (i*TableMulti) % Nb_Modulo)
    tbedges.append(newedge)

mesh = bpy.data.meshes.new("mesh_temp")
mesh.from_pydata(vertices=verts, edges=tbedges, faces=tbfaces)
mesh.update()

# create object from mesh
obj = bpy.data.objects.new("Multi_Modulo_2D", mesh)
scene = bpy.context.scene
newCol.objects.link(obj)


# convert to curve
# bevel
# convert back to mesh
bpy.ops.object.select_all(action='DESELECT')
view_layer = bpy.context.view_layer
obj.select_set(True)
view_layer.objects.active = obj
bpy.ops.object.convert(target='CURVE', keep_original=False)
bpy.context.object.data.dimensions = '3D'
bpy.context.object.data.bevel_depth = 0.005
bpy.context.object.data.bevel_resolution = 1  # 6 faces by segments
bpy.context.object.data.use_radius = False
bpy.context.object.data.twist_mode = 'Z_UP'
bpy.context.object.data.fill_mode = 'FULL'
bpy.ops.object.convert(target='MESH')

# End of script - Enjoy
