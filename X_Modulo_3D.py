import bpy
import math
import time
import random

# ********************************************************************
# X_Modulo_3D
# Blender version = 2.8
# Author = Doc OuatZat (DOZ) and by the way is creator (Patrick M)
# Web Site = docouatzat.com
# Mail = docouatzat@gmail.com
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


# Create collection
def create_collection(collection_name, parent_collection):
    if collection_name in bpy.data.collections:
        return bpy.data.collections[collection_name]
    else:
        new_collection = bpy.data.collections.new(collection_name)
        parent_collection.children.link(new_collection)
        return new_collection


# Create vertices on sphere surface
def Points_Sphere(samples, randomizer):
    rnd = 1.0
    random.seed(randomizer)
    rnd = random.random() * samples
    points = []
    offset = 2.0 / samples
    inc = math.pi * (3. - math.sqrt(5.))
    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2)
        phi = ((i + rnd) % samples) * inc
        r = math.sqrt(1 - pow(y, 2))
        x = math.cos(phi) * r
        z = math.sin(phi) * r
        points.append([x, y, z])
    return points

# ------------------
# MAIN
# ------------------

# Create a new collection
newCol = create_collection("XModulo2D", bpy.context.scene.collection)

Nb_Modulo = 1000
TableMulti = 2

verts = Points_Sphere(Nb_Modulo, randomizer=20)

mesh = bpy.data.meshes.new("mesh_temp")
mesh.from_pydata(vertices=verts, edges=[], faces=[])
mesh.update()

# Generate Edges
for i in range(1, Nb_Modulo, 1):
    mesh.edges.add(i)
    edge = mesh.edges[-1]
    edge.vertices = (i, (i * TableMulti) % Nb_Modulo)

mesh.update()

# Create object from mesh
obj = bpy.data.objects.new("Multi_Modulo_3D", mesh)
scene = bpy.context.scene
newCol.objects.link(obj)

# Convert to curve
# Bevel
# Convert back to mesh
bpy.ops.object.select_all(action='DESELECT')
view_layer = bpy.context.view_layer
obj.select_set(True)
view_layer.objects.active = obj
bpy.ops.object.convert(target='CURVE', keep_original=False)
bpy.context.object.data.bevel_depth = 0.002
bpy.context.object.data.twist_mode = 'Z_UP'
bpy.context.object.data.fill_mode = 'FULL'
bpy.ops.object.convert(target='MESH')

# End of script - Enjoy
