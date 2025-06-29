"""
Constants for MetaHuman FBX validation.
Contains the required Azure/ARKit blendshape names, bone requirements, and input FBX blendshapes.
"""

# Azure Cognitive Services expects these 52 ARKit-compatible facial blendshapes
# plus 3 rotation parameters (headRoll, leftEyeRoll, rightEyeRoll)
# Reference: Azure Cognitive Services documentation for 3D viseme output
AZURE_BLENDSHAPES = [
    # Eye blendshapes
    "eyeBlinkLeft",
    "eyeLookDownLeft",
    "eyeLookInLeft",
    "eyeLookOutLeft",
    "eyeLookUpLeft",
    "eyeSquintLeft",
    "eyeWideLeft",
    "eyeBlinkRight",
    "eyeLookDownRight",
    "eyeLookInRight",
    "eyeLookOutRight",
    "eyeLookUpRight",
    "eyeSquintRight",
    "eyeWideRight",

    # Jaw blendshapes
    "jawForward",
    "jawLeft",
    "jawRight",
    "jawOpen",

    # Mouth blendshapes
    "mouthClose",
    "mouthFunnel",
    "mouthPucker",
    "mouthLeft",
    "mouthRight",
    "mouthSmileLeft",
    "mouthSmileRight",
    "mouthFrownLeft",
    "mouthFrownRight",
    "mouthDimpleLeft",
    "mouthDimpleRight",
    "mouthStretchLeft",
    "mouthStretchRight",
    "mouthRollLower",
    "mouthRollUpper",
    "mouthShrugLower",
    "mouthShrugUpper",
    "mouthPressLeft",
    "mouthPressRight",
    "mouthLowerDownLeft",
    "mouthLowerDownRight",
    "mouthUpperUpLeft",
    "mouthUpperUpRight",

    # Brow blendshapes
    "browDownLeft",
    "browDownRight",
    "browInnerUp",
    "browOuterUpLeft",
    "browOuterUpRight",

    # Cheek blendshapes
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",

    # Nose blendshapes
    "noseSneerLeft",
    "noseSneerRight",

    # Tongue blendshape
    "tongueOut"
]

# The three rotation parameters that Azure outputs (indices 52-54)
AZURE_ROTATIONS = [
    "headRoll",      # Head tilt rotation
    "leftEyeRoll",   # Left eye rotation
    "rightEyeRoll"   # Right eye rotation
]

# Total number of parameters Azure outputs: 52 blendshapes + 3 rotations = 55
TOTAL_AZURE_PARAMETERS = len(AZURE_BLENDSHAPES) + len(AZURE_ROTATIONS)

# MetaHuman naming variations that might need mapping
METAHUMAN_NAME_MAPPINGS = {
    # Common variations MetaHuman might use
    "mouthSmile_L": "mouthSmileLeft",
    "mouthSmile_R": "mouthSmileRight",
    "mouthFrown_L": "mouthFrownLeft",
    "mouthFrown_R": "mouthFrownRight",
    "eyeBlink_L": "eyeBlinkLeft",
    "eyeBlink_R": "eyeBlinkRight",
    # Add more mappings as needed when processing actual MetaHuman FBX files
}

# The complete list of blendshapes (morph targets) expected in the original MetaHuman FBX input.
# This contains 823 blendshapes that can be dynamically extracted from the input file.
# For validation purposes, we check that the input contains at least these core blendshapes.
# The full list can be obtained by calling extract_all_blendshapes() from step2 morph processor.
EXPECTED_INPUT_BLENDSHAPE_COUNT = 823

# Required bones for head and eye rotations
REQUIRED_BONES = [
    "head",
    "Head",
    "HeadBone",
    "leftEye",
    "LeftEye",
    "left_eye",
    "rightEye",
    "RightEye",
    "right_eye"
]
