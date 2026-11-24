import math
import os

import aud
import bpy
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


# Spectre audio 3D - Blender 5.3+
#
# Dans l'editeur de texte de Blender, executer le script et choisir un MP3.
# Le noeud Sample Sound Frequencies analyse le son directement dans Blender.
# Aucun precalcul Python ni cache de simulation n'est necessaire.
#
# X : 1 a 128 bandes logarithmiques, de 20 Hz a 20 kHz ; une seule bande
# couvre toutes les frequences du son.
# Y : historique ; la ligne la plus recente est a Y = 0.
# Z : amplitude des bandes, multipliable dans le modificateur.
#
# Un objet et une piste sonore sont ajoutes a la scene. La plage
# de lecture est adaptee a la duree du fichier, sans changer les images/seconde.
# Le parametre "Son" du modificateur permet de changer le son analyse.
# Il ne modifie pas la piste du Sequenceur ni la fin de la timeline : les
# ajuster manuellement pour entendre le nouveau son en synchronisation.
# Le debut du spectre reste a l'image de debut de la scene lors de sa creation.
# Le MP3 reste externe : conserver le fichier ou l'empaqueter dans le .blend.
# Chaque execution ajoute un nouveau spectre et une nouvelle piste sonore.
# Des pistes sonores existantes peuvent donc se melanger au nouveau MP3.
# Pour un objet personnalise, choisir l'objet et activer "Utiliser objet".
# Les objets remplacant les cubes doivent etre centres a l'origine et avoir
# des dimensions de reference 1 x 1 x 1 ; leur echelle est appliquee par GN.
# Une FFT de 32768 echantillons est utilisee pour distinguer les frequences
# basses ; elle peut rendre le premier calcul et la lecture plus lents.

BANDS = 32
MIN_FREQUENCY = 20.0
MAX_FREQUENCY = 20000.0
HISTORY_FRAMES = 100
BAR_SPACING = 0.4
BAR_WIDTH = 0.3
AMPLITUDE_SCALE = 12.0


def make_node_group(start_frame, fps, sound):
    group = bpy.data.node_groups.new("Spectre audio 3D", "GeometryNodeTree")

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
    socket("Espacement des frequences", "INPUT", "NodeSocketFloat", BAR_SPACING, 0.001, 100)
    socket("Espacement du temps", "INPUT", "NodeSocketFloat", BAR_SPACING, 0.001, 100)
    socket("Largeur des barres", "INPUT", "NodeSocketFloat", BAR_WIDTH, 0.001, 100)
    socket("Profondeur des barres", "INPUT", "NodeSocketFloat", BAR_WIDTH, 0.001, 100)
    socket("Gain amplitude", "INPUT", "NodeSocketFloat", AMPLITUDE_SCALE, 0.0, 10000)
    socket("Utiliser objet", "INPUT", "NodeSocketBool", False,
           description="Active le remplacement des cubes par l'objet choisi")
    socket("Objet", "INPUT", "NodeSocketObject",
           description="Objet centre a l'origine, de dimensions de reference 1 x 1 x 1")
    socket("Materiau", "INPUT", "NodeSocketMaterial",
           description="Materiau applique aux cubes par defaut")

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

    def switch(condition, false_value, true_value, x, y):
        result = node("GeometryNodeSwitch", "Choix", x, y)
        result.input_type = "FLOAT"
        connect(condition, result.inputs["Switch"])
        connect(false_value, result.inputs["False"])
        connect(true_value, result.inputs["True"])
        return result.outputs["Output"]

    inputs = node("NodeGroupInput", "Reglages", -1000, 300)
    output = node("NodeGroupOutput", "Spectre", 1400, 300)
    band_count = inputs.outputs["Nombre de bandes"]
    point_count = int_node("MULTIPLY", band_count, inputs.outputs["Historique en images"],
                           -800, 900)
    points = node("GeometryNodeMeshLine", "Bandes et historique", -600, 900)
    points.inputs["Offset"].default_value = (0.0, 0.0, 0.0)
    connect(point_count, points.inputs["Count"])
    index = node("GeometryNodeInputIndex", "Index du point", -1000, 0).outputs["Index"]
    band = int_node("MODULO", index, band_count, -800, 0)
    age = int_node("DIVIDE", index, band_count, -800, -200)

    time = node("GeometryNodeInputSceneTime", "Image actuelle", -1000, -400)
    elapsed = math_node("SUBTRACT", time.outputs["Frame"], start_frame, -800, -400)
    seconds_per_frame = math_node("DIVIDE", time.outputs["Seconds"], time.outputs["Frame"],
                                  -800, -600)
    frame_is_zero = math_node("COMPARE", time.outputs["Frame"], 0.0, -800, -800)
    seconds_per_frame = switch(frame_is_zero, seconds_per_frame, 1.0 / fps, -600, -600)
    sample_frame = math_node("SUBTRACT", elapsed, age, -600, -400)
    sample_time = math_node("MULTIPLY", sample_frame, seconds_per_frame, -400, -400)

    fraction_low = math_node("DIVIDE", band, band_count, -800, -1100)
    fraction_high = math_node("DIVIDE", int_node("ADD", band, 1, -800, -1300),
                              band_count, -600, -1300)
    ratio = MAX_FREQUENCY / MIN_FREQUENCY
    low = math_node("MULTIPLY", MIN_FREQUENCY,
                    math_node("POWER", ratio, fraction_low, -600, -1100), -400, -1100)
    high = math_node("MULTIPLY", MIN_FREQUENCY,
                     math_node("POWER", ratio, fraction_high, -400, -1300), -200, -1300)
    single_band = math_node("LESS_THAN", band_count, 2, -600, -1500)
    low = switch(single_band, low, 0.0, -200, -1100)
    high = switch(single_band, high, 1_000_000_000.0, 0, -1300)
    sample = node("GeometryNodeSampleSoundFrequencies", "Amplitude audio", 0, -400)
    sample.inputs["FFT Size"].default_value = "32768"
    connect(inputs.outputs["Son"], sample.inputs["Sound"])
    connect(sample_time, sample.inputs["Time"])
    connect(low, sample.inputs["Low"])
    connect(high, sample.inputs["High"])

    x = math_node("MULTIPLY", band, inputs.outputs["Espacement des frequences"], -200, -800)
    y = math_node("MULTIPLY", age, inputs.outputs["Espacement du temps"], 0, -800)
    height = math_node("MULTIPLY", sample.outputs["Amplitude"],
                       inputs.outputs["Gain amplitude"], 0, -1000)
    store_age = node("GeometryNodeStoreNamedAttribute", "Memoriser l'age", 0, 700)
    store_age.data_type = "INT"
    store_age.domain = "POINT"
    store_age.inputs["Name"].default_value = "audio_age"
    connect(points.outputs["Mesh"], store_age.inputs["Geometry"])
    connect(age, store_age.inputs["Value"])
    store_height = node("GeometryNodeStoreNamedAttribute", "Memoriser la hauteur",
                        200, 400)
    store_height.data_type = "FLOAT"
    store_height.domain = "POINT"
    store_height.inputs["Name"].default_value = "audio_height"
    connect(store_age.outputs["Geometry"], store_height.inputs["Geometry"])
    connect(height, store_height.inputs["Value"])
    half_height = math_node("MULTIPLY", height, 0.5, 200, -1000)
    coords = node("ShaderNodeCombineXYZ", "Placer les barres", 400, -600)
    connect(x, coords.inputs["X"])
    connect(y, coords.inputs["Y"])
    connect(half_height, coords.inputs["Z"])
    moved = node("GeometryNodeSetPosition", "Grille visible", 400, 400)
    connect(store_height.outputs["Geometry"], moved.inputs["Geometry"])
    connect(coords.outputs["Vector"], moved.inputs["Position"])

    size = node("ShaderNodeCombineXYZ", "Dimensions des barres", 400, -300)
    connect(inputs.outputs["Largeur des barres"], size.inputs["X"])
    connect(inputs.outputs["Profondeur des barres"], size.inputs["Y"])
    stored_height = node("GeometryNodeInputNamedAttribute", "Hauteur memorisee", 400, -1100)
    stored_height.data_type = "FLOAT"
    stored_height.inputs["Name"].default_value = "audio_height"
    connect(stored_height.outputs["Attribute"], size.inputs["Z"])
    cube = node("GeometryNodeMeshCube", "Cube de base", 0, 100)
    material = node("GeometryNodeSetMaterial", "Materiau des cubes", 200, 100)
    connect(cube.outputs["Mesh"], material.inputs["Geometry"])
    connect(inputs.outputs["Materiau"], material.inputs["Material"])
    object_info = node("GeometryNodeObjectInfo", "Objet personnalise", 0, -100)
    object_info.transform_space = "ORIGINAL"
    connect(inputs.outputs["Objet"], object_info.inputs["Object"])
    choose = node("GeometryNodeSwitch", "Choix de l'objet", 400, 100)
    choose.input_type = "GEOMETRY"
    connect(inputs.outputs["Utiliser objet"], choose.inputs["Switch"])
    connect(material.outputs["Geometry"], choose.inputs["False"])
    connect(object_info.outputs["Geometry"], choose.inputs["True"])
    instances = node("GeometryNodeInstanceOnPoints", "Barres du spectre", 800, 400)
    connect(moved.outputs["Geometry"], instances.inputs["Points"])
    stored_age = node("GeometryNodeInputNamedAttribute", "Age memorise", 400, -1450)
    stored_age.data_type = "INT"
    stored_age.inputs["Name"].default_value = "audio_age"
    outside = math_node("GREATER_THAN", stored_age.outputs["Attribute"], elapsed, 600, -1450)
    selection = node("FunctionNodeBooleanMath", "Depuis le debut du son", 800, -1450)
    selection.operation = "NOT"
    connect(outside, selection.inputs[0])
    connect(selection.outputs[0], instances.inputs["Selection"])
    connect(choose.outputs["Output"], instances.inputs["Instance"])
    connect(size.outputs["Vector"], instances.inputs["Scale"])
    connect(instances.outputs["Instances"], output.inputs["Geometry"])
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
    frame_count = math.ceil(sample_count * fps / rate)
    end_frame = start_frame + frame_count - 1
    if end_frame > 1_048_574:
        raise ValueError("Le spectre depasse la limite de la timeline de Blender.")

    editor = scene.sequence_editor
    channel = max((strip.channel for strip in editor.strips), default=0) + 1 if editor else 1
    if channel > 128:
        raise ValueError("Aucune piste libre pour le son dans le Sequenceur.")

    editor = scene.sequence_editor_create()
    strip = editor.strips.new_sound("Spectre audio", filepath, channel, start_frame)
    sound = strip.sound
    if sound is None:
        raise RuntimeError("Blender n'a pas pu charger le son.")
    mesh = bpy.data.meshes.new("Support spectre audio")
    obj = bpy.data.objects.new("Spectre audio 3D", mesh)
    context.collection.objects.link(obj)
    group = make_node_group(start_frame, fps, sound)
    modifier = obj.modifiers.new("Spectre audio", "NODES")
    modifier.node_group = group

    scene.frame_end = end_frame
    scene.frame_set(start_frame)
    context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


class OBJECT_OT_create_audio_spectrum(bpy.types.Operator, ImportHelper):
    bl_idname = "object.create_audio_spectrum"
    bl_label = "Creer un spectre audio 3D"
    bl_description = "Choisir un fichier MP3 et creer son spectre Geometry Nodes"

    filename_ext = ".mp3"
    filter_glob: StringProperty(default="*.mp3", options={"HIDDEN"})

    def execute(self, context):
        try:
            obj = create_spectrum(context, self.filepath)
        except (aud.error, OSError, ValueError, RuntimeError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        self.report({"INFO"}, "Spectre cree : " + obj.name)
        return {"FINISHED"}


def register():
    if bpy.app.version < (5, 3, 0):
        raise RuntimeError("Ce script necessite Blender 5.3 ou une version plus recente.")
    previous = getattr(bpy.types, OBJECT_OT_create_audio_spectrum.__name__, None)
    if previous is not None:
        bpy.utils.unregister_class(previous)
    bpy.utils.register_class(OBJECT_OT_create_audio_spectrum)


if __name__ == "__main__":
    register()
    bpy.ops.object.create_audio_spectrum("INVOKE_DEFAULT")
