import bpy
import math

# X_Modulo_GN_3D - Blender 5.3
# Author: Patochun (Patrick M) - Licence Creative Commons CC BY
# https://www.youtube.com/channel/UCCNXecgdUbUChEyvW3gFWvw
# https://creativecommons.org
#
# Executer ce script dans l'editeur de texte de Blender. Il ajoute un
# modificateur Geometry Nodes au cube nomme "Cube", sans modifier son maillage.
# Les reglages sont accessibles dans le modificateur :
#   Repartition : 0 = Fibonacci, 1 = aleatoire uniforme, 2 = anneaux,
#     3 = colimacon, 4 = anneaux decales, 5 = meridiens,
#     6 = grille perturbee, 7 = icosphere, 8 = paires antipodales,
#     9 = bande equatoriale, 10 = double spirale, 11 = trois grands cercles.
#   Graine : variation de Fibonacci, des points aleatoires, de la grille
#     ou de la bande equatoriale.
#   Points par anneau : maximum par anneau, le dernier pouvant etre incomplet.
#   Colimacon : nombre de tours et choix entre hauteur ou latitude reguliere.
#     Le premier point est au pole Nord (+Z), le dernier au pole Sud (-Z).
#   Anneaux decales : fraction d'un intervalle ajoutee a chaque anneau.
#   Meridiens : nombre maximal de points par meridien, sans doublons aux poles.
#   Grille perturbee : amplitude relative aux intervalles de la grille.
#   Icosphere : le nombre de points depend du niveau de subdivision et non
#     du reglage Nombre de points. Son ordre est celui des sommets de Blender.
#   Paires antipodales et double spirale : les points sont alternes par paire ;
#     avec un nombre impair, le dernier point n'a pas de partenaire.
#   Bande equatoriale : demi-largeur en degres, de 0 (equateur) a 90 (sphere).
#   Double spirale : nombre de tours commun au reglage du colimacon.
#   Grands cercles : les points alternent entre trois plans orthogonaux.
# Les anciens modes 0 a 2 conservent leur axe polaire Y ; les nouveaux utilisent Z.
# Le point i est relie au point (i * Table) modulo le nombre reel de points.
# Le point 0 n'emet pas de lien, comme dans le script d'origine.
#   Filtre des nombres : 0 = tous, 1 = non premiers (dont 0 et 1),
#     2 = premiers. Les numeros affiches restent les indices d'origine.
#   Modulo sur selection : active, les liens utilisent les rangs de la
#     selection ; desactive, les liens gardent les indices d'origine et seuls
#     ceux dont les deux extremites sont selectionnees restent visibles.
#   Afficher les numeros : etiquettes orientees vers la camera, avec une
#     taille reglable. Leur generation peut etre lente pour beaucoup de points.
#
# A chaque execution, le modificateur X Modulo est remplace et ses reglages
# reviennent aux valeurs par defaut. Les autres modificateurs sont conserves.
# La lumiere ponctuelle est placee au centre (puissance 10000), le World est
# noir et la camera effectue un tour en 720 images a 24 images/seconde.
# Les images 1 a 720 constituent une boucle ; l'animation continue au-dela.


def create_modulo_nodes():
    group = bpy.data.node_groups.new("X Modulo 3D", "GeometryNodeTree")
    group["x_modulo_3d"] = True

    def socket(name, direction, socket_type, default=None, minimum=None, maximum=None, description=""):
        item = group.interface.new_socket(name=name, in_out=direction, socket_type=socket_type)
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
    socket("Repartition", "INPUT", "NodeSocketInt", 0, 0, 11,
           "0 Fibonacci, 1 aleatoire, 2 anneaux, 3 colimacon, "
           "4 anneaux decales, 5 meridiens, 6 grille perturbee, 7 icosphere, "
           "8 paires antipodales, 9 bande equatoriale, 10 double spirale, 11 grands cercles")
    socket("Nombre de points", "INPUT", "NodeSocketInt", 1000, 2, 10000)
    socket("Table", "INPUT", "NodeSocketInt", 2, 0, 10000)
    socket("Rayon sphere", "INPUT", "NodeSocketFloat", 1.0, 0.001, 10000.0)
    socket("Graine", "INPUT", "NodeSocketInt", 20, 0, 1000000)
    socket("Points par anneau", "INPUT", "NodeSocketInt", 32, 1, 10000)
    socket("Afficher les liens", "INPUT", "NodeSocketBool", True)
    socket("Rayon des liens", "INPUT", "NodeSocketFloat", 0.002, 0.00001, 100.0)
    socket("Afficher les points", "INPUT", "NodeSocketBool", False)
    socket("Rayon des points", "INPUT", "NodeSocketFloat", 0.01, 0.00001, 100.0)
    socket("Tours du colimacon", "INPUT", "NodeSocketFloat", 8.0, 0.0, 1000.0)
    socket("Colimacon surface uniforme", "INPUT", "NodeSocketBool", True,
           description="Active : hauteur reguliere ; desactive : latitude reguliere")
    socket("Decalage des anneaux", "INPUT", "NodeSocketFloat", 0.5, 0.0, 1.0,
           "Fraction d'un intervalle entre points, ajoutee a chaque anneau")
    socket("Points par meridien", "INPUT", "NodeSocketInt", 32, 1, 10000)
    socket("Perturbation de la grille", "INPUT", "NodeSocketFloat", 0.5, 0.0, 1.0,
           "Amplitude relative aux intervalles de latitude et de longitude")
    socket("Subdivisions icosphere", "INPUT", "NodeSocketInt", 3, 1, 6,
           "1 a 6 : 12, 42, 162, 642, 2562 ou 10242 sommets")
    socket("Demi-largeur bande", "INPUT", "NodeSocketFloat", 20.0, 0.0, 90.0,
           "Demi-largeur de la bande equatoriale en degres")
    socket("Filtre des nombres", "INPUT", "NodeSocketInt", 0, 0, 2,
           "0 : tous, 1 : non premiers (0 et 1 inclus), 2 : premiers")
    socket("Modulo sur selection", "INPUT", "NodeSocketBool", False,
           description="Active : recalculer les liens sur les rangs selectionnes ; "
                       "desactive : garder les liens d'origine entre points selectionnes")
    socket("Afficher les numeros", "INPUT", "NodeSocketBool", False)
    socket("Taille des numeros", "INPUT", "NodeSocketFloat", 0.1, 0.001, 100.0)

    nodes = group.nodes
    links = group.links
    rows = {}

    def node(node_type, label, column):
        result = nodes.new(node_type)
        result.label = label
        row = rows.get(column, 0)
        result.location = (column * 230, -row * 180)
        rows[column] = row + 1
        return result

    def connect(value, target):
        if value is None:
            return
        if isinstance(value, bpy.types.NodeSocket):
            links.new(value, target)
        else:
            target.default_value = value

    def math_node(operation, a, b=None, column=1):
        result = node("ShaderNodeMath", operation, column)
        result.operation = operation
        connect(a, result.inputs[0])
        if b is not None:
            connect(b, result.inputs[1])
        return result.outputs[0]

    def int_node(operation, a, b, column=1):
        result = node("FunctionNodeIntegerMath", operation, column)
        result.operation = operation
        connect(a, result.inputs[0])
        connect(b, result.inputs[1])
        return result.outputs[0]

    def boolean_node(operation, a, b=None, column=1):
        result = node("FunctionNodeBooleanMath", operation, column)
        result.operation = operation
        connect(a, result.inputs[0])
        if b is not None:
            connect(b, result.inputs[1])
        return result.outputs[0]

    def switch(data_type, condition, false_value, true_value, column):
        result = node("GeometryNodeSwitch", "Choix", column)
        result.input_type = data_type
        connect(condition, result.inputs["Switch"])
        connect(false_value, result.inputs["False"])
        connect(true_value, result.inputs["True"])
        return result.outputs["Output"]

    inputs = node("NodeGroupInput", "Parametres", 0)
    outputs = node("NodeGroupOutput", "Resultat", 13)
    count = inputs.outputs["Nombre de points"]
    seed = inputs.outputs["Graine"]
    index = node("GeometryNodeInputIndex", "Index", 0).outputs["Index"]

    # Chaque distribution produit une hauteur Y et un angle autour de Y.
    latitude = math_node("DIVIDE", math_node("ADD", index, 0.5), count, 2)
    fibonacci_y = math_node("SUBTRACT", math_node("MULTIPLY", latitude, 2.0, 3), 1.0, 4)
    constant_id = node("FunctionNodeInputInt", "Graine globale", 1)
    constant_id.integer = 0
    shift = node("FunctionNodeRandomValue", "Decalage Fibonacci", 2)
    shift.data_type = "FLOAT"
    connect(constant_id.outputs[0], shift.inputs["ID"])
    connect(seed, shift.inputs["Seed"])
    shifted_index = math_node("ADD", index, math_node("MULTIPLY", shift.outputs["Value"], count, 3), 4)
    wrapped_index = math_node("FLOORED_MODULO", shifted_index, count, 5)
    fibonacci_angle = math_node("MULTIPLY", wrapped_index, math.pi * (3.0 - math.sqrt(5.0)), 6)

    random_y = node("FunctionNodeRandomValue", "Hauteur aleatoire", 2)
    random_y.data_type = "FLOAT"
    random_y.inputs["Min"].default_value = -1.0
    random_y.inputs["Max"].default_value = 1.0
    connect(index, random_y.inputs["ID"])
    connect(seed, random_y.inputs["Seed"])
    random_angle = node("FunctionNodeRandomValue", "Angle aleatoire", 2)
    random_angle.data_type = "FLOAT"
    random_angle.inputs["Max"].default_value = 2.0 * math.pi
    connect(index, random_angle.inputs["ID"])
    connect(int_node("ADD", seed, 1, 1), random_angle.inputs["Seed"])

    per_ring = inputs.outputs["Points par anneau"]
    ring_index = int_node("DIVIDE", index, per_ring, 2)
    ring_count = math_node("CEIL", math_node("DIVIDE", count, per_ring, 2), column=3)
    ring_fraction = math_node("DIVIDE", math_node("ADD", ring_index, 0.5, 3), ring_count, 4)
    ring_y = math_node("COSINE", math_node("MULTIPLY", ring_fraction, math.pi, 5), column=6)
    ring_offset = int_node("MODULO", index, per_ring, 2)
    remaining = int_node("SUBTRACT", count, int_node("MULTIPLY", ring_index, per_ring, 2), 3)
    ring_size = int_node("MINIMUM", per_ring, remaining, 3)
    ring_angle = math_node("MULTIPLY", math_node("DIVIDE", ring_offset, ring_size, 3), 2.0 * math.pi, 4)

    spiral_fraction = math_node("DIVIDE", index, int_node("SUBTRACT", count, 1, 2), 3)
    spiral_uniform_y = math_node("SUBTRACT", 1.0, math_node("MULTIPLY", spiral_fraction, 2.0, 4), 5)
    spiral_latitude_y = math_node("COSINE", math_node("MULTIPLY", spiral_fraction, math.pi, 4), column=5)
    spiral_y = switch("FLOAT", inputs.outputs["Colimacon surface uniforme"],
                      spiral_latitude_y, spiral_uniform_y, 6)
    spiral_angle = math_node("MULTIPLY", math_node(
        "MULTIPLY", spiral_fraction, inputs.outputs["Tours du colimacon"], 4), 2.0 * math.pi, 5)

    ring_shift = math_node("DIVIDE", math_node(
        "MULTIPLY", ring_index, inputs.outputs["Decalage des anneaux"], 3), ring_size, 4)
    shifted_ring_angle = math_node("ADD", ring_angle, math_node(
        "MULTIPLY", ring_shift, 2.0 * math.pi, 5), 6)

    per_meridian = inputs.outputs["Points par meridien"]
    meridian_index = int_node("DIVIDE", index, per_meridian, 2)
    meridian_offset = int_node("MODULO", index, per_meridian, 2)
    meridian_count = math_node("CEIL", math_node("DIVIDE", count, per_meridian, 2), column=3)
    meridian_remaining = int_node("SUBTRACT", count, int_node(
        "MULTIPLY", meridian_index, per_meridian, 2), 3)
    meridian_size = int_node("MINIMUM", per_meridian, meridian_remaining, 3)
    meridian_fraction = math_node("DIVIDE", math_node("ADD", meridian_offset, 0.5, 3), meridian_size, 4)
    meridian_y = math_node("COSINE", math_node("MULTIPLY", meridian_fraction, math.pi, 5), column=6)
    meridian_angle = math_node("MULTIPLY", math_node(
        "DIVIDE", meridian_index, meridian_count, 4), 2.0 * math.pi, 5)

    def jitter(label, seed_offset):
        random_value = node("FunctionNodeRandomValue", label, 3)
        random_value.data_type = "FLOAT"
        random_value.inputs["Min"].default_value = -0.5
        random_value.inputs["Max"].default_value = 0.5
        connect(index, random_value.inputs["ID"])
        connect(int_node("ADD", seed, seed_offset, 2), random_value.inputs["Seed"])
        return math_node("MULTIPLY", random_value.outputs["Value"],
                         inputs.outputs["Perturbation de la grille"], 4)

    grid_latitude = math_node("DIVIDE", math_node(
        "ADD", math_node("ADD", ring_index, 0.5, 3), jitter("Latitude perturbee", 2), 4), ring_count, 5)
    grid_y = math_node("COSINE", math_node("MULTIPLY", grid_latitude, math.pi, 6), column=7)
    grid_angle = math_node("MULTIPLY", math_node(
        "DIVIDE", math_node("ADD", ring_offset, jitter("Longitude perturbee", 3), 4),
        ring_size, 5), 2.0 * math.pi, 6)

    pair_index = int_node("DIVIDE", index, 2, 2)
    pair_side = int_node("MODULO", index, 2, 2)
    pair_count = math_node("CEIL", math_node("DIVIDE", count, 2, 2), column=3)
    pair_fraction = math_node("DIVIDE", math_node("ADD", pair_index, 0.5, 3), pair_count, 4)
    antipodal_y = switch("FLOAT", pair_side, pair_fraction,
                         math_node("MULTIPLY", pair_fraction, -1.0, 4), 5)
    antipodal_angle = math_node("ADD", math_node(
        "MULTIPLY", pair_index, math.pi * (3.0 - math.sqrt(5.0)), 4),
        math_node("MULTIPLY", pair_side, math.pi, 4), 5)

    band_limit = math_node("SINE", math_node(
        "MULTIPLY", inputs.outputs["Demi-largeur bande"], math.pi / 180.0, 4), column=5)
    band_y = math_node("MULTIPLY", fibonacci_y, band_limit, 6)

    double_y = math_node("SUBTRACT", 1.0, math_node("MULTIPLY", pair_fraction, 2.0, 4), 5)
    double_angle = math_node("ADD", math_node(
        "MULTIPLY", math_node("MULTIPLY", pair_fraction, inputs.outputs["Tours du colimacon"], 4),
        2.0 * math.pi, 5), math_node("MULTIPLY", pair_side, math.pi, 4), 6)

    distribution = inputs.outputs["Repartition"]
    is_random = math_node("COMPARE", distribution, 1, 5)
    is_rings = math_node("COMPARE", distribution, 2, 5)
    y = switch("FLOAT", is_random, fibonacci_y, random_y.outputs["Value"], 7)
    y = switch("FLOAT", is_rings, y, ring_y, 8)
    angle = switch("FLOAT", is_random, fibonacci_angle, random_angle.outputs["Value"], 7)
    angle = switch("FLOAT", is_rings, angle, ring_angle, 8)
    for mode, mode_y, mode_angle in (
        (3, spiral_y, spiral_angle),
        (4, ring_y, shifted_ring_angle),
        (5, meridian_y, meridian_angle),
        (6, grid_y, grid_angle),
        (8, antipodal_y, antipodal_angle),
        (9, band_y, fibonacci_angle),
        (10, double_y, double_angle),
    ):
        selected = math_node("COMPARE", distribution, mode, 7)
        y = switch("FLOAT", selected, y, mode_y, 8)
        angle = switch("FLOAT", selected, angle, mode_angle, 8)
    radial = math_node("SQRT", math_node("MAXIMUM", math_node(
        "SUBTRACT", 1.0, math_node("MULTIPLY", y, y, 8), 9), 0.0, 9), column=10)
    horizontal_z = math_node("MULTIPLY", radial, math_node("SINE", angle, column=9), 10)
    z_is_north = math_node("GREATER_THAN", distribution, 2, 9)
    vector = node("ShaderNodeCombineXYZ", "Position sur la sphere", 10)
    connect(math_node("MULTIPLY", radial, math_node("COSINE", angle, column=9), 10), vector.inputs["X"])
    connect(switch("FLOAT", z_is_north, y, horizontal_z, 10), vector.inputs["Y"])
    connect(switch("FLOAT", z_is_north, horizontal_z, y, 10), vector.inputs["Z"])

    circle_group = int_node("MODULO", index, 3, 3)
    circle_index = int_node("DIVIDE", index, 3, 3)
    circle_size = int_node("DIVIDE", int_node(
        "SUBTRACT", int_node("ADD", count, 2, 3), circle_group, 4), 3, 5)
    circle_angle = math_node("MULTIPLY", math_node(
        "DIVIDE", math_node("ADD", circle_index, 0.125, 4), circle_size, 5), 2.0 * math.pi, 6)
    circle_cos = math_node("COSINE", circle_angle, column=7)
    circle_sin = math_node("SINE", circle_angle, column=7)
    circle_is_0 = math_node("COMPARE", circle_group, 0, 7)
    circle_is_2 = math_node("COMPARE", circle_group, 2, 7)
    circles = node("ShaderNodeCombineXYZ", "Trois grands cercles", 10)
    connect(switch("FLOAT", circle_is_2, circle_cos, 0.0, 8), circles.inputs["X"])
    connect(switch("FLOAT", circle_is_0, switch("FLOAT", circle_is_2, 0.0, circle_cos, 8),
                   circle_sin, 8), circles.inputs["Y"])
    connect(switch("FLOAT", circle_is_0, circle_sin, 0.0, 8), circles.inputs["Z"])
    is_circles = math_node("COMPARE", distribution, 11, 9)
    sphere_position = switch("VECTOR", is_circles, vector.outputs["Vector"], circles.outputs["Vector"], 11)
    scale = node("ShaderNodeVectorMath", "Rayon de la sphere", 11)
    scale.operation = "SCALE"
    connect(sphere_position, scale.inputs[0])
    connect(inputs.outputs["Rayon sphere"], scale.inputs["Scale"])

    points = node("GeometryNodeMeshLine", "Points indexes", 7)
    connect(count, points.inputs["Count"])
    positions = node("GeometryNodeSetPosition", "Repartition des points", 12)
    connect(points.outputs["Mesh"], positions.inputs["Geometry"])
    connect(scale.outputs["Vector"], positions.inputs["Position"])

    ico = node("GeometryNodeMeshIcoSphere", "Sommets de l'icosphere", 12)
    connect(inputs.outputs["Rayon sphere"], ico.inputs["Radius"])
    connect(inputs.outputs["Subdivisions icosphere"], ico.inputs["Subdivisions"])
    is_ico = math_node("COMPARE", distribution, 7, 11)
    point_geometry = switch("GEOMETRY", is_ico, positions.outputs["Geometry"], ico.outputs["Mesh"], 13)
    point_geometry.node.label = "Points de la distribution"

    # Les indices vont de 0 a 10241 au maximum (icosphere de niveau 6).
    is_prime = math_node("GREATER_THAN", index, 1, 13)
    for divisor in range(2, math.isqrt(10241) + 1):
        if any(divisor % factor == 0 for factor in range(2, math.isqrt(divisor) + 1)):
            continue
        divisible = math_node("COMPARE", int_node("MODULO", index, divisor, 13), 0, 14)
        composite = boolean_node("AND", divisible, math_node("GREATER_THAN", index, divisor, 13), 14)
        is_prime = boolean_node("AND", is_prime, boolean_node("NOT", composite, column=14), 15)

    filter_mode = inputs.outputs["Filtre des nombres"]
    non_prime = math_node("COMPARE", filter_mode, 1, 15)
    prime_only = math_node("COMPARE", filter_mode, 2, 15)
    selected = switch("BOOLEAN", non_prime, True, boolean_node("NOT", is_prime, column=15), 16)
    selected = switch("BOOLEAN", prime_only, selected, is_prime, 16)

    store_index = node("GeometryNodeStoreNamedAttribute", "Numero d'origine", 16)
    store_index.data_type = "INT"
    store_index.domain = "POINT"
    store_index.inputs["Name"].default_value = "x_modulo_numero"
    connect(point_geometry, store_index.inputs["Geometry"])
    connect(index, store_index.inputs["Value"])
    store_selected = node("GeometryNodeStoreNamedAttribute", "Points selectionnes", 17)
    store_selected.data_type = "BOOLEAN"
    store_selected.domain = "POINT"
    store_selected.inputs["Name"].default_value = "x_modulo_selection"
    connect(store_index.outputs["Geometry"], store_selected.inputs["Geometry"])
    connect(selected, store_selected.inputs["Value"])
    selected_points = node("GeometryNodeDeleteGeometry", "Filtrer les points", 18)
    selected_points.domain = "POINT"
    connect(store_selected.outputs["Geometry"], selected_points.inputs["Geometry"])
    connect(boolean_node("NOT", selected, column=17), selected_points.inputs["Selection"])
    link_points = switch("GEOMETRY", inputs.outputs["Modulo sur selection"],
                         store_selected.outputs["Geometry"], selected_points.outputs["Geometry"], 19)

    point_size = node("GeometryNodeAttributeDomainSize", "Nombre reel de points", 13)
    point_size.component = "MESH"
    connect(link_points, point_size.inputs["Geometry"])
    actual_count = point_size.outputs["Point Count"]
    divisor_count = int_node("MAXIMUM", actual_count, 1, 14)

    # Un mesh line de 2*N sommets devient N segments independants.
    line = node("GeometryNodeMeshLine", "Paires de sommets", 8)
    connect(int_node("MULTIPLY", actual_count, 2, 14), line.inputs["Count"])
    pair_index = int_node("DIVIDE", index, 2, 8)
    destination = int_node("MODULO", int_node("MULTIPLY", pair_index, inputs.outputs["Table"], 9), divisor_count, 10)
    odd_vertex = int_node("MODULO", index, 2, 9)
    sampled_index = switch("INT", odd_vertex, pair_index, destination, 11)
    sample = node("GeometryNodeSampleIndex", "Position du point cible", 12)
    sample.data_type = "FLOAT_VECTOR"
    sample.domain = "POINT"
    connect(link_points, sample.inputs["Geometry"])
    connect(node("GeometryNodeInputPosition", "Position", 11).outputs["Position"], sample.inputs["Value"])
    connect(sampled_index, sample.inputs["Index"])
    line_positions = node("GeometryNodeSetPosition", "Extremites des liens", 13)
    connect(line.outputs["Mesh"], line_positions.inputs["Geometry"])
    connect(sample.outputs["Value"], line_positions.inputs["Position"])
    delete_edges = node("GeometryNodeDeleteGeometry", "Separer les liens", 14)
    delete_edges.domain = "EDGE"
    connect(line_positions.outputs["Geometry"], delete_edges.inputs["Geometry"])
    connect(int_node("MODULO", index, 2, 13), delete_edges.inputs["Selection"])
    delete_first = node("GeometryNodeDeleteGeometry", "Sans lien depuis le point 0", 15)
    delete_first.domain = "POINT"
    connect(delete_edges.outputs["Geometry"], delete_first.inputs["Geometry"])
    selected_attribute = node("GeometryNodeInputNamedAttribute", "Selection d'origine", 14)
    selected_attribute.data_type = "BOOLEAN"
    selected_attribute.inputs["Name"].default_value = "x_modulo_selection"

    def sample_selection(point_index):
        result = node("GeometryNodeSampleIndex", "Extremite selectionnee", 15)
        result.data_type = "BOOLEAN"
        result.domain = "POINT"
        connect(link_points, result.inputs["Geometry"])
        connect(selected_attribute.outputs["Attribute"], result.inputs["Value"])
        connect(point_index, result.inputs["Index"])
        return result.outputs["Value"]

    both_selected = boolean_node("AND", sample_selection(pair_index), sample_selection(destination), 16)
    delete_link = boolean_node("OR", math_node("LESS_THAN", index, 2, 14),
                               boolean_node("NOT", both_selected, column=16), 17)
    connect(delete_link, delete_first.inputs["Selection"])
    to_curve = node("GeometryNodeMeshToCurve", "Segments en courbes", 16)
    connect(delete_first.outputs["Geometry"], to_curve.inputs["Mesh"])
    profile = node("GeometryNodeCurvePrimitiveCircle", "Profil des liens", 16)
    profile.inputs["Resolution"].default_value = 6
    connect(inputs.outputs["Rayon des liens"], profile.inputs["Radius"])
    tubes = node("GeometryNodeCurveToMesh", "Liens", 17)
    connect(to_curve.outputs["Curve"], tubes.inputs["Curve"])
    connect(profile.outputs["Curve"], tubes.inputs["Profile Curve"])
    tubes.inputs["Fill Caps"].default_value = True

    dot = node("GeometryNodeMeshIcoSphere", "Point visible", 13)
    dot.inputs["Subdivisions"].default_value = 1
    connect(inputs.outputs["Rayon des points"], dot.inputs["Radius"])
    instances = node("GeometryNodeInstanceOnPoints", "Points visibles", 14)
    connect(selected_points.outputs["Geometry"], instances.inputs["Points"])
    connect(dot.outputs["Mesh"], instances.inputs["Instance"])
    realized = node("GeometryNodeRealizeInstances", "Maillage des points", 15)
    connect(instances.outputs["Instances"], realized.inputs["Geometry"])

    foreach_in = node("GeometryNodeForeachGeometryElementInput", "Numeros par point", 19)
    foreach_out = node("GeometryNodeForeachGeometryElementOutput", "Numeros generes", 23)
    foreach_in.pair_with_output(foreach_out)
    foreach_out.domain = "POINT"
    foreach_out.input_items.new("INT", "Numero")
    foreach_out.input_items.new("VECTOR", "Position")
    connect(selected_points.outputs["Geometry"], foreach_in.inputs["Geometry"])
    number_attribute = node("GeometryNodeInputNamedAttribute", "Lire le numero d'origine", 18)
    number_attribute.data_type = "INT"
    number_attribute.inputs["Name"].default_value = "x_modulo_numero"
    connect(number_attribute.outputs["Attribute"], foreach_in.inputs["Numero"])
    connect(node("GeometryNodeInputPosition", "Position du numero", 18).outputs["Position"],
            foreach_in.inputs["Position"])
    number_to_string = node("FunctionNodeValueToString", "Numero en texte", 20)
    number_to_string.data_type = "INT"
    connect(foreach_in.outputs["Numero"], number_to_string.inputs["Value"])
    text = node("GeometryNodeStringToCurves", "Texte du numero", 20)
    connect(number_to_string.outputs["String"], text.inputs["String"])
    connect(inputs.outputs["Taille des numeros"], text.inputs["Size"])
    text_realized = node("GeometryNodeRealizeInstances", "Caracteres", 21)
    connect(text.outputs["Curve Instances"], text_realized.inputs["Geometry"])
    text_mesh = node("GeometryNodeFillCurve", "Surface du texte", 21)
    connect(text_realized.outputs["Geometry"], text_mesh.inputs["Curve"])
    camera_info = node("GeometryNodeObjectInfo", "Camera pour les numeros", 19)
    camera_info.transform_space = "RELATIVE"
    camera_info.inputs["Object"].default_value = bpy.context.scene.camera
    direction = node("ShaderNodeVectorMath", "Vers la camera", 20)
    direction.operation = "SUBTRACT"
    connect(camera_info.outputs["Location"], direction.inputs[0])
    connect(foreach_in.outputs["Position"], direction.inputs[1])
    align = node("FunctionNodeAlignRotationToVector", "Orienter vers la camera", 21)
    align.axis = "Z"
    connect(direction.outputs["Vector"], align.inputs["Vector"])
    text_transform = node("GeometryNodeTransform", "Placer le numero", 22)
    connect(text_mesh.outputs["Mesh"], text_transform.inputs["Geometry"])
    connect(foreach_in.outputs["Position"], text_transform.inputs["Translation"])
    connect(align.outputs["Rotation"], text_transform.inputs["Rotation"])
    connect(text_transform.outputs["Geometry"], foreach_out.inputs["Geometry"])

    visible_lines = switch("GEOMETRY", inputs.outputs["Afficher les liens"], None, tubes.outputs["Mesh"], 18)
    visible_points = switch("GEOMETRY", inputs.outputs["Afficher les points"], None, realized.outputs["Geometry"], 18)
    visible_numbers = switch("GEOMETRY", inputs.outputs["Afficher les numeros"],
                             None, next(s for s in foreach_out.outputs if s.identifier == "Generation_0"), 24)
    join = node("GeometryNodeJoinGeometry", "Resultat", 25)
    connect(visible_lines, join.inputs["Geometry"])
    connect(visible_points, join.inputs["Geometry"])
    connect(visible_numbers, join.inputs["Geometry"])
    outputs.location = (26 * 230, 0)
    connect(join.outputs["Geometry"], outputs.inputs["Geometry"])
    return group


def validate_scene(scene):
    obj = scene.objects.get("Cube")
    if obj is None or obj.type != "MESH":
        raise RuntimeError('Le cube par defaut "Cube" est introuvable ou n\'est pas un maillage.')

    camera = scene.camera
    if camera is None or camera.type != "CAMERA":
        raise RuntimeError("La scene doit posseder une camera active.")
    if camera.parent is not None and not camera.parent.get("x_modulo_turntable"):
        raise RuntimeError("La camera a deja un parent ; detachez-la avant de creer le turntable.")
    if camera.animation_data:
        raise RuntimeError("La camera possede deja une animation ; retirez-la avant de creer le turntable.")
    for constraint in camera.constraints:
        if (constraint.name != "X Modulo - Cible" or constraint.type != "TRACK_TO"
                or not camera.parent or not camera.parent.get("x_modulo_turntable")):
            raise RuntimeError("La camera possede deja des contraintes ; retirez-les avant de creer le turntable.")

    lights = [light for light in scene.objects if light.type == "LIGHT" and light.get("x_modulo_light")]
    light = lights[0] if lights else scene.objects.get("Light")
    if light is not None and light.type != "LIGHT":
        light = None
    if light is not None and (light.parent or light.constraints or light.animation_data):
        raise RuntimeError("La lumiere a un parent, des contraintes ou une animation ; liberez-la avant execution.")
    return obj, camera, light


def replace_modulo_nodes(obj):
    group = create_modulo_nodes()
    old_modifiers = [
        mod for mod in obj.modifiers
        if mod.type == "NODES" and mod.node_group and mod.node_group.get("x_modulo_3d")
    ]
    old_index = list(obj.modifiers).index(old_modifiers[0]) if old_modifiers else len(obj.modifiers)
    old_groups = {mod.node_group for mod in old_modifiers}
    for modifier in old_modifiers:
        obj.modifiers.remove(modifier)
    for old_group in old_groups:
        if old_group.users == 0:
            bpy.data.node_groups.remove(old_group)
    group.name = "X Modulo 3D"
    modifier = obj.modifiers.new(name="X Modulo 3D", type="NODES")
    modifier.node_group = group
    obj.modifiers.move(len(obj.modifiers) - 1, old_index)


def setup_light(scene, obj, light):
    if light is None:
        data = bpy.data.lights.new("X Modulo - Lumiere", type="POINT")
        light = bpy.data.objects.new("X Modulo - Lumiere", data)
        scene.collection.objects.link(light)
    elif light.data.users > 1:
        light.data = light.data.copy()
    light["x_modulo_light"] = True
    light.data.type = "POINT"
    light.data.energy = 10000.0
    matrix = light.matrix_world.copy()
    matrix.translation = obj.matrix_world.translation
    light.matrix_world = matrix


def setup_world(scene):
    if scene.world is None:
        scene.world = bpy.data.worlds.new("X Modulo - World")
    elif scene.world.users > 1:
        scene.world = scene.world.copy()
    world = scene.world
    nodes = world.node_tree.nodes
    background = next((node for node in nodes if node.type == "BACKGROUND" and node.get("x_modulo_world")), None)
    if background is None:
        background = nodes.new("ShaderNodeBackground")
        background.label = "X Modulo - World sans eclairage"
        background["x_modulo_world"] = True
    strength = background.inputs["Strength"]
    for link in list(strength.links):
        world.node_tree.links.remove(link)
    strength.default_value = 0.0
    outputs = [node for node in nodes if node.type == "OUTPUT_WORLD"]
    if not outputs:
        outputs = [nodes.new("ShaderNodeOutputWorld")]
    for output in outputs:
        world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])


def setup_turntable(scene, obj, camera):
    original_frame = scene.frame_current
    original_subframe = scene.frame_subframe
    scene.frame_set(1)
    camera_matrix = camera.matrix_world.copy()
    pivot = camera.parent
    if pivot is None:
        pivot = bpy.data.objects.new("X Modulo - Turntable", None)
        pivot["x_modulo_turntable"] = True
        scene.collection.objects.link(pivot)
    else:
        old_action = pivot.animation_data.action if pivot.animation_data else None
        pivot.animation_data_clear()
        if old_action and old_action.get("x_modulo_turntable") and old_action.users == 0:
            bpy.data.actions.remove(old_action)

    pivot.rotation_mode = "XYZ"
    pivot.rotation_euler = (0.0, 0.0, 0.0)
    pivot.location = obj.matrix_world.translation
    bpy.context.view_layer.update()
    camera.parent = pivot
    camera.matrix_world = camera_matrix

    target = camera.constraints.get("X Modulo - Cible")
    if target is None:
        target = camera.constraints.new("TRACK_TO")
        target.name = "X Modulo - Cible"
    target.target = pivot
    target.track_axis = "TRACK_NEGATIVE_Z"
    target.up_axis = "UP_Y"

    pivot.rotation_euler.z = 0.0
    pivot.keyframe_insert(data_path="rotation_euler", index=2, frame=1)
    pivot.rotation_euler.z = 2.0 * math.pi
    pivot.keyframe_insert(data_path="rotation_euler", index=2, frame=721)
    action = pivot.animation_data.action
    action["x_modulo_turntable"] = True
    channelbag = action.layers[0].strips[0].channelbag(pivot.animation_data.action_slot)
    curve = channelbag.fcurves.find("rotation_euler", index=2)
    for key in curve.keyframe_points:
        key.interpolation = "LINEAR"
    curve.modifiers.new("CYCLES")

    scene.render.fps = 24
    scene.render.fps_base = 1.0
    scene.frame_start = 1
    scene.frame_end = 720
    scene.frame_set(original_frame, subframe=original_subframe)


def main():
    scene = bpy.context.scene
    obj, camera, light = validate_scene(scene)
    replace_modulo_nodes(obj)
    setup_light(scene, obj, light)
    setup_world(scene)
    setup_turntable(scene, obj, camera)


if __name__ == "__main__":
    main()
