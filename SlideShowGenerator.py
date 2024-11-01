"""
slideShowGenerator

Generates a video slide show with a folder of pictures

Author   : Patochun (Patrick M)
Mail     : ptkmgr@gmail.com
YT : https://www.youtube.com/channel/UCCNXecgdUbUChEyvW3gFWvw
Create   : 2024-10-13
Version  : 4.0
Compatibility : DaVinci Resolve v19

Licence used : Creative Commons CC BY
Check licence here : https://creativecommons.org

Usage :
    python slideShowGenerator.py [folder] [displayTime] [travelTime] [resolution]
    
    folder => the folder where are the jpeg images
        Default value = C:\Temp
    displayTime => the time slideshow freeze on each image
        Default value = 5
    travelTime => the time the slideshow travel between two images
        Default value = 5
    resolution => two value
                    HD => 1920*1080
                    UHD => 3840*2160
        Default value = HD
                    
    ex : slideShowGenerator.py "C:\temp\picturesSample" 10 5 HD
"""

import sys
import random
import os
import numpy as np

# Global Variable
# Dirty coding to avoid the use of class instead of mutable string in function capability
curText = "global"
curLayer = "global"

# Template definitions
# @xxxx@ are variables
# Separator "," between template will set by function
templateStart = """
{
    Tools = ordered() {
"""

templateEnd = """
    },
    ActiveTool = "MediaOut1"
}
"""

templatePaper = """
        @Name@ = GroupOperator {
            Inputs = ordered() {
                Input1 = InstanceInput {
                    SourceOp = "PaperFastNoise3",
                    Source = "Seethe",
                    Name = "Texture Seethe",
                    Default = -1.543,
                },
                Input2 = InstanceInput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Gain",
                    Default = 0.84,
                },
                Input3 = InstanceInput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Lift",
                    Default = 0,
                },
                Input4 = InstanceInput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Gamma",
                    Default = 1,
                },
                Input5 = InstanceInput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Contrast",
                    Default = 0.57,
                },
                Input6 = InstanceInput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Brightness",
                    Default = 0.06,
                },
                Input7 = InstanceInput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Saturation",
                    Default = 0.66,
                }
            },
            Outputs = {
                MainOutput1 = InstanceOutput {
                    SourceOp = "PaperBrightnessContrast",
                    Source = "Output",
                }
            },
            ViewInfo = GroupInfo {
                Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ },
                Flags = {
                    AllowPan = false,
                    AutoSnap = true,
                    RemoveRouters = true
                },
                Size = { 244.687, 195.886, 122.343, 24.2424 },
                Direction = "Horizontal",
                PipeStyle = "Direct",
                Scale = 1,
                Offset = { 0, 0 }
            },
            Tools = ordered() {
                PaperFastNoise1 = FastNoise {
                    CtrlWShown = false,
                    Inputs = {
                        GlobalOut = Input { Value = 149, },
                        Width = Input { Value = @BGWidth@, },
                        Height = Input { Value = @BGHeight@, },
                        ["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
                        Detail = Input { Value = 10, },
                        Color1Red = Input { Value = 0.89, },
                        Color1Green = Input { Value = 0.86010312, },
                        Color1Blue = Input { Value = 0.67017, },
                        Color1Alpha = Input { Value = 1, },
                        Color2Red = Input { Value = 0.913, },
                        Color2Green = Input { Value = 0.733380032, },
                        Color2Blue = Input { Value = 0.489368, }
                    },
                    ViewInfo = OperatorInfo { Pos = { -58.8183, 7.99655 } },
                },
                PaperFastNoise2 = FastNoise {
                    CtrlWShown = false,
                    Inputs = {
                        GlobalOut = Input { Value = 149, },
                        Width = Input { Value = @BGWidth@, },
                        Height = Input { Value = @BGHeight@, },
                        ["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
                        Detail = Input { Value = 10, },
                        XScale = Input { Value = 1000, },
                        Color1Red = Input { Value = 0.992, },
                        Color1Green = Input { Value = 0.992, },
                        Color1Blue = Input { Value = 0.992, },
                        Color1Alpha = Input { Value = 1, },
                        Color2Red = Input { Value = 0.929, },
                        Color2Green = Input { Value = 0.81280068, },
                        Color2Blue = Input { Value = 0.654945, }
                    },
                    ViewInfo = OperatorInfo { Pos = { -58.8183, 40.9966 } },
                },
                ChannelBooleans1 = ChannelBoolean {
                    CtrlWShown = false,
                    Inputs = {
                        Operation = Input { Value = 6, },
                        Background = Input {
                            SourceOp = "PaperFastNoise1",
                            Source = "Output",
                        },
                        Foreground = Input {
                            SourceOp = "PaperFastNoise2",
                            Source = "Output",
                        }
                    },
                    ViewInfo = OperatorInfo { Pos = { 59, 40.9966 } },
                },
                PaperFastNoise3 = FastNoise {
                    CtrlWShown = false,
                    Inputs = {
                        GlobalOut = Input { Value = 149, },
                        Width = Input { Value = @BGWidth@, },
                        Height = Input { Value = @BGHeight@, },
                        ["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
                        Center = Input { Value = { 0.960365853658537, 0.947154471544715 }, },
                        Detail = Input { Value = 10, },
                        Contrast = Input { Value = 1.32, },
                        Brightness = Input { Value = 1, },
                        XScale = Input { Value = 0.41, },
                        Seethe = Input { Value = -1.543, },
                        Discontinuous = Input { Value = 1, },
                        Inverted = Input { Value = 1, },
                        Color1Red = Input { Value = 1, },
                        Color1Green = Input { Value = 1, },
                        Color1Blue = Input { Value = 1, },
                        Color1Alpha = Input { Value = 1, },
                        Color2Red = Input { Value = 0, },
                        Color2Green = Input { Value = 0, },
                        Color2Blue = Input { Value = 0, }
                    },
                    ViewInfo = OperatorInfo { Pos = { -59.6869, 96.4506 } },
                },
                PaperMerge = Merge {
                    CtrlWZoom = false,
                    CtrlWShown = false,
                    Inputs = {
                        Blend = Input { Value = 0.543, },
                        Background = Input {
                            SourceOp = "ChannelBooleans1",
                            Source = "Output",
                        },
                        Foreground = Input {
                            SourceOp = "PaperFastNoise3",
                            Source = "Output",
                        },
                        ApplyMode = Input { Value = FuID { "Overlay" }, },
                        PerformDepthMerge = Input { Value = 0, }
                    },
                    ViewInfo = OperatorInfo { Pos = { 59, 96.4506 } },
                },
                PaperBrightnessContrast = BrightnessContrast {
                    CtrlWShown = false,
                    Inputs = {
                        Brightness = Input { Value = 0.19, },
                        Saturation = Input { Value = 0.66, },
                        Input = Input {
                            SourceOp = "PaperMerge",
                            Source = "Output",
                        }
                    },
                    ViewInfo = OperatorInfo { Pos = { 59, 137.519 } },
                }
            }
        }
"""

templateLoader = """
        @Name@ = Loader {
            Clips = {
                Clip {
                    ID = "Clip1",
                    Filename = "@FileName@",
                    FormatID = "JpegFormat",
                    StartFrame = -1,
                    LengthSetManually = true,
                    TrimIn = 0,
                    TrimOut = 0,
                    ExtendFirst = 0,
                    ExtendLast = 7000001,
                    Loop = 1,
                    AspectMode = 0,
                    Depth = 0,
                    TimeCode = 0,
                    GlobalStart = 0,
                    GlobalEnd = 7000001
                }
            },
            Inputs = {
                EffectMask = Input {
                    SourceOp = "@SourceOp@",
                    Source = "Mask",
                },
                LocalCache = Input { Value = FuID { "On" }, },
                ["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, }
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

templateRectangle = """
        @Name@ = RectangleMask {
            CtrlWZoom = false,
            Inputs = {
                Filter = Input { Value = FuID { "Fast Gaussian" }, },
                MaskWidth = Input { Value = @MaskWidth@, },
                MaskHeight = Input { Value = @MaskHeight@, },
                PixelAspect = Input { Value = { 1, 1 }, },
                UseFrameFormatSettings = Input { Value = 1, },
                ClippingMode = Input { Value = FuID { "None" }, },
                Width = Input { Value = @WidthRatio@, },
                Height = Input { Value = @HeightRatio@, }
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

# template MultiMerge decomposed
templateMultiMergeStart = """
        @Name@ = MultiMerge {
            Inputs = {
                LayerOrder = Input { Value = ScriptVal { {
                        [0] = 1
                        } }, },
                Background = Input {
                    SourceOp = "@nameBG@",
                    Source = "Output",
                },
                EffectMask = Input {
                    SourceOp = "@maskName@",
                    Source = "Mask",
                }
"""

# LayerX sample = Layer1
# InputNode sample = Transform_2
# LayerName sample = LayerName1
templateMultiMergeLayer = """
                ["@LayerX@.Foreground"] = Input {
                    SourceOp = "@InputNode@",
                    Source = "Output",
                },
                ["@LayerX@.Center"] = Input { Value = { @PosX@, @PosY@ }, },
                ["@LayerX@.Size"] = Input { Value = @Size@, },
                @LayerName@ = Input { Value = "@InputNode@ Layer", }
"""

templateMultiMergeLayerRectControl = """
                ["@LayerName@.Foreground"] = Input {
                    SourceOp = "@RectControl@",
                    Source = "Mask",
                },
                ["@LayerName@.Center"] = Input {
                    SourceOp = "@InputNode@",
                    Source = "Position",
                },
                ["@LayerName@.Operator"] = Input { Value = FuID { "Mask" }, },
                ["@LayerName@.Blend"] = Input { Value = 0.65, },
                @LayerName@ = Input { Value = "@RectControl@ Layer", }
"""

templateMultiMergeEnd = """
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

templatePolyPathStart = """
        @Name@ = PolyPath {
            Inputs = {
                Displacement = Input {
                    SourceOp = "@DisplacementName@",
                    Source = "Value",
                },
                PolyLine = Input {
                    Value = Polyline {
                        Points = {
"""

templatePolyPathEnd = """
                        }
                    },
                }
            },
        }
"""

templatePathDisplacementStart = """
        @Name@ = BezierSpline {
            SplineColor = { Red = 255, Green = 0, Blue = 255 },
            NameSet = true,
            KeyFrames = {
"""

templatePathDisplacementEnd = """

            }
        }
"""

templateMerge = """
        @Name@ = Merge {
            CtrlWZoom = false,
            NameSet = true,
            Inputs = {
                Blend = Input { Value = @Blend@, },
                Background = Input {
                    SourceOp = "@BG-SrcOp@",
                    Source = "Output",
                },
                Foreground = Input {
                    SourceOp = "@FG-SrcOp@",
                    Source = "Mask",
                },
                Center = Input {
                    SourceOp = "@Center-SrcOp@",
                    Source = "Position",
                },
                Operator = Input { Value = FuID { "Mask" }, },
                PerformDepthMerge = Input { Value = 0, }
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

templateCrop = """
        @Name@ = Crop {
            Inputs = {
                XOffset = Input {
                    SourceOp = "@XOffset-SrcOp@",
                    Source = "@XOffset-TypeSrc@",
                },
                YOffset = Input {
                    SourceOp = "@YOffset-SrcOp@",
                    Source = "@YOffset-TypeSrc@",
                },
                XSize = Input { Value = @XSize@, },
                YSize = Input { Value = @YSize@, },
                Input = Input {
                    SourceOp = "@Input-SrcOp@",
                    Source = "Output",
                }
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

# Operator
# 1 = substract
# 2 = multiply
templateCalcType1 = """
        @Name@ = Calculation {
            Inputs = {
                FirstOperand = Input {
                    SourceOp = "@Src-Op@",
                    Source = "Result",
                },
                Operator = Input { Value = @Operator@, },
                SecondOperand = Input { Value = @SecondOperandValue@, }
            },
        }
"""

templateCalcType2 = """
        @Name@ = Calculation {
            Inputs = {
                FirstOperand = Input {
                    Value = 0,
                    Expression = "@Expression@",
                },
                Operator = Input { Value = @Operator@, },
                SecondOperand = Input { Value = @SecondOperandValue@, }
            },
        }
"""

TemplatePaintMask = """
        @Name@ = PaintMask {
            CtrlWZoom = false,
            Inputs = {
                Filter = Input { Value = FuID { "Fast Gaussian" }, },
				SoftEdge = Input { Value = @SoftEdge@, },
                PaintMode = Input { Value = FuID { "None" }, },
                MaskWidth = Input { Value = @MaskWidth@, },
                MaskHeight = Input { Value = @MaskHeight@, },
                PixelAspect = Input { Value = { 1, 1 }, },
                UseFrameFormatSettings = Input { Value = 1, },
                ClippingMode = Input { Value = FuID { "None" }, },
                Paint = Input {
                    SourceOp = "@SrcOp@",
                    Source = "Out",
                }
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

TemplateStroke = """
        @Name@ = Stroke {
            Points = {
            },
            IsThreaded = false,
            Brushes = { "SoftBrush" },
            ApplyModes = { "PaintApplyColor" },
            CtrlWZoom = false,
            Inputs = {
                Paint = Input {
                    SourceOp = "@StrokePrev@",
                    Source = "Out",
                },
                BrushControls = Input { Value = 1, },
				["SoftBrush.Size"] = Input { Value = 0.0283, },
				["SoftBrush.Softness"] = Input { Value = 0.473, },
                StrokeControls = Input { Value = 1, },
                StrokeAnimation = Input { Value = 2, },
                WriteOnEnd = Input {
                    SourceOp = "@StrokeEnd@",
                    Source = "Value",
                },
                Center = Input { Value = { @CenterX@, @CenterY@ }, },
                Polyline = Input {
                    Value = Polyline {
                        Points = {
                            { Linear = true, X = -0.0911271870136261, Y = 0.0422503501176834, RX = 0.0625727574030558, RY = 0.00173131624857585 },
                            { Linear = true, X = 0.0965910851955414, Y = 0.0474442988634109, LX = -0.0625727574030558, LY = -0.00173131624857585, RX = -0.0627314945062001, RY = -0.0077765000363191 },
                            { Linear = true, X = -0.0916033983230591, Y = 0.0241147987544537, LX = 0.0627314945062001, LY = 0.0077765000363191, RX = 0.0622697075208028, RY = -0.00376561159888903 },
                            { Linear = true, X = 0.0952057242393494, Y = 0.0128179639577866, LX = -0.0622697075208028, LY = 0.00376561159888903, RX = -0.0618800719579061, RY = -0.00554021696249644 },
                            { Linear = true, X = -0.0904344916343689, Y = -0.00380268692970276, LX = 0.0618800719579061, LY = 0.00554021696249644, RX = 0.0640735824902852, RY = -0.00369347135225932 },
                            { Linear = true, X = 0.101786255836487, Y = -0.0148831009864807, LX = -0.0640735824902852, LY = 0.00369347135225932, RX = -0.064766267935435, RY = -0.00623274346192678 },
                            { Linear = true, X = -0.0925125479698181, Y = -0.033581331372261, LX = 0.064766267935435, LY = 0.00623274346192678, RX = 0, RY = 0 },
                            { Linear = true, X = -0.0925125479698181, Y = -0.033581331372261, LX = 0, LY = 0, RX = 0.0655743976434072, RY = -0.00207757949829102 },
                            { Linear = true, X = 0.104210644960403, Y = -0.0398140698671341, LX = -0.0655743976434072, LY = 0.00207757949829102, RX = -0.0651126106580098, RY = -0.00230842332045237 },
                            { Linear = true, X = -0.0911271870136261, Y = -0.0467393398284912, LX = 0.0651126106580098, LY = 0.00230842332045237 }
                        }
                    },
                }
            },
        }
"""
  
templateStrokeEnd = """
        @Name@ = BezierSpline {
            SplineColor = { Red = 233, Green = 233, Blue = 10 },
            KeyFrames = {
"""

templateStrokeEndEnd = """
            }
        }
"""

templateBezierSpline = """
        @Name@ = BezierSpline {
            SplineColor = { Red = @Red@, Green = @Green@, Blue = @Blue@ },
            KeyFrames = {
"""

templateBezierSplineEnd = """
			}
		}
"""

templateTransform = """
		@Name@ = Transform {
			CtrlWZoom = false,
			Inputs = {
				Size = Input {
					SourceOp = "@SrcOpSize@",
					Source = "Value",
				},
				Input = Input {
					SourceOp = "@SrcOpInput@",
					Source = "Output",
				}
			},
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
		}
"""

templateMediaOut = """
        @Name@ = MediaOut {
            Inputs = {
                Index = Input { Value = "0", },
                Input = Input {
                    SourceOp = "@SourceOp@",
                    Source = "Output",
                },
            },
            ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
        }
"""

# --------------------------------------------------------
# functions
# --------------------------------------------------------
def setValue( valueName, value):
    global curText
    valueName = "@" + valueName + "@"
    if isinstance( value, str):
        curText = curText.replace( valueName, value)
    else:
        curText = curText.replace( valueName, str(value))

def setValueLayer( valueName, value):
    global curLayer
    valueName = "@" + valueName + "@"
    if isinstance( value, str):
        curLayer = curLayer.replace( valueName, value)
    else:
        curLayer = curLayer.replace( valueName, str(value))

def get_jpeg_dimensions(filename):
    with open(filename, 'rb') as f:
        f.seek(0)  # Go to the start of the file
        # Read the first few bytes to find the SOF0 marker (0xC0)
        while True:
            byte = f.read(1)
            if not byte:
                break
            if byte == b'\xFF':
                marker = f.read(1)
                if marker == b'\xC0':  # SOF0 marker
                    f.read(3)  # Skip the next 3 bytes
                    height = int.from_bytes(f.read(2), 'big')
                    width = int.from_bytes(f.read(2), 'big')
                    return width, height

    return None

# --------------------------------------------------------
# Main function
# --------------------------------------------------------
def CreateSlideShow(folder, displayTime, travelTime, resolution):
    """
    Generate davinci resolve setting fusion file.

    Note:
        The XMargin variable allows you to specify the size of the margin

    Returns:
        NA
    """
    # ---------------------------------------------------------------
    global curText
    global curLayer
    
    print("folder :", folder)
    print("display time : ", displayTime)
    print("travel time : ", travelTime)
    print("resolution : ", resolution)
  
    # Reference size of pictures
    if resolution == "UHD":
        refXSize = 3840
        refYSize = 2160
    else:
        refXSize = 1920
        refYSize = 1080

    Xmargin = 300 
    Ymargin = Xmargin # BUG Davinci about erratic displacement in no square space
    ExtMargin = 4 * Xmargin

    # Check folder exist
    if not os.path.exists(folder):
            print("folder don't exist :", folder)
            exit

    # Check if it is a real folder
    if not os.path.isdir(folder):
            print("Not a folder :", folder)
            exit

    # List files into folder
    files = os.listdir(folder)

    # Filter to check files only
    files = [file for file in files if os.path.isfile(os.path.join(folder, file))]

    # sort in alphabetical order
    files.sort()

    # Init
    xStart = 150    # xStart => Most left node position for x
    yStart = 0      # yStart => Most upper node position for y
    xSpace = 125    # xSpace => spacing between nodes horizontally
    ySpace = 50     # ySpace => spacing between nodes vertically

    result = ""
    
    # Main loop
    currentX = xStart
    currentY = yStart

    fourBackSlashes = "\\\\"
    twoBackSlashes = "\\"

    # Prepare grid and directionnal array
    grid = np.zeros((21, 21), dtype=int)

    imageInfos = np.zeros((100,8), dtype=int)
    # 0 = relative position X into grid
    # 1 = relative position Y into grid
    # 2 = posX in pixel
    # 3 = posY in pixel
    # 4 = offset between posX and previous X image
    # 5 = offset between posY and previous Y image
    # 6 = original X size
    # 7 = original Y size

    dir = np.zeros((4, 2), dtype=int)
    # To Up
    dir[0,0] = 0
    dir[0,1] = -1
    # To Right
    dir[1,0] = 1
    dir[1,1] = 0
    # To down
    dir[2,0] = 0
    dir[2,1] = 1
    # To Left
    dir[3,0] = -1
    dir[3,1] = 0

    filesCount = 0

    print("files in alphabetical order :")
    for file in files:
        print(file)
        imageFile = folder + twoBackSlashes + file
        dimensions = get_jpeg_dimensions(imageFile)
        if dimensions:
            width, height = dimensions
        else:
            # if error reading dimension, assume reference size
            width = refYSize
            height = refYSize

        filesCount += 1
        # Store image dimension
        imageInfos[filesCount,6] = width
        imageInfos[filesCount,7] = height

        # Append the Loader node
        curText = templateLoader
        nameLoader = "Loader_" + str(filesCount)
        setValue( "Name", nameLoader)
        pathFile = folder + twoBackSlashes + file
        pathFile = pathFile.replace(twoBackSlashes, fourBackSlashes)
        setValue( "FileName", pathFile)
        setValue( "SourceOp", "")
        setValue( "OperatorInfoPosX", currentX)
        setValue( "OperatorInfoPosY", currentY)
        result = result + curText[:-1] + ","
        
        currentY += ySpace
        currentX = xStart

    currentX += (3*xSpace)
    currentY = yStart

    travelDir = 3
    # Place initial coordinates to center of grid
    x = 11
    y = 11
    minX = 1000
    minY = 1000
    maxX = 0
    maxY = 0

    imageNumber = 0
    testX = 0
    testY = 0
    pathLong = 0
    
    # Place Images in table grid in a spiral way
    for i in range(filesCount):
        imageNumber += 1
        # Attempt to rotate clockwise
        travelDirTest = travelDir + 1
        if (travelDirTest == 4):
            travelDirTest = 0
        testX = x + int(dir[travelDirTest,0])
        testY = y + int(dir[travelDirTest,1])
        # if next pos with rotate is free then go
        if (grid[testX,testY] == 0):
            travelDir = travelDirTest
        # apply the move and store image number in the grid and memorize pathlong
        deltaX = (refXSize + Xmargin) * abs(int(dir[travelDir,0])) * (imageNumber != 1)
        deltaY = (refYSize + Ymargin) * abs(int(dir[travelDir,1])) * (imageNumber != 1)
        deltaXY = deltaX + deltaY
        pathLong += deltaXY
        # Move the coordinate into table grid and imageInfos
        x = x + int(dir[travelDir,0])
        y = y + int(dir[travelDir,1])
        grid[x,y] = imageNumber
        imageInfos[imageNumber,0] = x
        imageInfos[imageNumber,1] = y
        imageInfos[imageNumber,4] = deltaX
        imageInfos[imageNumber,5] = deltaY
        # memorize min and max for x and y
        minX = min(minX, x)
        maxX = max(maxX, x)
        minY = min(minY, y)
        maxY = max(maxY, y)

    # Real size of image table
    sizeTabX = maxX - minX + 1
    sizeTabY = maxY - minY + 1

    # Generate Background Paper
    curText = templatePaper
    nameBG = "Paper"
    setValue( "Name", nameBG)
    backGroundWidth = max (((sizeTabX * refXSize) + ((sizeTabX + 1) * Xmargin)), ((sizeTabY * refYSize) + ((sizeTabY + 1) * Ymargin)))
    backGroundWidth += 2 * ExtMargin
    # Height = Width accordingly to the fusion BUG on displacement calculation
    backGroundHeight = backGroundWidth
    setValue( "BGWidth", backGroundWidth)
    setValue( "BGHeight", backGroundHeight)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", yStart)
    result = result + curText[:-1] + ","
    currentY = ((filesCount - 1) / 2) * ySpace

    # Generate multimerging node
    namePaintMask = "PaintMasK"

    curText = templateMultiMergeStart
    nameMultiMerge = "MultiMerging"
    setValue( "Name", nameMultiMerge)
    setValue( "nameBG", "PaperBrightnessContrast") # Be aware, not a variable
    setValue( "maskName", namePaintMask)
    result = result + curText[:-1] + ","

    curText = ""
    layerNumber = 0
    caracterSeparator = ","
    for i in range(filesCount):
        layerNumber += 1
        curLayer = templateMultiMergeLayer
        setValueLayer( "LayerX", "Layer" + str(layerNumber))
        setValueLayer( "InputNode", "Loader_" + str(layerNumber))
        setValueLayer( "SourceMode", "Output")
        setValueLayer( "LayerName", "LayerName" + str(layerNumber))

        # determine position X, mean the center of image expressed as a fraction of the background image width
        indX = int(imageInfos[layerNumber,0]) - minX # indice X from 0 to n
        posX = indX * refXSize
        posX = posX + (Xmargin * (indX + 1))
        posX = posX + refXSize // 2 # center of image
        imageInfos[layerNumber,2] = posX
        posX += ExtMargin
        posX = posX / backGroundWidth

        # determine position Y, mean the center of image expressed as a fraction of the background image height
        indY = int(imageInfos[layerNumber,1]) - minY # indice Y from 0 to n
        posY = indY * refYSize
        posY = posY + (Ymargin * (indY + 1))
        posY = posY + refYSize // 2 # center of image
        imageInfos[layerNumber,3] = posY
        posY += ExtMargin
        posY = posY / backGroundHeight

        # determine scale
        deltaX = int(imageInfos[layerNumber,6]) / refXSize
        deltaY = int(imageInfos[layerNumber,7]) / refYSize
        if deltaX > deltaY:
            scale = 1 / deltaX # refXSize / int(size[layerNumber,0])
        else:
            scale = 1 / deltaY # refYSize / int(size[layerNumber,1])

        setValueLayer( "PosX", posX)
        setValueLayer( "PosY", posY)
        setValueLayer( "Size", scale)

        # if layerNumber == filesCount:
        #     caracterSeparator = ""
        curText += curLayer[:-1]
        curText += caracterSeparator
    
    result = result + curText[:-1] + ","

    curText = templateMultiMergeEnd
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY)
    result = result + curText[:-1] + ","
    currentX += xSpace

    # Generate polyPath for merge_control
    curText = templatePolyPathStart
    namePolyPathMerge = "PolyPathMultiMerge"
    nameDisplacement = namePolyPathMerge + "_Displacement"
    setValue( "Name", namePolyPathMerge)
    setValue( "DisplacementName", nameDisplacement)
    templateLine = "							{ Linear = true, X = @valX@, Y = @valY@ },"
    for i in range(filesCount):
        layerNumber = i+1
        newLine = templateLine
        # for multimerge X and Y must be relative to global size
        pointX = (int(imageInfos[layerNumber,2] + ExtMargin) / backGroundWidth -0.5)
        pointY = (int(imageInfos[layerNumber,3] + ExtMargin) / backGroundHeight -0.5)
        newLine = newLine.replace("@valX@",str(pointX))
        newLine = newLine.replace("@valY@",str(pointY))
        # newLine = newLine.replace("@valRX@","0")
        # newLine = newLine.replace("@valRY@","0")
        curText += newLine
    
    curText += templatePolyPathEnd
    result = result + curText[:-1] + ","

    # Generate Displacement Path for multimerge_control
    curText = templatePathDisplacementStart
    setValue( "Name", nameDisplacement)
    templateLine = "				[@XFrame@] = { @YValue@, Flags = { Linear = true } },"
    XFrame = 0
    YValue = 0
    for i in range(filesCount):
        imageNumber = i+1
        newLine = templateLine
        newLine = newLine.replace("@XFrame@",str(XFrame))
        newLine = newLine.replace("@YValue@",str(YValue))
        curText += newLine
        XFrame += 30 * displayTime
        newLine = templateLine
        newLine = newLine.replace("@XFrame@",str(XFrame))
        newLine = newLine.replace("@YValue@",str(YValue))
        curText += newLine
        XFrame += 30 * travelTime
        DX = int(imageInfos[imageNumber + 1, 4])
        DY = int(imageInfos[imageNumber + 1, 5])
        YValue += (DX + DY) / pathLong
      
    curText += templatePathDisplacementEnd
    result = result + curText[:-1] + ","

    # Generate Stroke
    imageNumber = 0
    strokePrevName = ""
    for i in range(filesCount):
        imageNumber += 1
        
        # Generate Stroke End
        curText = templateStrokeEnd
        nameStrokeBrush = "StrokeEnd" + str(imageNumber)
        setValue( "Name", nameStrokeBrush)
        templateLine = "				[@FrameNumber@] = { @YPos@, Flags = { Linear = true } },"
        frameStart = (imageNumber -1) * ((displayTime + travelTime) * 30)
        frameStart += - travelTime * 30 // 4
        frameEnd = frameStart + 30
        newLine = templateLine
        newLine = newLine.replace("@FrameNumber@",str(frameStart))
        newLine = newLine.replace("@YPos@","0")
        curText += newLine
        newLine = templateLine
        newLine = newLine.replace("@FrameNumber@",str(frameEnd))
        newLine = newLine.replace("@YPos@","1")
        curText += newLine
        result = result + curText
        curText = templateStrokeEndEnd
        result = result + curText[:-1] + ","

        # Generate Stroke main
        curText = TemplateStroke
        nameStroke = "Stroke" + str(imageNumber)
        setValue( "Name", nameStroke)
        setValue( "StrokePrev", strokePrevName)
        setValue( "StrokeEnd", nameStrokeBrush)
        imgCenterX = int(imageInfos[imageNumber,2] + ExtMargin)/backGroundWidth
        imgCenterY = int(imageInfos[imageNumber,3] + ExtMargin)/backGroundHeight
        setValue( "CenterX", imgCenterX)
        setValue( "CenterY", imgCenterY)

        # Generate Stroke Line
        imgSizeX = refXSize / backGroundWidth
        imgSizeY = refYSize / backGroundHeight

        for j in range(10):
            randX = imgSizeX - random.uniform(0.0, imgSizeX)
            randY = imgSizeY - random.uniform(0.0, imgSizeY)

        strokePrevName = nameStroke
        result = result + curText[:-1] + ","

    # Generate PaintMask with Stroke test
    curText = TemplatePaintMask
    setValue( "Name", namePaintMask)
    setValue( "MaskWidth", backGroundWidth)
    setValue( "MaskHeight", backGroundHeight)
    setValue( "SoftEdge", 0.008)
    setValue( "SrcOp", nameStroke)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY + ySpace)
    result = result + curText[:-1] + ","

    # Generate rectangle for the mergeCtrl
    curText = templateRectangle
    nameRectangle = "RectangleControl"
    setValue( "Name", nameRectangle)
    setValue( "MaskWidth", refXSize)
    setValue( "MaskHeight", refYSize)
    setValue( "WidthRatio", 1.3)
    setValue( "HeightRatio", 1.3)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY - 2 * ySpace)
    result = result + curText[:-1] + ","

    # Generate mergeCtrl
    curText = templateMerge
    nameMerge = "MergeCtrl"
    setValue( "Name", nameMerge)
    setValue( "Blend", 0.5)
    setValue( "BG-SrcOp", nameMultiMerge)
    setValue( "FG-SrcOp", nameRectangle)
    setValue( "Center-SrcOp", namePolyPathMerge)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY - ySpace)
    result = result + curText[:-1] + ","
    currentX += xSpace

    # Generate Calculations
    curText = templateCalcType2
    nameCalcX2 = "CalcX2"
    setValue( "Name", nameCalcX2)
    setValue( "Expression", nameMerge + ".Center.X")
    setValue( "Operator", 2) # multiply
    setValue( "SecondOperandValue", backGroundWidth)
    result = result + curText[:-1] + ","

    curText = templateCalcType2
    nameCalcY2 = "CalcY2"
    setValue( "Name", nameCalcY2)
    setValue( "Expression", nameMerge + ".Center.Y")
    setValue( "Operator", 2) # multiply
    setValue( "SecondOperandValue", backGroundHeight)
    result = result + curText[:-1] + ","

    curText = templateCalcType1
    nameCalcX1 = "CalcX1"
    setValue( "Name", nameCalcX1)
    setValue( "Src-Op", nameCalcX2)
    setValue( "Operator", 1) # substract
    setValue( "SecondOperandValue", (refXSize*1.3) / 2)
    result = result + curText[:-1] + ","

    curText = templateCalcType1
    nameCalcY1 = "CalcY1"
    setValue( "Name", nameCalcY1)
    setValue( "Src-Op", nameCalcY2)
    setValue( "Operator", 1) # substract
    setValue( "SecondOperandValue", (refYSize*1.3) / 2)
    result = result + curText[:-1] + ","

    # Generate Cropping
    curText = templateCrop
    nameCropping = "Cropping"
    setValue( "Name", nameCropping)
    setValue( "XOffset-SrcOp", nameCalcX1)
    setValue( "YOffset-SrcOp", nameCalcY1)
    setValue( "XOffset-TypeSrc", "Result")
    setValue( "YOffset-TypeSrc", "Result")
    setValue( "XSize", refXSize * 1.3) # 30% margin
    setValue( "YSize", refYSize * 1.3)
    setValue( "Input-SrcOp", nameMultiMerge)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY)
    result = result + curText[:-1] + ","
    currentX += xSpace

    # Generate BezierSpline Transform Size
    curText = templateBezierSpline
    nameBSTransformSize = "BSTransformSize"
    setValue( "Name", nameBSTransformSize)
    setValue( "Red", 0)
    setValue( "Green", 255)
    setValue( "Blue", 0)
    NumFrame = 0
    templateLine = "				[@NumFrame@] = { @Size@, Flags = { Linear = true } },"
    for i in range(filesCount - 1):
        imageNumber = i+1
        newLine = templateLine
        NumFrame += displayTime * 30
        newLine = newLine.replace("@NumFrame@",str(NumFrame))
        newLine = newLine.replace("@Size@",str(1.3))
        curText += newLine
        NumFrame += travelTime * 30 / 2
        newLine = templateLine
        newLine = newLine.replace("@NumFrame@",str(NumFrame))
        newLine = newLine.replace("@Size@",str(1))
        curText += newLine
        NumFrame += travelTime * 30 / 2
        newLine = templateLine
        newLine = newLine.replace("@NumFrame@",str(NumFrame))
        newLine = newLine.replace("@Size@",str(1.3))
        curText += newLine

    curText += templateBezierSplineEnd
    result = result + curText[:-1] + ","

    # Generate Transform
    curText = templateTransform
    nameTransform = "Transform"
    setValue( "Name", nameTransform)
    setValue( "SrcOpSize", nameBSTransformSize)
    setValue( "SrcOpInput", nameCropping)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY)
    result = result + curText[:-1] + ","
    currentX += xSpace

    # Generate MediaOut
    curText = templateMediaOut
    nameMediaOut = "MediaOut1"
    setValue( "Name", nameMediaOut)
    setValue( "SourceOp", nameTransform)
    setValue( "OperatorInfoPosX", currentX)
    setValue( "OperatorInfoPosY", currentY)
    result = result + curText[:-1] + ","

    # Set starting and ending Text
    result = templateStart[:-1] + result
    result = result[:-1] + templateEnd
    print(result)
    
    # File path
    file_path = "output.setting"

    # Open the file in write mode and write the text
    with open(file_path, "w") as file:
        file.write(result)

# Main
if __name__ == "__main__":
    # Check input parameters
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = "C:\temp"
    if len(sys.argv) > 2:
        displayTime = int(sys.argv[2])
    else:
        displayTime = 5
    if len(sys.argv) > 3:
        travelTime = int(sys.argv[3])
    else:
        travelTime = 5
    if len(sys.argv) > 4:
        resolution = sys.argv[4]
    else:
        resolution = "HD"

    # Call main function with parameters
    CreateSlideShow(folder, displayTime, travelTime, resolution)
