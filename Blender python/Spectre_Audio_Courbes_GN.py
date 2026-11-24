import math
import os

import aud
import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


# Spectre audio en courbes - Blender 5.3+
#
# Executer le script dans l'editeur de texte et choisir un MP3.
# Le modificateur analyse le son directement avec Sample Sound Frequencies.
# X : 1 a 128 bandes logarithmiques de 20 Hz a 20 kHz ; une seule bande
# couvre toutes les frequences. Y : historique ; Z : amplitude.
# Les courbes relient les bandes et les instants dans les deux directions.
#
# Le parametre Son permet de choisir un autre son charge dans Blender.
# Changer aussi la piste du Sequenceur et la fin de la timeline pour ecouter
# ce nouveau son ; le debut reste l'image de debut lors de la creation.
# Chaque execution ajoute un objet et une piste sonore. Les pistes existantes
# peuvent se melanger a la nouvelle piste. Le fichier audio reste externe.
# Une FFT de 32768 echantillons est utilisee pour les basses frequences.

BANDS = 32
MIN_FREQUENCY = 20.0
MAX_FREQUENCY = 20000.0
HISTORY_FRAMES = 100
SPACING = 0.4
AMPLITUDE_SCALE = 12.0
CURVE_RADIUS = 0.025


def make_node_group(start_frame, fps, sound):
    group = bpy.data.node_groups.new("Spectre audio - courbes", "GeometryNodeTree")

    def socket(name, direction, socket_type, default=None, minimum=None, maximum=None,
               description=""):
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
    socket("Son", "INPUT", "NodeSocketSound", sound,
           description="Son analyse ; changer aussi la piste du Sequenceur pour l'ecouter")
    socket("Nombre de bandes", "INPUT", "NodeSocketInt", BANDS, 1, 128,
           "1 : tout le spectre ; 2 a 128 : bandes logarithmiques de 20 Hz a 20 kHz")
    socket("Historique en images", "INPUT", "NodeSocketInt", HISTORY_FRAMES, 1, 1000)
    socket("Espacement des frequences", "INPUT", "NodeSocketFloat", SPACING, 0.001, 100)
    socket("Espacement du temps", "INPUT", "NodeSocketFloat", SPACING, 0.001, 100)
    socket("Gain amplitude", "INPUT", "NodeSocketFloat", AMPLITUDE_SCALE, 0.0, 10000)
    socket("Rayon des courbes", "INPUT", "NodeSocketFloat", CURVE_RADIUS, 0.0001, 10)
    socket("Courbes de frequences", "INPUT", "NodeSocketBool", True)
    socket("Courbes de temps", "INPUT", "NodeSocketBool", True)
    socket("Lisser les courbes", "INPUT", "NodeSocketBool", True)
    socket("Resolution du lissage", "INPUT", "NodeSocketInt", 4, 1, 32,
           "Plus la resolution est elevee, plus la geometrie est dense")
    socket("Materiau", "INPUT", "NodeSocketMaterial")

    nodes = group.nodes
    links = group.links

    def node(node_type, label, x, y):
        result = nodes.new(node_type)
        result.label = label
        result.location = (x, y)
        return result

    def connect(value, target):
        if isinstance(value, bpy.types.NodeSocket):
            links.new(value, target)
        else:
            target.default_value = value

    def math_node(operation, first, second, x, y):
        result = node("ShaderNodeMath", operation, x, y)
        result.operation = operation
        connect(first, result.inputs[0])
        connect(second, result.inputs[1])
        return result.outputs[0]

    def int_node(operation, first, second, x, y):
        result = node("FunctionNodeIntegerMath", operation, x, y)
        result.operation = operation
        connect(first, result.inputs[0])
        connect(second, result.inputs[1])
        return result.outputs[0]

    def bool_node(operation, first, second, x, y):
        result = node("FunctionNodeBooleanMath", operation, x, y)
        result.operation = operation
        connect(first, result.inputs[0])
        if second is not None:
            connect(second, result.inputs[1])
        return result.outputs[0]

    def switch(data_type, condition, false_value, true_value, x, y):
        result = node("GeometryNodeSwitch", "Choix", x, y)
        result.input_type = data_type
        connect(condition, result.inputs["Switch"])
        if false_value is not None:
            connect(false_value, result.inputs["False"])
        if true_value is not None:
            connect(true_value, result.inputs["True"])
        return result.outputs["Output"]

    def store_int(geometry, name, value, x, y):
        result = node("GeometryNodeStoreNamedAttribute", name, x, y)
        result.data_type = "INT"
        result.domain = "POINT"
        result.inputs["Name"].default_value = name
        connect(geometry, result.inputs["Geometry"])
        connect(value, result.inputs["Value"])
        return result.outputs["Geometry"]

    def read_int(name, x, y):
        result = node("GeometryNodeInputNamedAttribute", name, x, y)
        result.data_type = "INT"
        result.inputs["Name"].default_value = name
        return result.outputs["Attribute"]

    inputs = node("NodeGroupInput", "Reglages", -1600, 500)
    output = node("NodeGroupOutput", "Spectre", 2800, 500)
    band_count = inputs.outputs["Nombre de bandes"]
    history = inputs.outputs["Historique en images"]
    width = int_node("MAXIMUM", band_count, 2, -1400, 800)
    rows = int_node("MAXIMUM", history, 2, -1400, 600)
    grid = node("GeometryNodeMeshGrid", "Grille des bandes et du temps", -1200, 800)
    connect(width, grid.inputs["Vertices X"])
    connect(rows, grid.inputs["Vertices Y"])
    index = node("GeometryNodeInputIndex", "Index de la grille", -1600, 0).outputs["Index"]
    band = int_node("DIVIDE", index, rows, -1400, 0)
    age = int_node("MODULO", index, rows, -1400, -200)
    grid_with_band = store_int(grid.outputs["Mesh"], "audio_band", band, -1000, 800)
    grid_with_age = store_int(grid_with_band, "audio_age", age, -800, 800)

    time = node("GeometryNodeInputSceneTime", "Image actuelle", -1600, -500)
    elapsed = math_node("SUBTRACT", time.outputs["Frame"], start_frame, -1400, -500)
    too_many_bands = math_node("GREATER_THAN", band,
                               int_node("SUBTRACT", band_count, 1, -1200, -200),
                               -1000, -100)
    too_many_rows = math_node("GREATER_THAN", age,
                              int_node("SUBTRACT", history, 1, -1200, -400),
                              -1000, -300)
    before_start = math_node("GREATER_THAN", age, elapsed, -1000, -500)
    discard = bool_node(
        "OR", too_many_bands,
        bool_node("OR", too_many_rows, before_start, -800, -350), -600, -200
    )
    delete = node("GeometryNodeDeleteGeometry", "Grille disponible", -400, 800)
    delete.domain = "POINT"
    connect(grid_with_age, delete.inputs["Geometry"])
    connect(discard, delete.inputs["Selection"])

    current_band = read_int("audio_band", -600, -800)
    current_age = read_int("audio_age", -600, -1000)
    seconds_per_frame = math_node("DIVIDE", time.outputs["Seconds"], time.outputs["Frame"],
                                  -1200, -800)
    frame_is_zero = math_node("COMPARE", time.outputs["Frame"], 0.0, -1200, -1000)
    seconds_per_frame = switch(
        "FLOAT", frame_is_zero, seconds_per_frame, 1.0 / fps, -1000, -800
    )
    sample_frame = math_node("SUBTRACT", elapsed, current_age, -400, -1000)
    sample_time = math_node("MULTIPLY", sample_frame, seconds_per_frame, -200, -1000)
    fraction_low = math_node("DIVIDE", current_band, band_count, -400, -1200)
    fraction_high = math_node("DIVIDE", int_node("ADD", current_band, 1, -400, -1400),
                              band_count, -200, -1400)
    ratio = MAX_FREQUENCY / MIN_FREQUENCY
    low = math_node("MULTIPLY", MIN_FREQUENCY,
                    math_node("POWER", ratio, fraction_low, -200, -1200), 0, -1200)
    high = math_node("MULTIPLY", MIN_FREQUENCY,
                     math_node("POWER", ratio, fraction_high, 0, -1400), 200, -1400)
    single_band = math_node("LESS_THAN", band_count, 2, -200, -1600)
    low = switch("FLOAT", single_band, low, 0.0, 200, -1200)
    high = switch("FLOAT", single_band, high, 1_000_000_000.0, 400, -1400)
    sample = node("GeometryNodeSampleSoundFrequencies", "Amplitude audio", 400, -1000)
    sample.inputs["FFT Size"].default_value = "32768"
    connect(inputs.outputs["Son"], sample.inputs["Sound"])
    connect(sample_time, sample.inputs["Time"])
    connect(low, sample.inputs["Low"])
    connect(high, sample.inputs["High"])

    position = node("ShaderNodeCombineXYZ", "Frequence / temps / amplitude", 600, -500)
    connect(math_node("MULTIPLY", current_band, inputs.outputs["Espacement des frequences"],
                      200, -500), position.inputs["X"])
    connect(math_node("MULTIPLY", current_age, inputs.outputs["Espacement du temps"],
                      200, -700), position.inputs["Y"])
    connect(math_node("MULTIPLY", sample.outputs["Amplitude"],
                      inputs.outputs["Gain amplitude"], 600, -1000), position.inputs["Z"])
    moved = node("GeometryNodeSetPosition", "Grille deformee", 800, 800)
    connect(delete.outputs["Geometry"], moved.inputs["Geometry"])
    connect(position.outputs["Vector"], moved.inputs["Position"])

    # Separate edges by their original band, then make independent spline families.
    endpoints = node("GeometryNodeInputMeshEdgeVertices", "Extremites des aretes", 800, 100)
    def band_at_index(index_socket, x, y):
        field = node("GeometryNodeFieldAtIndex", "Bande du sommet", x, y)
        field.data_type = "INT"
        field.domain = "POINT"
        connect(index_socket, field.inputs["Index"])
        connect(current_band, field.inputs["Value"])
        return field.outputs["Value"]

    first_band = band_at_index(endpoints.outputs["Vertex Index 1"], 1000, 100)
    second_band = band_at_index(endpoints.outputs["Vertex Index 2"], 1000, -100)
    same_band = math_node("COMPARE", first_band, second_band, 1200, 0)
    freq_selection = bool_node("NOT", same_band, None, 1400, 0)
    frequency_curves = node("GeometryNodeMeshToCurve", "Courbes de frequences", 1600, 800)
    connect(moved.outputs["Geometry"], frequency_curves.inputs["Mesh"])
    connect(freq_selection, frequency_curves.inputs["Selection"])
    time_curves = node("GeometryNodeMeshToCurve", "Courbes de temps", 1600, 400)
    connect(moved.outputs["Geometry"], time_curves.inputs["Mesh"])
    connect(same_band, time_curves.inputs["Selection"])

    def smooth_curve(curve, x, y):
        bezier = node("GeometryNodeCurveSplineType", "Bezier", x, y)
        bezier.spline_type = "BEZIER"
        connect(curve, bezier.inputs["Curve"])
        handles = node("GeometryNodeCurveSetHandles", "Poignees automatiques", x + 200, y)
        handles.handle_type = "AUTO"
        connect(bezier.outputs["Curve"], handles.inputs["Curve"])
        resolution = node("GeometryNodeSetSplineResolution", "Resolution du lissage",
                          x + 400, y)
        connect(handles.outputs["Curve"], resolution.inputs["Curve"])
        connect(inputs.outputs["Resolution du lissage"], resolution.inputs["Resolution"])
        return switch("GEOMETRY", inputs.outputs["Lisser les courbes"],
                      curve, resolution.outputs["Curve"], x + 600, y)

    freq = smooth_curve(frequency_curves.outputs["Curve"], 1800, 800)
    temporal = smooth_curve(time_curves.outputs["Curve"], 1800, 400)
    freq = switch("GEOMETRY", inputs.outputs["Courbes de frequences"], None, freq, 2400, 800)
    temporal = switch("GEOMETRY", inputs.outputs["Courbes de temps"], None, temporal, 2400, 400)
    curves = node("GeometryNodeJoinGeometry", "Courbes dans les deux directions", 2600, 600)
    connect(freq, curves.inputs["Geometry"])
    connect(temporal, curves.inputs["Geometry"])
    profile = node("GeometryNodeCurvePrimitiveCircle", "Section des courbes", 2400, 0)
    profile.inputs["Resolution"].default_value = 8
    connect(inputs.outputs["Rayon des courbes"], profile.inputs["Radius"])
    tube = node("GeometryNodeCurveToMesh", "Courbes visibles au rendu", 2800, 600)
    tube.inputs["Fill Caps"].default_value = True
    connect(curves.outputs["Geometry"], tube.inputs["Curve"])
    connect(profile.outputs["Curve"], tube.inputs["Profile Curve"])

    # A single point has no edge to turn into a curve.
    domain = node("GeometryNodeAttributeDomainSize", "Nombre de points", 1400, -400)
    domain.component = "MESH"
    connect(moved.outputs["Geometry"], domain.inputs["Geometry"])
    one_point = math_node("COMPARE", domain.outputs["Point Count"], 1, 1600, -400)
    show_any = bool_node("OR", inputs.outputs["Courbes de frequences"],
                         inputs.outputs["Courbes de temps"], 1600, -600)
    show_point = bool_node("AND", one_point, show_any, 1800, -400)
    sphere = node("GeometryNodeMeshIcoSphere", "Point isole", 1800, -800)
    sphere.inputs["Subdivisions"].default_value = 2
    connect(inputs.outputs["Rayon des courbes"], sphere.inputs["Radius"])
    point_instance = node("GeometryNodeInstanceOnPoints", "Afficher le point isole",
                          2000, -400)
    connect(moved.outputs["Geometry"], point_instance.inputs["Points"])
    connect(show_point, point_instance.inputs["Selection"])
    connect(sphere.outputs["Mesh"], point_instance.inputs["Instance"])
    realized = node("GeometryNodeRealizeInstances", "Realiser le point", 2200, -400)
    connect(point_instance.outputs["Instances"], realized.inputs["Geometry"])
    join = node("GeometryNodeJoinGeometry", "Courbes et point", 3000, 600)
    connect(tube.outputs["Mesh"], join.inputs["Geometry"])
    connect(realized.outputs["Geometry"], join.inputs["Geometry"])
    material = node("GeometryNodeSetMaterial", "Materiau", 3200, 600)
    connect(join.outputs["Geometry"], material.inputs["Geometry"])
    connect(inputs.outputs["Materiau"], material.inputs["Material"])
    connect(material.outputs["Geometry"], output.inputs["Geometry"])
    return group


def create_spectrum(context, filepath):
    scene = context.scene
    start_frame = scene.frame_start
    fps = scene.render.fps / scene.render.fps_base
    if not os.path.isfile(filepath):
        raise FileNotFoundError("Fichier audio introuvable : " + filepath)
    if fps <= 0:
        raise ValueError("La cadence de la scene doit etre positive.")
    source = aud.Sound.file(filepath)
    rate, channels = source.specs
    sample_count = source.length
    if rate <= 0 or channels <= 0 or sample_count <= 0:
        raise ValueError("Le fichier audio ne contient aucun echantillon exploitable.")
    end_frame = start_frame + math.ceil(sample_count * fps / rate) - 1
    if end_frame > 1_048_574:
        raise ValueError("Le spectre depasse la limite de la timeline de Blender.")

    editor = scene.sequence_editor
    channel = max((strip.channel for strip in editor.strips), default=0) + 1 if editor else 1
    if channel > 128:
        raise ValueError("Aucune piste libre pour le son dans le Sequenceur.")
    editor = scene.sequence_editor_create()
    strip = editor.strips.new_sound("Spectre audio courbes", filepath, channel, start_frame)
    if strip.sound is None:
        raise RuntimeError("Blender n'a pas pu charger le son.")

    mesh = bpy.data.meshes.new("Support spectre audio courbes")
    obj = bpy.data.objects.new("Spectre audio courbes", mesh)
    context.collection.objects.link(obj)
    modifier = obj.modifiers.new("Spectre audio courbes", "NODES")
    modifier.node_group = make_node_group(start_frame, fps, strip.sound)
    scene.frame_end = end_frame
    scene.frame_set(start_frame)
    context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


class OBJECT_OT_create_audio_curve_spectrum(bpy.types.Operator, ImportHelper):
    bl_idname = "object.create_audio_curve_spectrum"
    bl_label = "Creer un spectre audio en courbes"
    bl_description = "Choisir un fichier MP3 et creer son spectre en courbes"

    filename_ext = ".mp3"
    filter_glob: StringProperty(default="*.mp3", options={"HIDDEN"})

    def execute(self, context):
        try:
            obj = create_spectrum(context, self.filepath)
        except (aud.error, OSError, ValueError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        self.report({"INFO"}, "Spectre en courbes cree : " + obj.name)
        return {"FINISHED"}


def register():
    if bpy.app.version < (5, 3, 0):
        raise RuntimeError("Ce script necessite Blender 5.3 ou une version plus recente.")
    previous = getattr(bpy.types, OBJECT_OT_create_audio_curve_spectrum.__name__, None)
    if previous is not None:
        bpy.utils.unregister_class(previous)
    bpy.utils.register_class(OBJECT_OT_create_audio_curve_spectrum)


if __name__ == "__main__":
    register()
    bpy.ops.object.create_audio_curve_spectrum("INVOKE_DEFAULT")
