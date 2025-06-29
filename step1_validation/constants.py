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

# MetaHuman naming variations that need mapping to Azure blendshapes
# Based on analysis of actual MetaHuman FBX morph target names
METAHUMAN_NAME_MAPPINGS = {
    # Eye blendshapes - MetaHuman uses underscore naming with mesh prefixes
    "head_lod0_mesh__eye_blink_L": "eyeBlinkLeft",
    "head_lod0_mesh__eye_blink_R": "eyeBlinkRight",
    "head_lod0_mesh__eye_lookDown_L": "eyeLookDownLeft",
    "head_lod0_mesh__eye_lookDown_R": "eyeLookDownRight",
    "head_lod0_mesh__eye_lookLeft_L": "eyeLookInLeft",    # Left eye looking left = looking in
    "head_lod0_mesh__eye_lookLeft_R": "eyeLookOutRight",  # Right eye looking left = looking out
    "head_lod0_mesh__eye_lookRight_L": "eyeLookOutLeft",  # Left eye looking right = looking out
    "head_lod0_mesh__eye_lookRight_R": "eyeLookInRight",  # Right eye looking right = looking in
    "head_lod0_mesh__eye_lookUp_L": "eyeLookUpLeft",
    "head_lod0_mesh__eye_lookUp_R": "eyeLookUpRight",
    "head_lod0_mesh__eye_squintInner_L": "eyeSquintLeft",
    "head_lod0_mesh__eye_squintInner_R": "eyeSquintRight",
    "head_lod0_mesh__eye_widen_L": "eyeWideLeft",
    "head_lod0_mesh__eye_widen_R": "eyeWideRight",

    # Jaw blendshapes
    "head_lod0_mesh__jaw_fwd": "jawForward",
    "head_lod0_mesh__jaw_left": "jawLeft",
    "head_lod0_mesh__jaw_right": "jawRight",
    "head_lod0_mesh__jaw_open": "jawOpen",

    # Mouth blendshapes - many variations in MetaHuman
    "head_lod0_mesh__mouth_left": "mouthLeft",
    "head_lod0_mesh__mouth_right": "mouthRight",
    "head_lod0_mesh__mouth_cornerPull_left": "mouthSmileLeft",
    "head_lod0_mesh__mouth_cornerPull_right": "mouthSmileRight",
    "head_lod0_mesh__mouth_cornersUp_L": "mouthSmileLeft",
    "head_lod0_mesh__mouth_cornersUp_R": "mouthSmileRight",
    "head_lod0_mesh__mouth_cornerDepress_L": "mouthFrownLeft",
    "head_lod0_mesh__mouth_cornerDepress_R": "mouthFrownRight",
    "head_lod0_mesh__mouth_cornersDown_L": "mouthFrownLeft",
    "head_lod0_mesh__mouth_cornersDown_R": "mouthFrownRight",
    "head_lod0_mesh__mouth_dimple_left": "mouthDimpleLeft",
    "head_lod0_mesh__mouth_dimple_right": "mouthDimpleRight",
    "head_lod0_mesh__mouth_stretch_left": "mouthStretchLeft",
    "head_lod0_mesh__mouth_stretch_right": "mouthStretchRight",
    "head_lod0_mesh__mouth_lowerLipRollIn_L": "mouthRollLower",
    "head_lod0_mesh__mouth_lowerLipRollIn_R": "mouthRollLower",
    "head_lod0_mesh__mouth_upperLipRollIn_L": "mouthRollUpper",
    "head_lod0_mesh__mouth_upperLipRollIn_R": "mouthRollUpper",
    "head_lod0_mesh__mouth_lipsPress_L": "mouthPressLeft",
    "head_lod0_mesh__mouth_lipsPress_R": "mouthPressRight",
    "head_lod0_mesh__mouth_lowerLipDepress_left": "mouthLowerDownLeft",
    "head_lod0_mesh__mouth_lowerLipDepress_right": "mouthLowerDownRight",
    "head_lod0_mesh__mouth_upperLipRaise_left": "mouthUpperUpLeft",
    "head_lod0_mesh__mouth_upperLipRaise_right": "mouthUpperUpRight",

    # Funnel and pucker - using compound shapes
    "head_lod0_mesh__mouth_funnel_DL": "mouthFunnel",  # Use one of the funnel variants
    "head_lod0_mesh__mouth_lipsPurse_DL": "mouthPucker", # Use one of the purse variants

    # Close mouth - may need to map from lips together
    "head_lod0_mesh__mouth_down": "mouthClose",

    # Brow blendshapes
    "head_lod0_mesh__brow_down_L": "browDownLeft",
    "head_lod0_mesh__brow_down_R": "browDownRight",
    "head_lod0_mesh__brow_raiseIn_L": "browInnerUp",  # Inner raise maps to inner up
    "head_lod0_mesh__brow_raiseIn_R": "browInnerUp",  # Both sides contribute
    "head_lod0_mesh__brow_raiseOuter_left": "browOuterUpLeft",
    "head_lod0_mesh__brow_raiseOuter_right": "browOuterUpRight",

    # Cheek blendshapes - using actual MetaHuman morph names
    "head_lod0_mesh__cheek_blow_cor": "cheekPuff",  # Use cheek blow for puff
    "head_lod0_mesh__EcheekRaise_EsquintInner_L": "cheekSquintLeft",
    "head_lod0_mesh__EcheekRaise_EsquintInner_R": "cheekSquintRight",

    # Nose blendshapes
    "head_lod0_mesh__nose_wrinkle_left": "noseSneerLeft",
    "head_lod0_mesh__nose_wrinkle_right": "noseSneerRight",

    # Tongue blendshape - may be on teeth mesh
    "teeth_lod0_mesh__tongue_out_cor": "tongueOut",

    # Additional variations without prefix (for backwards compatibility)
    "eye_blink_L": "eyeBlinkLeft",
    "eye_blink_R": "eyeBlinkRight",
    "eye_lookDown_L": "eyeLookDownLeft",
    "eye_lookDown_R": "eyeLookDownRight",
    "eye_lookLeft_L": "eyeLookInLeft",    # Left eye looking left = looking in
    "eye_lookLeft_R": "eyeLookOutRight",  # Right eye looking left = looking out
    "eye_lookRight_L": "eyeLookOutLeft",  # Left eye looking right = looking out
    "eye_lookRight_R": "eyeLookInRight",  # Right eye looking right = looking in
    "eye_lookUp_L": "eyeLookUpLeft",
    "eye_lookUp_R": "eyeLookUpRight",
    "eye_squintInner_L": "eyeSquintLeft",
    "eye_squintInner_R": "eyeSquintRight",
    "eye_widen_L": "eyeWideLeft",
    "eye_widen_R": "eyeWideRight",
    "jaw_fwd": "jawForward",
    "jaw_left": "jawLeft",
    "jaw_right": "jawRight",
    "jaw_open": "jawOpen",
    "mouth_left": "mouthLeft",
    "mouth_right": "mouthRight",
    "mouth_cornerPull_left": "mouthSmileLeft",
    "mouth_cornerPull_right": "mouthSmileRight",
    "mouth_cornersUp_L": "mouthSmileLeft",
    "mouth_cornersUp_R": "mouthSmileRight",
    "mouth_cornerDepress_L": "mouthFrownLeft",
    "mouth_cornerDepress_R": "mouthFrownRight",
    "mouth_cornersDown_L": "mouthFrownLeft",
    "mouth_cornersDown_R": "mouthFrownRight",
    "mouth_funnel_DL": "mouthFunnel",  # Use one of the funnel variants
    "mouth_lipsPurse_DL": "mouthPucker", # Use one of the purse variants
    "mouth_down": "mouthClose",
    "brow_down_L": "browDownLeft",
    "brow_down_R": "browDownRight",
    "brow_raiseIn_L": "browInnerUp",  # Inner raise maps to inner up
    "brow_raiseIn_R": "browInnerUp",  # Both sides contribute
    "brow_raiseOuter_left": "browOuterUpLeft",
    "brow_raiseOuter_right": "browOuterUpRight",
    "cheek_puff_L": "cheekPuff",  # If exists
    "cheek_raiseInner_L": "cheekSquintLeft",  # If exists
    "cheek_raiseInner_R": "cheekSquintRight", # If exists
    "nose_wrinkle_left": "noseSneerLeft",
    "nose_wrinkle_right": "noseSneerRight",
    "tongue_out_cor": "tongueOut",

    # Legacy style variations with _L/_R suffixes
    "mouthSmile_L": "mouthSmileLeft",
    "mouthSmile_R": "mouthSmileRight",
    "mouthFrown_L": "mouthFrownLeft",
    "mouthFrown_R": "mouthFrownRight",
    "eyeBlink_L": "eyeBlinkLeft",
    "eyeBlink_R": "eyeBlinkRight",

    # Mouth shrug mappings - using lip roll/towards movements
    "head_lod0_mesh__mouth_lowerLipRollOut_L": "mouthShrugLower",
    "head_lod0_mesh__mouth_lowerLipRollOut_R": "mouthShrugLower",
    "head_lod0_mesh__mouth_upperLipRollOut_L": "mouthShrugUpper",
    "head_lod0_mesh__mouth_upperLipRollOut_R": "mouthShrugUpper",
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
