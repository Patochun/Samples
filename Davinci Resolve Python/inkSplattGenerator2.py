import sys
import random
from dataclasses import dataclass

# ------------------------------------------------------------
# Template base helper
# ------------------------------------------------------------

class FusionTemplate:
    def __init__(self, template):
        self.template = template

    def render(self, **kwargs):
        # Render template using python format
        return self.template.format(**kwargs)


# ------------------------------------------------------------
# Node templates
# ------------------------------------------------------------

FAST_NOISE_TEMPLATE = FusionTemplate("""
        {name} = FastNoise {{
            NameSet = true,
            Inputs = {{
                GlobalOut = Input {{ Value = 299, }},
                Width = Input {{ Value = 3840, }},
                Height = Input {{ Value = 2160, }},
                UseFrameFormatSettings = Input {{ Value = 1, }},
                ["Gamut.SLogVersion"] = Input {{ Value = FuID {{ "SLog2" }} }},
                Detail = Input {{ Value = 10 }},
                Contrast = Input {{ Value = {contrast} }},
                Brightness = Input {{ Value = -0.002 }},
                XScale = Input {{ Value = {scale} }},
                Seethe = Input {{ Value = {seethe} }},
                SeetheRate = Input {{ Value = {seetheRate} }},
                Type = Input {{ Value = 1 }},
                GradientType = Input {{ Value = 5 }},
                Start = Input {{ Value = {{ {startX}, {startY} }} }},
                End = Input {{ Value = {{ {endX}, {endY} }} }},
                Gradient = Input {{
                    Value = Gradient {{
                        Colors = {{
                            [0] = {{ {gradStart}, {gradStart}, {gradStart}, 1 }},
                            [1] = {{ {gradEnd}, {gradEnd}, {gradEnd}, 1 }}
                        }}
                    }},
                }},
                Offset = Input {{
                    SourceOp = "{offsetName}",
                    Source = "Value",
                }},
            }},
            ViewInfo = OperatorInfo {{ Pos = {{ {posX}, {posY} }} }},
        }}
""")

BEZIER_TEMPLATE = FusionTemplate("""
        {name} = BezierSpline {{
            SplineColor = {{ Red = {red}, Green = {green}, Blue = {blue} }},
            CtrlWZoom = false,
            KeyFrames = {{
                [{startFrame}] = {{ -5, RH = {{ {interFrame}, 10 }}, Flags = {{ Linear = true }} }},
                [{endFrame}] = {{ 10, LH = {{ 140, 10 }} }}
            }}
        }}
""")


# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------

@dataclass
class FastNoiseNode:
    index: int
    posX: int
    posY: int

    def generate(self):
        # Compute margins
        uhDRatio = 3840 / 2160
        yMargin = 0.30
        xMargin = yMargin / uhDRatio
        yExpand = 0.008
        xExpand = yExpand * uhDRatio

        startX = random.uniform(xMargin, 1 - xMargin)
        startY = random.uniform(yMargin, 1 - yMargin)

        centerProximity = abs(startX - 0.5) + abs(startY - 0.5)
        contrastMin = (1 - centerProximity) * 10
        contrastMax = (1 - centerProximity) * 20

        return FAST_NOISE_TEMPLATE.render(
            name=f"Ink_Splash_{self.index}",
            offsetName=f"Ink_Splash_{self.index}_Offset",
            contrast=random.uniform(contrastMin, contrastMax),
            scale=random.uniform(2, 3),
            seethe=random.uniform(0, 10),
            seetheRate=random.uniform(0.01, 0.05),
            startX=startX,
            startY=startY,
            endX=startX + random.uniform(-xExpand, xExpand),
            endY=startY + random.uniform(-yExpand, yExpand),
            gradStart=random.uniform(0.5, 0.75),
            gradEnd=1,
            posX=self.posX,
            posY=self.posY,
        )


@dataclass
class BezierSplineNode:
    index: int
    framesCount: int

    def generate(self):
        startBase = self.framesCount // 10
        endBase = int(self.framesCount * 0.7)
        interBase = (startBase + endBase) // 2

        return BEZIER_TEMPLATE.render(
            name=f"Ink_Splash_{self.index}_Offset",
            red=random.uniform(20, 235),
            green=random.uniform(20, 235),
            blue=random.uniform(20, 235),
            startFrame=random.randint(startBase, startBase * 2),
            interFrame=random.randint(interBase - 10, interBase + 10),
            endFrame=random.randint(endBase - 10, endBase + 10),
        )


# ------------------------------------------------------------
# Generator
# ------------------------------------------------------------

class InkSplashGenerator:
    def __init__(self, inkSplashCount, framesCount):
        self.inkSplashCount = inkSplashCount
        self.framesCount = framesCount
        self.nodes = []

    def generate(self):
        xStart = 150
        yStart = 0
        ySpace = 25

        currentY = yStart

        for i in range(1, self.inkSplashCount + 1):
            currentY += ySpace

            fastNoise = FastNoiseNode(i, xStart, currentY)
            bezier = BezierSplineNode(i, self.framesCount)

            self.nodes.append(fastNoise.generate())
            self.nodes.append(bezier.generate())

        return self.buildFile()

    def buildFile(self):
        body = ",\n".join(self.nodes)
        return f"""
{{
    Tools = ordered() {{
{body}
    }},
    ActiveTool = "MediaOut1"
}}
"""


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

if __name__ == "__main__":
    inkSplashCount = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    framesCount = int(sys.argv[2]) if len(sys.argv) > 2 else 240

    generator = InkSplashGenerator(inkSplashCount, framesCount)
    result = generator.generate()

    with open("output.setting", "w") as file:
        file.write(result)

    print("Ink splashes generated successfully.")