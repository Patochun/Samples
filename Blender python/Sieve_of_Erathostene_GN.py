import bpy


# Sieve_of_Erathostene_GN
# Blender 5.3+
#
# Run this script from Blender's Text Editor.
# The Geometry Nodes simulation processes one candidate per frame.
# Bake the simulation cache before rendering or scrubbing freely.

BIG_CUBE_EDGE = 5
SPACING = 2.5
CUBE_SIZE = 1.8
FRAMES_PER_CANDIDATE = 1
COLLECTION_NAME = "Sieve_Erathostene_GN"
GROUP_NAME = "Sieve of Erathostene - Simulation"
GENERATED_TAG = "sieve_of_erathostene_gn_generated"


def new_material(name, color):
    material = bpy.data.materials.new(name=name)
    material.diffuse_color = (*color, 1.0)
    shader = material.node_tree.nodes.get("Principled BSDF")
    if shader is not None:
        shader.inputs["Base Color"].default_value = (*color, 1.0)
    return material


def make_collection():
    collection = bpy.data.collections.new(COLLECTION_NAME)
    collection[GENERATED_TAG] = True
    bpy.context.scene.collection.children.link(collection)
    return collection


def make_node_group(cube_material, active_material, text_material):
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

    socket("Geometry", "INPUT", "NodeSocketGeometry")
    socket("Geometry", "OUTPUT", "NodeSocketGeometry")
    socket("Taille du cube", "INPUT", "NodeSocketInt", BIG_CUBE_EDGE, 2, 20,
           "Nombre de cubes sur chaque axe.")
    socket("Espacement", "INPUT", "NodeSocketFloat", SPACING, 0.1, 100.0)
    socket("Taille des cubes", "INPUT", "NodeSocketFloat", CUBE_SIZE, 0.01, 100.0)
    socket("Images par candidat", "INPUT", "NodeSocketInt",
           FRAMES_PER_CANDIDATE, 1, 100,
           "Nombre d'images entre deux candidats du crible.")

    nodes = group.nodes
    links = group.links

    def node(node_type, label, location):
        result = nodes.new(node_type)
        result.label = label
        result.location = location
        return result

    def connect(value, target, socket_name=None):
        if isinstance(value, bpy.types.NodeSocket):
            links.new(value, target if socket_name is None else target.inputs[socket_name])
        elif socket_name is not None:
            target.inputs[socket_name].default_value = value
        else:
            target.default_value = value

    def math_node(operation, a, b=None, location=(0, 0)):
        result = node("ShaderNodeMath", operation, location)
        result.operation = operation
        connect(a, result.inputs[0])
        if b is not None:
            connect(b, result.inputs[1])
        return result.outputs[0]

    def int_node(operation, a, b, location=(0, 0)):
        result = node("FunctionNodeIntegerMath", operation, location)
        result.operation = operation
        connect(a, result.inputs[0])
        connect(b, result.inputs[1])
        return result.outputs[0]

    def bool_node(operation, a, b=None, location=(0, 0)):
        result = node("FunctionNodeBooleanMath", operation, location)
        result.operation = operation
        connect(a, result.inputs[0])
        if b is not None:
            connect(b, result.inputs[1])
        return result.outputs[0]

    def named_attribute(name, location):
        result = node("GeometryNodeInputNamedAttribute", name, location)
        result.data_type = "BOOLEAN"
        result.inputs["Name"].default_value = name
        return result.outputs["Attribute"]

    group_input = node("NodeGroupInput", "Parametres", (-1500, 500))
    group_output = node("NodeGroupOutput", "Sortie", (1900, 500))

    # Build one point per number and place the points in the original 3D order.
    edge = group_input.outputs["Taille du cube"]
    edge_squared = int_node("MULTIPLY", edge, edge, (-1250, 900))
    point_count = int_node("MULTIPLY", edge_squared, edge, (-1050, 900))

    mesh_line = node("GeometryNodeMeshLine", "Un point par cube", (-850, 900))
    mesh_line.inputs["Start Location"].default_value = (0.0, 0.0, 0.0)
    mesh_line.inputs["Offset"].default_value = (0.0, 0.0, 0.0)
    connect(point_count, mesh_line, "Count")

    grid_index = node("GeometryNodeInputIndex", "Numero - 1", (-1250, 400)).outputs["Index"]
    x_index = int_node("MODULO", grid_index, edge, (-1050, 350))
    row_index = int_node("DIVIDE", grid_index, edge, (-1050, 150))
    y_index = int_node("MODULO", row_index, edge, (-850, 150))
    z_index = int_node("DIVIDE", grid_index, edge_squared, (-1050, -50))
    y_coord = math_node("SUBTRACT", edge, y_index, (-650, 150))
    z_coord = math_node("SUBTRACT", edge, z_index, (-650, -50))
    x_position = math_node(
        "MULTIPLY", x_index, group_input.outputs["Espacement"], (-450, 350)
    )
    y_position = math_node(
        "MULTIPLY", y_coord, group_input.outputs["Espacement"], (-450, 150)
    )
    z_position = math_node(
        "MULTIPLY", z_coord, group_input.outputs["Espacement"], (-450, -50)
    )
    position = node("ShaderNodeCombineXYZ", "Position en grille", (-250, 200))
    connect(x_position, position.inputs["X"])
    connect(y_position, position.inputs["Y"])
    connect(z_position, position.inputs["Z"])
    set_position = node("GeometryNodeSetPosition", "Placer la grille", (-50, 900))
    connect(mesh_line.outputs["Mesh"], set_position, "Geometry")
    connect(position.outputs["Vector"], set_position, "Position")

    initial_number = node("GeometryNodeStoreNamedAttribute", "Numero d'origine",
                          (0, 1150))
    initial_number.data_type = "INT"
    initial_number.domain = "POINT"
    initial_number.inputs["Name"].default_value = "sieve_number"
    connect(set_position.outputs["Geometry"], initial_number, "Geometry")
    connect(int_node("ADD", grid_index, 1, (-250, 600)), initial_number, "Value")

    initial_alive = node("GeometryNodeStoreNamedAttribute", "Initialiser les nombres",
                         (150, 900))
    initial_alive.data_type = "BOOLEAN"
    initial_alive.domain = "POINT"
    initial_alive.inputs["Name"].default_value = "sieve_alive"
    initial_alive.inputs["Value"].default_value = True
    connect(initial_number.outputs["Geometry"], initial_alive, "Geometry")
    initial_current = node("GeometryNodeStoreNamedAttribute", "Initialiser la selection",
                           (350, 1100))
    initial_current.data_type = "BOOLEAN"
    initial_current.domain = "POINT"
    initial_current.inputs["Name"].default_value = "sieve_current"
    initial_current.inputs["Value"].default_value = False
    connect(initial_alive.outputs["Geometry"], initial_current, "Geometry")

    # The simulation carries the alive state forward from one frame to the next.
    sim_input = node("GeometryNodeSimulationInput", "Etat precedent", (400, 900))
    sim_output = node("GeometryNodeSimulationOutput", "Etat suivant", (1100, 900))
    sim_input.pair_with_output(sim_output)
    connect(initial_current.outputs["Geometry"], sim_input, "Geometry")

    sim_index = node("GeometryNodeInputIndex", "Numero - 1", (400, 250)).outputs["Index"]
    number = int_node("ADD", sim_index, 1, (600, 250))

    scene_time = node("GeometryNodeInputSceneTime", "Temps de la scene", (350, -200))
    frame_offset = math_node(
        "SUBTRACT", scene_time.outputs["Frame"], bpy.context.scene.frame_start,
        (550, -200),
    )
    frame_step = math_node(
        "DIVIDE", frame_offset, group_input.outputs["Images par candidat"],
        (750, -200),
    )
    candidate = math_node("ADD", math_node("FLOOR", frame_step, location=(950, -200)),
                          1.0, (1150, -200))

    alive_before = named_attribute("sieve_alive", (550, 500))
    is_one = math_node("COMPARE", number, 1.0, (800, 200))
    candidate_is_one = math_node("COMPARE", candidate, 1.0, (1350, -200))
    remove_one = bool_node(
        "AND", is_one, candidate_is_one, (1550, 100)
    )

    candidate_after_one = math_node("GREATER_THAN", candidate, 1.0, (1350, -400))
    number_after_candidate = math_node("GREATER_THAN", number, candidate, (1000, 0))
    remainder = math_node(
        "FLOORED_MODULO", number, candidate, (1200, 0)
    )
    is_multiple = math_node("COMPARE", remainder, 0.0, (1400, 0))
    remove_multiple = bool_node(
        "AND",
        candidate_after_one,
        bool_node("AND", number_after_candidate, is_multiple, (1600, -100)),
        (1800, -100),
    )
    remove_number = bool_node("OR", remove_one, remove_multiple, (2000, 100))
    alive_after = bool_node(
        "AND", alive_before, bool_node("NOT", remove_number, location=(2200, 100)),
        (2400, 300),
    )

    store_alive = node("GeometryNodeStoreNamedAttribute", "Mettre a jour les nombres",
                       (2700, 900))
    store_alive.data_type = "BOOLEAN"
    store_alive.domain = "POINT"
    store_alive.inputs["Name"].default_value = "sieve_alive"
    connect(sim_input.outputs["Geometry"], store_alive, "Geometry")
    connect(alive_after, store_alive, "Value")

    is_candidate = math_node("COMPARE", number, candidate, (1000, -500))
    candidate_is_prime = bool_node(
        "AND",
        is_candidate,
        bool_node("AND", alive_before,
                  candidate_after_one, (1600, -450)),
        (1800, -450),
    )
    store_current = node("GeometryNodeStoreNamedAttribute", "Surligner le candidat",
                         (2950, 900))
    store_current.data_type = "BOOLEAN"
    store_current.domain = "POINT"
    store_current.inputs["Name"].default_value = "sieve_current"
    connect(store_alive.outputs["Geometry"], store_current, "Geometry")
    connect(candidate_is_prime, store_current, "Value")
    connect(store_current.outputs["Geometry"], sim_output, "Geometry")

    # Keep only live points, then instance cubes and their number labels.
    alive_after_sim = named_attribute("sieve_alive", (1300, 500))
    current_after_sim = named_attribute("sieve_current", (1300, 250))
    separate_alive = node("GeometryNodeSeparateGeometry", "Nombres encore actifs",
                          (1500, 700))
    separate_alive.domain = "POINT"
    connect(sim_output.outputs["Geometry"], separate_alive, "Geometry")
    connect(alive_after_sim, separate_alive, "Selection")

    separate_current = node("GeometryNodeSeparateGeometry", "Candidat courant",
                            (1700, 700))
    separate_current.domain = "POINT"
    connect(separate_alive.outputs["Selection"], separate_current, "Geometry")
    connect(current_after_sim, separate_current, "Selection")

    # Cube instances use separate materials for ordinary and current candidates.
    cube = node("GeometryNodeMeshCube", "Cube", (1200, -850))
    connect(group_input.outputs["Taille des cubes"], cube.inputs["Size"])
    cube_normal = node("GeometryNodeSetMaterial", "Materiau normal", (1400, -850))
    cube_normal.inputs["Material"].default_value = cube_material
    connect(cube.outputs["Mesh"], cube_normal, "Geometry")
    cube_active = node("GeometryNodeSetMaterial", "Materiau actif", (1400, -1050))
    cube_active.inputs["Material"].default_value = active_material
    connect(cube.outputs["Mesh"], cube_active, "Geometry")

    cube_instances = node("GeometryNodeInstanceOnPoints", "Cubes", (1900, 350))
    connect(separate_current.outputs["Inverted"], cube_instances, "Points")
    connect(cube_normal.outputs["Geometry"], cube_instances, "Instance")
    active_cube_instances = node("GeometryNodeInstanceOnPoints", "Cube candidat",
                                 (1900, 100))
    connect(separate_current.outputs["Selection"], active_cube_instances, "Points")
    connect(cube_active.outputs["Geometry"], active_cube_instances, "Instance")

    # Text geometry cannot be driven by a field, so generate it once per point.
    foreach_in = node("GeometryNodeForeachGeometryElementInput", "Numeros par point",
                      (1250, -1200))
    foreach_out = node("GeometryNodeForeachGeometryElementOutput", "Numeros generes",
                       (2700, -1200))
    foreach_in.pair_with_output(foreach_out)
    foreach_out.domain = "POINT"
    foreach_out.input_items.new("INT", "Numero")
    foreach_out.input_items.new("VECTOR", "Position")
    foreach_out.input_items.new("BOOLEAN", "Candidat")
    connect(separate_alive.outputs["Selection"], foreach_in, "Geometry")

    number_attribute = node("GeometryNodeInputNamedAttribute", "Lire le numero d'origine",
                            (1050, -1400))
    number_attribute.data_type = "INT"
    number_attribute.inputs["Name"].default_value = "sieve_number"
    connect(number_attribute.outputs["Attribute"], foreach_in, "Numero")
    position_attribute = node("GeometryNodeInputPosition", "Position du cube", (1050, -1600))
    connect(position_attribute.outputs["Position"], foreach_in, "Position")
    connect(current_after_sim, foreach_in, "Candidat")

    value_to_string = node("FunctionNodeValueToString", "Numero en texte", (1450, -1300))
    value_to_string.data_type = "INT"
    connect(foreach_in.outputs["Numero"], value_to_string, "Value")
    string_to_curves = node("GeometryNodeStringToCurves", "Etiquettes", (1650, -1300))
    string_to_curves.inputs["Align X"].default_value = "Center"
    connect(value_to_string.outputs["String"], string_to_curves, "String")
    string_to_curves.inputs["Size"].default_value = 0.65
    text_realized = node("GeometryNodeRealizeInstances", "Realiser les caracteres",
                         (1850, -1300))
    connect(string_to_curves.outputs["Curve Instances"], text_realized, "Geometry")
    text_mesh = node("GeometryNodeFillCurve", "Surface du texte", (2050, -1300))
    connect(text_realized.outputs["Geometry"], text_mesh, "Curve")
    text_normal = node("GeometryNodeSetMaterial", "Texte normal", (2250, -1300))
    text_normal.inputs["Material"].default_value = text_material
    connect(text_mesh.outputs["Mesh"], text_normal, "Geometry")
    text_active = node("GeometryNodeSetMaterial", "Texte actif", (2450, -1300))
    text_active.inputs["Material"].default_value = active_material
    connect(text_normal.outputs["Geometry"], text_active, "Geometry")
    connect(foreach_in.outputs["Candidat"], text_active, "Selection")
    label_number = node("GeometryNodeStoreNamedAttribute", "Conserver le numero du texte",
                        (2650, -1400))
    label_number.data_type = "INT"
    label_number.domain = "FACE"
    label_number.inputs["Name"].default_value = "sieve_number"
    connect(text_active.outputs["Geometry"], label_number, "Geometry")
    connect(foreach_in.outputs["Numero"], label_number, "Value")
    offset = node("ShaderNodeCombineXYZ", "Decalage du texte", (2050, -1650))
    offset.inputs["Y"].default_value = -0.35
    connect(
        math_node("ADD", math_node("MULTIPLY", group_input.outputs["Taille des cubes"],
                                   0.5, (1650, -1750)), 0.01, (1850, -1750)),
        offset.inputs["Z"],
    )
    label_position = node("ShaderNodeVectorMath", "Position du texte", (2250, -1650))
    label_position.operation = "ADD"
    connect(foreach_in.outputs["Position"], label_position.inputs[0])
    connect(offset.outputs["Vector"], label_position.inputs[1])
    text_transform = node("GeometryNodeTransform", "Placer au-dessus du cube",
                          (2850, -1300))
    connect(label_number.outputs["Geometry"], text_transform, "Geometry")
    connect(label_position.outputs["Vector"], text_transform, "Translation")
    connect(text_transform.outputs["Geometry"], foreach_out, "Geometry")

    join = node("GeometryNodeJoinGeometry", "Cubes et numeros", (2400, 350))
    connect(cube_instances.outputs["Instances"], join.inputs["Geometry"])
    connect(active_cube_instances.outputs["Instances"], join.inputs["Geometry"])
    connect(next(s for s in foreach_out.outputs if s.identifier == "Generation_0"),
            join.inputs["Geometry"])
    connect(join.outputs["Geometry"], group_output.inputs["Geometry"])
    return group


def main():
    scene = bpy.context.scene
    if bpy.app.version < (5, 3, 0):
        raise RuntimeError("Ce script necessite Blender 5.3 ou une version plus recente.")
    scene.frame_start = 1
    scene.render.fps = 25
    collection = make_collection()

    cube_material = new_material("Sieve GN - Cube", (0.8, 0.4, 0.2))
    active_material = new_material("Sieve GN - Candidat", (0.4, 1.0, 0.2))
    text_material = new_material("Sieve GN - Numeros", (1.0, 0.0, 0.0))

    mesh = bpy.data.meshes.new("Sieve GN Host Mesh")
    host = bpy.data.objects.new("Sieve of Erathostene GN", mesh)
    host[GENERATED_TAG] = True
    collection.objects.link(host)

    node_group = make_node_group(cube_material, active_material, text_material)
    modifier = host.modifiers.new("Crible d'Eratosthene", "NODES")
    modifier.node_group = node_group

    scene.frame_end = (
        scene.frame_start
        + ((BIG_CUBE_EDGE ** 3) - 1) * FRAMES_PER_CANDIDATE
        + 100
    )
    scene.frame_set(scene.frame_start)
    bpy.context.view_layer.objects.active = host
    host.select_set(True)

    print(
        "Geometry Nodes Sieve created. Bake the Simulation Zone cache before "
        "rendering or scrubbing."
    )


main()
