"""
Constants for MetaHuman FBX validation and processing.

Contains the 52 ARKit blendshapes required for Azure Cognitive Services
viseme animation and essential bone names for MetaHuman characters.
"""

# The 52 standard ARKit blendshapes required for viseme animation
# These correspond to Apple's ARKit facial expression blend shapes
ARKIT_BLENDSHAPES = [
    # Eye movements
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
    
    # Jaw movements
    "jawForward",
    "jawLeft",
    "jawRight",
    "jawOpen",
    
    # Mouth movements - crucial for visemes
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
    
    # Brow movements
    "browDownLeft",
    "browDownRight", 
    "browInnerUp",
    "browOuterUpLeft",
    "browOuterUpRight",
    
    # Cheek movements
    "cheekPuff",
    "cheekSquintLeft",
    "cheekSquintRight",
    
    # Nose movements  
    "noseSneerLeft",
    "noseSneerRight",
    
    # Tongue (if supported)
    "tongueOut"
]

# Essential bones that should be present in a MetaHuman rig
# These are commonly found in MetaHuman characters
REQUIRED_BONES = [
    "root",
    "pelvis", 
    "spine_01",
    "spine_02", 
    "spine_03",
    "neck_01",
    "head",
    
    # Eyes (important for gaze tracking)
    "FACIAL_L_Eye",
    "FACIAL_R_Eye",
    
    # Jaw (important for mouth animation)
    "FACIAL_C_FacialRoot",
    "FACIAL_C_Jaw",
    
    # Optional but common arm bones
    "clavicle_l",
    "clavicle_r",
    "upperarm_l", 
    "upperarm_r"
]

# Minimum required bones (core skeleton)
CORE_REQUIRED_BONES = [
    "root",
    "pelvis",
    "spine_01", 
    "head",
    "FACIAL_C_FacialRoot"
]