import bpy
import numpy as np
import math
import random

# ********************************************************************
# Traffic Jam Simulator
# Blender version = 2.8 to 3.5
# Author = Patochun (Patrick M)
# Web Site = patochun.wordpress.com
# Mail = ptkmgr@gmail.com
#
# Licence used = Creative Commons CC BY
# Check licence here : https://creativecommons.org
#
# Master variables :
#   SegCount = Mean the number of segments, one segment must be empty
#              or containing a car
#   LaneCount = Mean the number of Lane. This code is designed for 1 lane only
#   CarCount = Mean the number of cars
# ********************************************************************

# Design the Road
# The segment represent place to put one car (SizeCarX) or nothing
SegCount = 500
LaneCount = 1  # Must be a pure divider of SegCount
Road_Segments = np.zeros(((LaneCount + 1), (SegCount + 1)), dtype=int)

# Coef (divide by) for interpolate the road to screen
# Cars touching
CoefBlender = SegCount / 50

# Design the car
# 5 meters / 2,5 meters (x,y)
# You can use everything you want
obj_Model_Name = 'Car_Model'
SizeCarX = 5  # mean also the size of one segment
SizeCarY = 2.5
SizeOfRoad = SegCount * SizeCarX
# transform speed in km/h into segment unit in second
CoefSpeed = 1 / 3600 * 1000 / SizeCarX

# in Km/h
SpeedWish = 130

# Material Index StopLight
Mat_Idx_SL_Off = 1
Mat_Idx_SL_On = 5

CarCount = 32
# I know, I can use multidimmensionnal array but I won't
Car_Pos = np.zeros(((CarCount + 1), 3), dtype=int)  # 1 - lane, 2 - segment
Car_Rot = np.zeros((CarCount + 1), dtype=int)  # For managing rotations
Car_Speed = np.zeros((CarCount + 1), dtype=int)  # Speed in Km/h


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


# Assign object to collection
def assign_to_collection(collect, ob):
    # Find actual collection to remove object for
    collect_to_unlink = find_collection(bpy.context, ob)
    # Assign object into collection
    collect.objects.link(ob)


# Initial State
# Create the number of cars choosing (by duplicating the car model)
# And place them belong the lanes of the road
def initial_state(collect):
    # Design the road

    # Dispatch cars on the road
    # For sample here we use the dispatch fair
    # Same amount of car by lane

    # Init the road
    for lane in range(1, LaneCount + 1):
        for segment in range(1, SegCount + 1):
            Road_Segments[lane, segment] = 0

    # Init car on the road
    CarCountByLane = (CarCount + 1) / LaneCount
    CarSpaceByLane = (SegCount + 1) / CarCountByLane
    TotalSegment = LaneCount * SegCount
    for car in range(1, CarCount + 1):
        lane = round((CarSpaceByLane * car)) // SegCount + 1
        segment = round((CarSpaceByLane * car)) % SegCount
        Road_Segments[lane, segment] = car
        Car_Pos[car, 1] = lane
        Car_Pos[car, 2] = segment

    # Design all cars
    for car in range(1, CarCount + 1):
        # Reproduce Model
        obj_Name = 'Car_' + str(car)
        ob = bpy.data.objects[obj_Model_Name]
        new_ob = bpy.data.objects.new(obj_Model_Name, ob.data.copy())
        assign_to_collection(collect, new_ob)
        new_ob.name = obj_Name
        new_ob.scale = 2.0, 2.0, 2.0
        if car == 10:
            mesh = new_ob.data
            for f in mesh.polygons:  # iterate over faces
                if f.material_index == 2:
                    f.material_index = 6
                    f.keyframe_insert('material_index')


# Redraw all car at their respectives positions
def redraw_car(scn):
    z = 1.2
    rx = math.radians(90)
    ry = 0
    theta = math.radians(360)  # 2Pi
    alpha = theta / SegCount
    for car in range(1, CarCount + 1):
        obj_Name = 'Car_' + str(car)
        ob = bpy.data.objects[obj_Name]

        # Place it
        lane = Car_Pos[car, 1]
        segment = Car_Pos[car, 2]
        angle = segment * alpha

        x = (SizeOfRoad * math.cos(angle) / CoefBlender) * (1 + (lane / 19))
        y = (SizeOfRoad * math.sin(angle) / CoefBlender) * (1 + (lane / 19))

        rot = math.radians(math.degrees(angle) + (360 * Car_Rot[car]) - 90)

        ob.location = (x, y, z)
        ob.keyframe_insert('location')
        ob.rotation_euler = (rx, ry, rot)
        ob.keyframe_insert('rotation_euler')


# Give space between car and car in front of
# reel space + freed space by supposed car in front speed
# return space_IFO in segment unit
def get_space_IFO(car) -> int:
    curlane = Car_Pos[car, 1]
    curseg = Car_Pos[car, 2]
    space_IFO = 0
    while 1 == 1:
        curseg += 1
        space_IFO += 1
        if curseg > SegCount:
            curseg = 1
        if (Road_Segments[curlane, curseg] != 0):
            Car_IFO = Road_Segments[curlane, curseg]
            Speed_Car_IFO = Car_Speed[Car_IFO]
            break
    return space_IFO


# calculate the new speed for a car
def new_speed(car, space_IFO) -> int:
    # Search the speed limit to preserve speed objective and security distance
    Speed = Car_Speed[car]

    # if speed < wish speed then attempt to accelerate a bit (10 percents)
    if (Speed < SpeedWish):
        if Speed == 0:
            Speed = SpeedWish // 10
        else:
            Speed = Speed + round(Speed * 0.10)
        if (Speed > SpeedWish):
            Speed = SpeedWish

    # and now check if the speed choosen is acceptable for security reason
    # if not, adapt it
    space_IFO = space_IFO * SizeCarX  # set space_IFO in meters
    Secure_Dist = (Speed * 0.55) * 1.35
    quantum = round(Speed * 0.10)
    while space_IFO < Secure_Dist:
        # Slow down a bit (10 percents)
        Speed = Speed - quantum
        Secure_Dist = (Speed * 0.55) * 1.35
        # In case of full stop
        if (Speed < 0):
            Speed = 0
            break
    return Speed  # km/h


# ------------------
# MAIN
# ------------------

bpy.ops.transform.translate(value=(1, 1, 1))

# Create a new collection
newCol = create_collection("Cars", bpy.context.scene.collection)

# Set the initial state
initial_state(newCol)

# Set the cars behavior
# and the default speed
# speed mean speed in km/h
for i in range(1, CarCount + 1):
    Car_Speed[i] = SpeedWish

# ----------
# Simulation
# ----------

# Set animation start
scn = bpy.context.scene
scn.frame_current = 1

# Draw initial state
redraw_car(scn)

# 60 here, mean 60 seconds
for t in range(1, 400):
    # Animate all individual car with type of behavior
    # part 1 - for segment position
    for car in range(1, CarCount + 1):
        space_IFO = 0
        curlane = Car_Pos[car, 1]
        curseg = Car_Pos[car, 2]
        curspeed = Car_Speed[car]

        # Each Car try to run at maximum speed (speedwish)
        # Remove car on actual segment
        Road_Segments[curlane, curseg] = 0
        # Set the new car segment position
        space_IFO = get_space_IFO(car)
        speed = new_speed(car, space_IFO)

        # Slow down one car
        if (car == 10) and (t > 20 and t < 40):
            speed = SpeedWish // 6

        Car_Speed[car] = speed
        Car_Pos[car, 2] += round(speed * CoefSpeed)

        # Assume the road is a circle
        # and count number of pass to Pos 0 for managing angle
        if Car_Pos[car, 2] > SegCount:
            Car_Pos[car, 2] = Car_Pos[car, 2] - SegCount
            Car_Rot[car] += 1
        # Set car on new segment
        Road_Segments[Car_Pos[car, 1], Car_Pos[car, 2]] = car

    # Add 6 frames
    scn.frame_current += 6

    # Draw initial state
    redraw_car(scn)

scn.frame_end = scn.frame_current + 25

# End of script - Enjoy
