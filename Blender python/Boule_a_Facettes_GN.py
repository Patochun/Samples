import bpy
import math


# Boule a facettes - Blender 5.3+
#
# Executer ce script dans l'editeur de texte de Blender.
# Il cree une boule de miroirs avec des panneaux ranges regulierement sur la sphere.
# Les dimensions, l'espacement, le decalage et le materiau sont reglables dans le modificateur.

RADIUS = 2.0
FACETS_AROUND = 48
VERTICAL_ROWS = 24
FACET_GAP = 0.02
FACET_THICKNESS = 0.02
ROW_STAGGER = 0.5
COLLECTION_NAME = "Boule_a_Facettes_GN"
GROUP_NAME = "Boule a facettes"
GENERATED_TAG = "boule_a_facettes_gn_generated"


def new_material(name, color, metallic, roughness):
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = (*color, 1.0)
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is not None:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
        shader.inputs["Metallic"].default_value = metallic
        shader.inputs["Roughness"].default_value = roughness
    return material


def new_mirror_material():
    return new_material(
        "Boule facettes - miroir", (0.8, 0.85, 0.95), 1.0, 0.025
    )


def make_collection():
    existing = next(
        (collection for collection in bpy.data.collections
         if collection.get(GENERATED_TAG)),
        None,
    )
    if existing is not None:
        return existing

    collection = bpy.data.collections.new(COLLECTION_NAME)
    collection[GENERATED_TAG] = True
    bpy.context.scene.collection.children.link(collection)
    return collection


def make_node_group(body_material, mirror_material):
    group = bpy.data.node_groups.new(GROUP_NAME, "GeometryNodeTree")
    group[GENERATED_TAG] = True

    def socket(name, direction, socket_type, default=None, minimum=None, maximum=None,
               description=""):
        item = group.interface.new_socket(
            name=name,
            in_out=direction,
            socket_type=socket_type,
        )
        if default is not None:
            item.default_value = default
        if minimum is not None:
            item.min_value = minimum
        if maximum is not None:
            item.max_value = maximum
        item.description = description
        return item

    socket("Geometry", "OUTPUT", "NodeSocketGeometry")
    socket("Rayon", "INPUT", "NodeSocketFloat", RADIUS, 0.1, 100.0)
    socket("Facettes autour", "INPUT", "NodeSocketInt", FACETS_AROUND, 8, 256,
           "Nombre de panneaux autour de chaque rangee.")
    socket("Rangees verticales", "INPUT", "NodeSocketInt", VERTICAL_ROWS, 4, 128,
           "Nombre de rangees de panneaux entre les poles.")
    socket("Ecart entre facettes", "INPUT", "NodeSocketFloat", FACET_GAP, 0.0, 0.45,
           "Ecart relatif entre les facettes.")
    socket("Epaisseur des facettes", "INPUT", "NodeSocketFloat",
           FACET_THICKNESS, 0.001, 1.0)
    socket("Decalage des rangees", "INPUT", "NodeSocketFloat",
           ROW_STAGGER, 0.0, 0.5,
           "Decalage applique une rangee sur deux, en fraction de panneau.")
    socket("Materiau miroir", "INPUT", "NodeSocketMaterial", mirror_material,
           description="Materiau metallique a faible rugosite pour les miroirs.")

    nodes = group.nodes
    links = group.links

    def node(node_type, label, location):
        result = nodes.new(node_type)
        result.label = label
        result.location = location
        return result

    def connect(value, target):
        if isinstance(value, bpy.types.NodeSocket):
            links.new(value, target)
        else:
            target.default_value = value

    def math_node(operation, first, second=None, location=(0, 0)):
        result = node("ShaderNodeMath", operation, location)
        result.operation = operation
        connect(first, result.inputs[0])
        if second is not None:
            connect(second, result.inputs[1])
        return result.outputs[0]

    def integer_node(operation, first, second, location=(0, 0)):
        result = node("FunctionNodeIntegerMath", operation, location)
        result.operation = operation
        connect(first, result.inputs[0])
        connect(second, result.inputs[1])
        return result.outputs[0]

    inputs = node("NodeGroupInput", "Parametres", (-1400, 300))
    output = node("NodeGroupOutput", "Boule terminee", (1800, 400))

    columns = inputs.outputs["Facettes autour"]
    rows = inputs.outputs["Rangees verticales"]
    radius = inputs.outputs["Rayon"]
    thickness = inputs.outputs["Epaisseur des facettes"]
    point_count = integer_node("MULTIPLY", columns, rows, (-1150, 900))

    points = node("GeometryNodeMeshLine", "Une position par miroir", (-900, 900))
    points.inputs["Start Location"].default_value = (0.0, 0.0, 0.0)
    points.inputs["Offset"].default_value = (0.0, 0.0, 0.0)
    connect(point_count, points.inputs["Count"])

    index = node("GeometryNodeInputIndex", "Index du panneau", (-1150, -100)).outputs["Index"]
    column = integer_node("MODULO", index, columns, (-900, -100))
    row = integer_node("DIVIDE", index, columns, (-900, -300))
    row_fraction = math_node(
        "DIVIDE",
        math_node("ADD", row, 0.5, (-650, -300)),
        rows,
        (-400, -300),
    )
    latitude = math_node(
        "SUBTRACT",
        math.pi / 2.0,
        math_node("MULTIPLY", row_fraction, math.pi, (-150, -300)),
        (100, -300),
    )
    longitude_fraction = math_node("DIVIDE", column, columns, (-650, -600))
    longitude = math_node(
        "MULTIPLY", longitude_fraction, 2.0 * math.pi, (-400, -600)
    )
    row_parity = integer_node("MODULO", row, 2, (-650, -850))
    stagger = math_node(
        "MULTIPLY", row_parity, inputs.outputs["Decalage des rangees"],
        (-400, -850),
    )
    angle_per_panel = math_node(
        "DIVIDE",
        2.0 * math.pi,
        columns,
        (-400, -1050),
    )
    stagger_angle = math_node(
        "MULTIPLY", stagger, angle_per_panel, (-150, -850)
    )
    longitude = math_node("ADD", longitude, stagger_angle, (100, -600))

    latitude_cosine = math_node("COSINE", latitude, location=(350, -300))
    latitude_sine = math_node("SINE", latitude, location=(350, -500))
    longitude_cosine = math_node("COSINE", longitude, location=(350, -700))
    longitude_sine = math_node("SINE", longitude, location=(350, -900))
    direction = node("ShaderNodeCombineXYZ", "Direction sur la sphere", (850, -500))
    connect(
        math_node("MULTIPLY", latitude_cosine, longitude_cosine, (600, -700)),
        direction.inputs["X"],
    )
    connect(
        math_node("MULTIPLY", latitude_cosine, longitude_sine, (600, -900)),
        direction.inputs["Y"],
    )
    connect(latitude_sine, direction.inputs["Z"])
    north = node("ShaderNodeCombineXYZ", "Direction vers le pole Nord", (850, -900))
    connect(
        math_node(
            "MULTIPLY",
            math_node("MULTIPLY", latitude_sine, longitude_cosine, (600, -1100)),
            -1.0,
            (850, -1100),
        ),
        north.inputs["X"],
    )
    connect(
        math_node(
            "MULTIPLY",
            math_node("MULTIPLY", latitude_sine, longitude_sine, (600, -1300)),
            -1.0,
            (850, -1300),
        ),
        north.inputs["Y"],
    )
    connect(latitude_cosine, north.inputs["Z"])

    half_thickness = math_node("MULTIPLY", thickness, 0.5, (-650, -1250))
    panel_radius = math_node("ADD", radius, half_thickness, (-400, -1250))
    panel_position = node("ShaderNodeVectorMath", "Poser les panneaux", (1100, -500))
    panel_position.operation = "SCALE"
    connect(direction.outputs["Vector"], panel_position.inputs["Vector"])
    connect(panel_radius, panel_position.inputs["Scale"])
    tile_points = node("GeometryNodeSetPosition", "Grille sur la sphere", (0, 900))
    connect(points.outputs["Mesh"], tile_points.inputs["Geometry"])
    connect(panel_position.outputs["Vector"], tile_points.inputs["Position"])

    sphere = node("GeometryNodeMeshUVSphere", "Sphere support", (-650, 500))
    connect(inputs.outputs["Facettes autour"], sphere.inputs["Segments"])
    connect(integer_node("ADD", rows, 2, (-900, 500)), sphere.inputs["Rings"])
    connect(radius, sphere.inputs["Radius"])

    body = node("GeometryNodeSetMaterial", "Fond sombre sous les miroirs", (-400, 500))
    body.inputs["Material"].default_value = body_material
    connect(sphere.outputs["Mesh"], body.inputs["Geometry"])

    gap_factor = math_node(
        "SUBTRACT", 1.0, inputs.outputs["Ecart entre facettes"], (-650, -1500)
    )
    circumference = math_node(
        "MULTIPLY", radius, 2.0 * math.pi, (-900, -1700)
    )
    width_before_gap = math_node(
        "DIVIDE", circumference, columns, (-650, -1700)
    )
    tile_width = math_node(
        "MULTIPLY",
        math_node("MULTIPLY", width_before_gap, latitude_cosine, (-400, -1700)),
        gap_factor,
        (-150, -1700),
    )
    tile_height = math_node(
        "DIVIDE",
        math_node("MULTIPLY", radius, math.pi, (-900, -1950)),
        rows,
        (-650, -1950),
    )
    tile_height = math_node("MULTIPLY", tile_height, gap_factor, (-400, -1950))
    tile_size = node("ShaderNodeCombineXYZ", "Dimensions des miroirs", (100, -1650))
    connect(tile_width, tile_size.inputs["X"])
    connect(tile_height, tile_size.inputs["Y"])
    connect(thickness, tile_size.inputs["Z"])

    cube = node("GeometryNodeMeshCube", "Panneau plat", (350, -1300))
    mirror = node("GeometryNodeSetMaterial", "Materiau miroir", (600, -1300))
    connect(inputs.outputs["Materiau miroir"], mirror.inputs["Material"])
    connect(cube.outputs["Mesh"], mirror.inputs["Geometry"])

    orientation = node("FunctionNodeAxesToRotation", "Orientation des panneaux",
                       (1100, -900))
    orientation.primary_axis = "Z"
    orientation.secondary_axis = "Y"
    connect(direction.outputs["Vector"], orientation.inputs["Primary Axis"])
    connect(north.outputs["Vector"], orientation.inputs["Secondary Axis"])
    instances = node("GeometryNodeInstanceOnPoints", "Panneaux miroir", (1000, 900))
    connect(tile_points.outputs["Geometry"], instances.inputs["Points"])
    connect(mirror.outputs["Geometry"], instances.inputs["Instance"])
    connect(orientation.outputs["Rotation"], instances.inputs["Rotation"])
    connect(tile_size.outputs["Vector"], instances.inputs["Scale"])

    join = node("GeometryNodeJoinGeometry", "Sphere et facettes", (1500, 400))
    connect(body.outputs["Geometry"], join.inputs["Geometry"])
    connect(instances.outputs["Instances"], join.inputs["Geometry"])
    connect(join.outputs["Geometry"], output.inputs["Geometry"])
    return group


def main():
    if bpy.app.version < (5, 3, 0):
        raise RuntimeError("Ce script necessite Blender 5.3 ou une version plus recente.")

    existing_hosts = [
        obj for obj in bpy.data.objects if obj.get(GENERATED_TAG)
    ]
    if len(existing_hosts) > 1:
        raise RuntimeError(
            "Plusieurs boules generees sont presentes. Supprimez les anciennes "
            "collections Boule_a_Facettes_GN avant de relancer le script."
        )

    host = existing_hosts[0] if existing_hosts else None
    collection = (
        host.users_collection[0]
        if host is not None and host.users_collection
        else make_collection()
    )
    body_material = new_material(
        "Boule facettes - fond sombre", (0.025, 0.03, 0.04), 0.75, 0.28
    )
    mirror_material = new_mirror_material()

    if host is None:
        mesh = bpy.data.meshes.new("Boule a facettes - support")
        host = bpy.data.objects.new("Boule a facettes", mesh)
        host[GENERATED_TAG] = True
        collection.objects.link(host)

    node_group = make_node_group(body_material, mirror_material)
    modifier = next(
        (
            item for item in host.modifiers
            if item.type == "NODES"
            and item.node_group is not None
            and item.node_group.get(GENERATED_TAG)
        ),
        None,
    )
    if modifier is None:
        modifier = host.modifiers.new("Boule a facettes", "NODES")
    modifier.node_group = node_group

    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = host
    host.select_set(True)
    return host


if __name__ == "__main__":
    main()
