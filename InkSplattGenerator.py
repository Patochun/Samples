"""
inkSplashGenerator

Generates ink splashes for Davinci Resolve fusion module

Author   : Patochun (Patrick M)
Mail     : ptkmgr@gmail.com
YT : https://youtu.be/UTj_k62UpUI
Create   : 2024-04-20
Version  : 1.0
Compatibility : DaVinci Resolve v18

Licence used : Creative Commons CC BY
Check licence here : https://creativecommons.org

Usage :
    python inkSplashGenerator.py [inkSplashCount] [framesCount]
    
    inkSplashCount => between 8 to 128 provide the bests results
    framesCount => small equal quickly splash appear than big equal slowly
"""

import sys
import random

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

templateFastNoise = """
		@Name@ = FastNoise {
			NameSet = true,
			Inputs = {
				GlobalOut = Input { Value = 299, },
				Width = Input { Value = 3840, },
				Height = Input { Value = 2160, },
				UseFrameFormatSettings = Input { Value = 1, },
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
				Detail = Input { Value = 10, },
				Contrast = Input { Value = @Contrast@, },
				Brightness = Input { Value = -0.002, },
				XScale = Input { Value = @Scale@, },
				Seethe = Input { Value = @Seethe@, },
				SeetheRate = Input { Value = @SeetheRate@, },
				Type = Input { Value = 1, },
				GradientType = Input { Value = 5, },
				Start = Input { Value = { @StartX@, @StartY@ }, },
				End = Input { Value = { @EndX@, @EndY@ }, },
				Gradient = Input {
					Value = Gradient {
						Colors = {
							[0] = { @GradStart@, @GradStart@, @GradStart@, 1 },
							[1] = { @GradEnd@, @GradEnd@, @GradEnd@, 1 }
						}
					},
				},
				Offset = Input {
					SourceOp = "@OffsetName@",
					Source = "Value",
				},
			},
			ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
		}
"""

templateBezierSpline = """
		@Name@ = BezierSpline {
			SplineColor = { Red = @Red@, Green = @Green@, Blue = @Blue@ },
			CtrlWZoom = false,
			KeyFrames = {
				[@StartFrame@] = { -5, RH = { @InterFrame@, 10 }, Flags = { Linear = true } },
				[@EndFrame@] = { 10, LH = { 140, 10 } }
			}
		}
"""

templateTransform = """
		@Name@ = Transform {
			NameSet = true,
			Inputs = {
				Center = Input { Value = { @CenterX@, @CenterY@ }, },
				Input = Input {
					SourceOp = "@InkSplashName@",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
		}
"""

templateBackground = """
		@Name@ = Background {
			Inputs = {
				GlobalOut = Input { Value = 149, },
				Width = Input { Value = 3840, },
				Height = Input { Value = 2160, },
				UseFrameFormatSettings = Input { Value = 1, },
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
				TopLeftRed = Input { Value = 1, },
				TopLeftGreen = Input { Value = 1, },
				TopLeftBlue = Input { Value = 1, },
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
					SourceOp = "@BackgroundName@",
					Source = "Output",
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
				["@LayerX@.ApplyMode"] = Input { Value = FuID { "Multiply" }, },
				@LayerName@ = Input { Value = "@InputNode@ Layer", }
"""

templateMultiMergeEnd = """
			},
			ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
		}
"""

templateMediaOut = """
		@Name@ = MediaOut {
			Inputs = {
				Index = Input { Value = "0", },
				Input = Input {
					SourceOp = "@SourceNode@",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { @OperatorInfoPosX@, @OperatorInfoPosY@ } },
		}
"""

# functions
def CreateInkSplashes(inkSplashCount, framesCount):
    """
    Generate davinci resolve setting fusion file.

    Args:
        inkSplashCount  : Count of desired ink Splash(s)
        framesCount : number of frames

    Note:
        The YMargin variable allows you to specify the size of the margin in Y as a percentage.
        The margin in X is calculated from that in Y by applying a ratio.

    Returns:
        NA
    """
    # ---------------------------------------------------------------
    print("Ink Splash(s) Count :", inkSplashCount)
    print("Frames Count : ", framesCount)

    # Init
    xStart = 150    # xStart => Most left node position for x
    yStart = 0      # yStart => Most upper node position for y
    xSpace = 100    # xSpace => spacing between nodes horizontally
    ySpace = 25     # ySpace => spacing between nodes vertically

    result = ""
    
    # Main loop
    currentX = xStart - 100
    currentY = yStart - 25

    backGroundName = "PureWhite"

    # Generate fastNoise + BezierSpline + Transform
    for i in range(inkSplashCount):
        inkSplashCurrentNumber = i+1
        currentY += ySpace
        print("Generate Ink Splash number :", inkSplashCurrentNumber)
        
        # Append the FastNoise node
        fastNoiseText = templateFastNoise
        fastNoiseName = "Ink_Splash_" + str(inkSplashCurrentNumber)
        fastNoisePosX = xStart
        fastNoisePosY = currentY
        bezierSplineName = fastNoiseName + "_Offset"
        fastNoiseText = fastNoiseText.replace( "@Name@", fastNoiseName)
        fastNoiseText = fastNoiseText.replace( "@OffsetName@", bezierSplineName)
        fastNoiseText = fastNoiseText.replace( "@OperatorInfoPosX@", str(fastNoisePosX))
        fastNoiseText = fastNoiseText.replace( "@OperatorInfoPosY@", str(fastNoisePosY))

        # Margin in percent
        UHDRatio = 3840/2160
        YMargin = 0.30
        XMargin = YMargin / UHDRatio
        YExpand = 0.008
        XExpand = YExpand * UHDRatio
                        
        fastNoiseScale = random.uniform(2, 3)
        fastNoiseSeethe = random.uniform(0, 10)
        fastNoiseSeetheRate = random.uniform(0.01, 0.05)
        fastNoiseStartX = random.uniform(XMargin, 1 - XMargin)
        fastNoiseStartY = random.uniform(YMargin, 1 - YMargin)
        fastNoiseEndX = fastNoiseStartX + random.uniform(-XExpand, XExpand)
        fastNoiseEndY = fastNoiseStartY + random.uniform(-YExpand, YExpand)
        fastNoiseGradStart = random.uniform(0.50, 0.75)
        fastNoiseGradEnd = random.uniform(1, 1)

        # fastNoiseContrast must be proportional to location of noise cloud
        # 10 to 20 if location is close the center
        # 1 to 5 if location if far from the center (or near the margin)
        # centerProximity give a value from 0 to 1, mean 0 is close the center and 1 is the most far possible considering the margins
        centerProximity = abs(fastNoiseStartX - 0.5) + abs(fastNoiseStartY - 0.5)
        noiseContrastMini = (1 - centerProximity) * 10
        noiseContrastMaxi = (1 - centerProximity) * 20
        fastNoiseContrast = random.uniform(noiseContrastMini, noiseContrastMaxi)

        fastNoiseText = fastNoiseText.replace( "@Contrast@", str(fastNoiseContrast))
        fastNoiseText = fastNoiseText.replace( "@Scale@", str(fastNoiseScale))
        fastNoiseText = fastNoiseText.replace( "@Seethe@", str(fastNoiseSeethe))
        fastNoiseText = fastNoiseText.replace( "@SeetheRate@", str(fastNoiseSeetheRate))
        fastNoiseText = fastNoiseText.replace( "@StartX@", str(fastNoiseStartX))
        fastNoiseText = fastNoiseText.replace( "@StartY@", str(fastNoiseStartY))
        fastNoiseText = fastNoiseText.replace( "@EndX@", str(fastNoiseEndX))
        fastNoiseText = fastNoiseText.replace( "@EndY@", str(fastNoiseEndY))
        fastNoiseText = fastNoiseText.replace( "@GradStart@", str(fastNoiseGradStart))
        fastNoiseText = fastNoiseText.replace( "@GradEnd@", str(fastNoiseGradEnd))

        result = result + fastNoiseText[:-1] + ","

        # Append the BezierSpline linked with the previous FastNoise
        bezierSplineText = templateBezierSpline
        bezierSplineText = bezierSplineText.replace( "@Name@", bezierSplineName)
        bezierSplineRed = random.uniform(20, 235)
        bezierSplineGreen = random.uniform(20, 235)
        bezierSplineBlue = random.uniform(20, 235)
        bezierSplineText = bezierSplineText.replace( "@Red@", str(bezierSplineRed))
        bezierSplineText = bezierSplineText.replace( "@Green@", str(bezierSplineGreen))
        bezierSplineText = bezierSplineText.replace( "@Blue@", str(bezierSplineBlue))
        bSStart = framesCount // 10
        bSEnd = int(framesCount - (framesCount * 0.3))
        bSInter = (bSEnd + bSStart) // 2
        bezierSplineStartFrame = (random.uniform(bSStart, bSStart * 2) // inkSplashCount) * inkSplashCurrentNumber
        bezierSplineInterFrame = random.uniform(bSInter - 10, bSInter + 10)
        bezierSplineEndFrame = random.uniform(bSEnd - 10, bSEnd + 10)
        bezierSplineText = bezierSplineText.replace( "@StartFrame@", str(bezierSplineStartFrame))
        bezierSplineText = bezierSplineText.replace( "@InterFrame@", str(bezierSplineInterFrame))
        bezierSplineText = bezierSplineText.replace( "@EndFrame@", str(bezierSplineEndFrame))

        result = result + bezierSplineText[:-1] + ","

    # Generate multimerging node
    multiMergeText = templateMultiMergeStart
    multiMergeName = "MultiMerging"
    multiMergeBackgroundName = backGroundName
    multiMergeText = multiMergeText.replace( "@Name@", multiMergeName)
    multiMergeText = multiMergeText.replace( "@BackgroundName@", multiMergeBackgroundName)
    multiMergeText = multiMergeText[:-1] + ","

    for i in range(inkSplashCount):
        inkSplashCurrentNumber = i+1
        LayerText = templateMultiMergeLayer
        LayerText_LayerX = "Layer" + str(inkSplashCurrentNumber)
        LayerText_InputNode = "Ink_Splash_" + str(inkSplashCurrentNumber)
        LayerText_LayerName = "LayerName" + str(inkSplashCurrentNumber)
        LayerText = LayerText.replace( "@LayerX@", LayerText_LayerX)
        LayerText = LayerText.replace( "@InputNode@", LayerText_InputNode)
        LayerText = LayerText.replace( "@LayerName@", LayerText_LayerName)
        if i+1 == inkSplashCount:
            caracterSeparator = ""
        else:
            caracterSeparator = ","
        multiMergeText += LayerText
        multiMergeText = multiMergeText[:-1] + caracterSeparator

    multiMergeText = multiMergeText + templateMultiMergeEnd
    multiMergePosX = fastNoisePosX + 100
    multiMergePosY = currentY
    multiMergeText = multiMergeText.replace( "@OperatorInfoPosX@", str(multiMergePosX))
    multiMergeText = multiMergeText.replace( "@OperatorInfoPosY@", str(multiMergePosY))
    result = result + multiMergeText[:-1] + ","

    # Generate Background
    backGroundText = templateBackground
    backGroundPosX = multiMergePosX
    backGroundPosY = multiMergePosY + ySpace
    backGroundText = backGroundText.replace( "@Name@", backGroundName)
    backGroundText = backGroundText.replace( "@OperatorInfoPosX@", str(backGroundPosX))
    backGroundText = backGroundText.replace( "@OperatorInfoPosY@", str(backGroundPosY))
    result = result + backGroundText[:-1] + ","

    # Generate MediaOut
    mediaOutText = templateMediaOut
    mediaOutName = "MediaOut1"
    mediaOutPosX = multiMergePosX + 100
    mediaOutPosY = currentY
    mediaOutSourceNode = multiMergeName
    mediaOutText = mediaOutText.replace( "@Name@", mediaOutName)
    mediaOutText = mediaOutText.replace( "@OperatorInfoPosX@", str(mediaOutPosX))
    mediaOutText = mediaOutText.replace( "@OperatorInfoPosY@", str(mediaOutPosY))
    mediaOutText = mediaOutText.replace( "@SourceNode@", mediaOutSourceNode)
    result = result + mediaOutText

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
        inkSplashCount = int(sys.argv[1])
    else:
        inkSplashCount = 3
    if len(sys.argv) > 2:
        framesCount = int(sys.argv[2])
    else:
        framesCount = 240

    # Call main function with parameters
    CreateInkSplashes(inkSplashCount, framesCount)
