# 🎭 MetaHuman FBX to GLB Converter (kitr)
Converting MetaHuman FBX files to optimized GLB format for Babylon.js with Azure viseme support.

## 🐳 Quick Start with Docker (Recommended)

The easiest way to get started is using Docker, which includes all dependencies:

```bash
# Build and test the complete setup
docker-compose build metahuman-converter
./docker_test.sh

# Validate your FBX file
cp your-metahuman.fbx input/
docker-compose run --rm metahuman-converter metahuman-convert validate input/your-metahuman.fbx
```

📖 **See [DOCKER_README.md](DOCKER_README.md) for complete Docker documentation and usage examples.**

## Overview

We need a robust CLI pipeline to convert a MetaHuman-exported avatar (FBX format, LOD0) into an optimized GLB ready for Babylon.js with Azure viseme blendshapes. The pipeline will validate the input FBX, standardize its facial blendshape targets to match Azure’s required 55 blendshapes (52 Apple ARKit facial shapes + 3 rotations) ￼ ￼, strip out unnecessary data for performance, convert to glTF/GLB, enforce texture resolution limits, and perform final validations. Each stage must be self-contained, with thorough logging and validation to catch issues early. An orchestrator function will coordinate these steps sequentially, ensuring that each step’s prerequisites are satisfied before moving on. We will use up-to-date tools (as of June 2025) and best practices for 3D asset optimization. The design also emphasizes iterative development – implementing one step at a time with tests – to avoid scope bloat and outdated assumptions.

Step 1: FBX Ingestion & Validation

Goal: Verify the FBX contains all required components for successful conversion. This prevents wasted work on an unsuitable file.
	•	MetaHuman Export Requirements: The FBX should be exported from Unreal Engine 5.5.4 at LOD0 (highest detail). LOD0 includes the full facial rig with all blendshapes; lower LODs may simplify or omit these ￼. The FBX must contain the face mesh (head geometry) skinned to a skeleton (if using one), and all default morph targets. MetaHumans are configured for Apple’s ARKit 52 facial blendshapes ￼ (for expressions/visemes) out-of-the-box, but the FBX might include additional custom or platform-specific shapes (MetaHuman’s internal set can be larger than ARKit’s) ￼.
	•	Morph Targets Presence: Validate that the FBX has the expected facial blendshapes needed for Azure. Specifically, ensure all 52 ARKit-equivalent shape keys are present (e.g. browInnerUp, eyeBlinkLeft, jawOpen, mouthSmile_L, etc.) – whether named exactly as ARKit or with slight naming differences (like “Left” vs “_L” suffix) ￼ ￼. If any of these core shapes are missing, the pipeline should flag an error. Rationale: Azure’s viseme JSON outputs 52 facial shape coefficients in a fixed order ￼ ￼; missing shapes means we can’t drive those expressions on the avatar.
	•	Skeleton/Bones: Check if a skeleton (armature) is present. If the pipeline will incorporate head and eye rotations (for Azure’s last 3 parameters: headRoll, leftEyeRoll, rightEyeRoll ￼), then bones for the head and eyeballs must exist in the FBX. Typically, a MetaHuman FBX includes a full body skeleton with head and eye joints. If we decide to drop the skeleton for simplicity, we must confirm that’s acceptable (e.g. if only facial morphs will be used and slight head/eye movements can be ignored or handled externally). Validation: Ensure either (a) the skeleton exists and includes at least the head bone and eye bones, or (b) we explicitly configure the pipeline to operate skeleton-less (and then skip rotation animation). This choice will be documented and consistent through the pipeline.
	•	Mesh & Vertex Data: Verify the FBX contains the necessary geometry and that vertex counts for all morph targets match the base mesh vertex count (a requirement for morph targets to work ￼ ￼). Also check the face mesh is skinned properly if a skeleton is present. Any severe issues (e.g. no mesh, mismatched vertex counts, etc.) should abort the process early with clear error logs.
	•	Materials and Textures: Ensure that materials and textures can be extracted. The FBX should include material assignments and either embed textures or reference image files. We don’t need to validate resolution here (that happens in Step 5), but we should note if textures are missing or paths invalid. Also confirm the number of materials is reasonable (MetaHuman characters have numerous material slots, but since we plan to limit texture resolution later, multiple materials are acceptable as long as each is <=1K texture).
	•	Unit/Axis Conventions: Record the FBX’s unit scale and axis orientation (Unreal uses centimeters, Z-up, left-handed coordinate). The fbx2gltf converter typically handles converting to glTF’s coordinate system (meters, Y-up, right-handed) automatically, but any unusual transforms (e.g. if the mesh is rotated or scaled on export) should be detected. We can log the root node transform and warn if a significant rotation/scale is present (to ensure the final avatar isn’t misoriented in Babylon).

Validation Implementation: We will likely use a library or API to parse the FBX. Options include the Autodesk FBX SDK (for direct FBX parsing in Python/C++), or converting to an intermediate format for inspection. For efficiency and simplicity, an approach is to first run fbx2gltf (or another converter) in a dry-run to inspect output data. However, it’s safer to directly validate the FBX if possible before conversion. We might use a minimal FBX parser library or a headless Blender invocation to list blendshape names and bone names. Logging should enumerate the found blendshape names and bones, and explicitly list any missing required shape (e.g. “ERROR: required morph target ‘mouthSmileLeft’ not found”) before halting. If all looks good, proceed.

Key Requirements for Step 1 (FBX):
	•	Contains high-detail head mesh with 52+ blendshapes (should match ARKit set).
	•	Contains skeleton with head/eye bones (if rotations to be supported).
	•	All morph targets have correct vertex counts and reasonable default naming (no duplicates, etc.).
	•	Materials present (with textures) and no other showstoppers.

Step 2: Generate/Map Azure Blendshape Set (55 Morph Targets)

Goal: Ensure the avatar has exactly the 55 blendshape controls expected by Azure’s 3D viseme output. This means configuring 52 ARKit-compatible facial morph targets + 3 rotational values for head and eyes ￼. In practice, MetaHuman FBX may include many more than 52 morph targets (potentially hundreds of corrective shapes). We need to distill or create the required 55.
	•	Identifying ARKit 52 Shapes: Using the validation info from Step 1, filter the morph targets to find the ARKit 52 shapes. MetaHuman’s default naming likely aligns closely with ARKit’s naming scheme ￼, though some names might use a different convention (for example, “Left” vs “_L”). We will create a mapping of expected ARKit names to the actual FBX morph names if they differ. For instance: map "mouthSmileLeft" to "mouthSmile_L" if needed, similarly "eyeBlinkRight" to "eyeBlink_R", etc. This mapping can be coded as a dictionary and verified against the FBX. All 52 keys should be found. If any are missing, we decide either to fail (since missing shapes means incomplete viseme support) or to skip those shapes (which would reduce viseme accuracy). Ideally, since MetaHumans are designed for ARKit, all should be present ￼.
	•	Creating Missing Shapes (if needed): In case some required blendshape is not directly present, consider if it can be derived. For example, if the FBX had separate “mouthSmileLeft” and “mouthSmileRight” but missing a combined “mouthSmile” (just hypothetical), we could combine left+right if needed. However, since Azure specifically lists separate left/right shapes, we likely won’t need to fuse shapes. Another example: if tongueOut is missing (some older rigs lacked it ￼), we might skip it or approximate it using any available tongue/jaw shapes. Given “Exact is best” but scope shouldn’t balloon, our approach is: do not attempt complex generation of new shapes that require artistry or unknown mappings. We will rely on the MetaHuman providing these shapes. If a shape is absent, log a warning and continue (or fail if it’s critical).
	•	Include Head/Eye Rotations: The Azure viseme output’s last three values are headRoll, leftEyeRoll, rightEyeRoll (which represent rotational movement, not traditional morph targets) ￼ ￼. We have two possible ways to handle these:
	1.	Use Skeleton Bones: The preferred method is to use the avatar’s skeleton. We will not create actual morph targets for these, since rotation is better handled by bone transforms. Instead, we ensure that the final GLB has a bone for the head and each eyeball. During animation, we can interpret Azure’s headRoll and eyeRoll values as rotation angles to apply to these bones in Babylon.js. This approach requires keeping the skeleton (at least the head and eye bones) through the pipeline.
	2.	Morph Targets as Rotations (Not Typical): Alternatively, one could create pseudo-morph-targets that rotate the head/eyes. This is uncommon and not recommended because rotating a head via blendshape would distort the mesh rather than truly rotate it. We will avoid morph targets for rotations. Instead, document that the client application (Babylon.js) should apply these 3 values by rotating the corresponding nodes or bones.
	•	Renaming for Consistency: To avoid confusion, we will standardize the final 52 morph target names to exactly match Azure’s specification (which mirrors ARKit names in camelCase) ￼ ￼. For example, if the FBX had "mouthSmile_L", we can rename it to "mouthSmileLeft". This makes it straightforward to map Azure’s JSON indices to the model’s morphs by name. Renaming can be done via the glTF layer (after conversion, by editing the glTF JSON) or possibly by instructing the conversion process to use the FBX blendshape names (some converters keep original names). We must ensure renaming doesn’t break anything (the indices in the glTF primitives’ targets should follow the new name mapping).
	•	Validation: After identifying or renaming shapes, verify we have exactly 52 facial blendshape entries. Any extra blendshape present in the model at this point (e.g. MetaHuman-specific correctives not in the ARKit list) should be marked for removal in the next step. We will prepare a list of morph targets to remove (the complement of the needed 52). Also, record the index or identity of the head/eye bones for later use (so we know which bones correspond to left/right eye and head for animation).
	•	Performance Note: Reducing from ~800 generic morphs to 52 will drastically lighten the asset’s morph data and memory footprint, improving runtime performance. Since performance is king, focusing only on the needed morphs is critical.

Output of Step 2: A mapping or confirmation that the model’s morph targets now include the 52 ARKit/Azure shapes (named consistently). No new .fbx is exported yet – this is more a data preparation step. If we are manipulating the data in-memory or via an intermediate format (like glTF or Blender), those changes (renaming, selection) will be applied in the next step.

Step 3: Clean Up Unneeded Morphs and Skeleton Data

Goal: Remove any data not required for our use-case, to optimize the GLB’s size and complexity. This step finalizes the set of morph targets and optionally prunes the skeleton or other components.
	•	Remove Unused Morph Targets: All morph targets not in the chosen 52-set should be stripped away. This includes any MetaHuman-specific shapes that are not part of ARKit visemes (for example, if MetaHuman had extra corrective shapes or expressions beyond the ARKit standard). By the end, the face mesh should have exactly those 52 morph target channels (plus we will account for the rotation parameters separately). Removing morph targets can be done by editing the glTF after conversion (deleting target entries and their data from the mesh) or by instructing a tool in the pipeline to exclude them. If using Blender or FBX SDK, one could delete the shape keys before export. If using glTF, one must carefully remove references in the JSON (meshes.primitives.targets arrays and corresponding accessors). This step will be validated by counting morph targets in the output.
	•	Skeleton Optimization: Determine if the skeleton is needed going forward:
	•	If we plan to use head/eye bone rotations, we must keep at least part of the skeleton (the head and eye bones, and any parent hierarchy up to the root for proper transformation). We could remove other bones not related to facial movement (e.g. body bones) if the body will remain static or not used. However, be cautious: removing bones that have weighted vertices without re-binding those vertices can break the mesh. If the avatar is full-body and we want to keep it posed, one approach (if skeleton removal is desired) is to apply the skeleton’s bind pose to the mesh (bake the vertex positions) and then remove the skeleton entirely. But that would make a static mesh (no body animation possible and no head rotation either unless we treat the head as a separate node).
	•	If we decide that no skeleton is required (e.g. perhaps the avatar will only be used from the neck up as a talking head, or slight head/eye movements are not important), we can remove the skeleton completely. In this case, the mesh will become a static mesh with just morph targets. We should then also remove any bone influences from the mesh (i.e. drop skinning). This simplifies the GLB, but we lose the ability to rotate head/eyes via bone. This trade-off must be clearly understood from the start. Given Azure’s output includes head and eye motion, it’s likely we want those; so the recommended approach is to keep the skeleton at least for the head and eyes.
	•	Prune Hierarchy (Conditional): If keeping the skeleton, consider trimming any bones that are truly unnecessary. For example, if the MetaHuman skeleton has dozens of facial bones (for fine controls that we are now replacing with morph targets), those could potentially be removed to avoid confusion and slight performance overhead. However, removing selective bones in the middle of a hierarchy is risky if other parts depend on them. We might opt to keep the skeleton intact except possibly physics or IK bones that have no influence. This is a delicate area; to avoid error, we might choose not to prune individual bones unless we are certain they have no weighted vertices. Logging can list all bones and maybe flag those with zero vertex influence (which could be safely removed).
	•	Geometry and Mesh: If the FBX included multiple meshes (e.g. separate head and body), evaluate if both are needed. For a Babylon.js avatar, we likely want the full body present for visual completeness, even if only the face animates. We should keep the body mesh but note that it might have its own morphs (MetaHuman bodies sometimes have morphs for body shape, etc.). If those exist and are irrelevant (e.g. “BodyMuscle” morphs), remove those too to keep the GLB lean. Essentially, any morph target not used for facial animation should be removed across all meshes. The body can still be animated via skeleton if needed (or remain static). We should also remove any dummy objects or cameras/lights that Unreal might have exported (unless needed). Only the skeletal mesh and necessary nodes should remain.
	•	Validation: After cleanup, run checks:
	•	Count of morph targets on the face mesh == 52. Log their names to ensure they match the Azure list ￼ ￼ (from eyeBlinkLeft through tongueOut).
	•	Verify that if skeleton is kept, the key bones (head and eyes) are still present and skinned. If skeleton was removed, verify that the mesh still looks correctly posed and that no weighted vertices are left untransformed.
	•	If multiple meshes, ensure no references to removed bones or morphs remain (the glTF validator can catch dangling references).

By the end of Step 3, the avatar data is streamlined: only essential morph targets and bones remain. This setup is much lighter and should animate correctly with Azure’s viseme data. (For example, first 52 blendshape values drive the morph targets directly, and the last 3 values can drive bone rotations, as noted in Step 2 ￼.)

Step 4: Convert FBX to glTF/GLB

Goal: Use the FBX2glTF tool (or similar) to convert the cleaned avatar into a GLB file, which is the format to be used with Babylon.js. We perform this after ensuring the FBX is properly set up to avoid conversion issues.
	•	Tool Selection: We will use the FBX2glTF command-line tool (Facebook’s open-source converter) for the conversion. FBX2glTF is a proven utility that supports skeletal meshes and morph targets (blendshapes) conversion to glTF 2.0 format ￼ ￼. Using the latest version (as of 2025) is important to avoid bugs with newer FBX features. The tool can output a binary .glb or a .gltf + binary buffer; we prefer .glb for a single-file asset.
	•	Conversion Execution: We’ll call FBX2glTF via a subprocess from our orchestrator. Key CLI options to use:
	•	--binary: output as .glb (binary glTF).
	•	--keep-attribute position,normal,uv0 (optional) to drop any unnecessary vertex attributes. We might only keep base attributes and perhaps one UV set. If MetaHuman exports color attributes or extra UVs we don’t need, dropping them can save space ￼.
	•	--blend-shape-normals and --blend-shape-tangents: decide whether to include them. Including blendshape normals can improve visual fidelity when morphing (if the shapes drastically change surface orientation), but it increases file size. Babylon.js can recompute normals if needed, so we might skip these for size unless the face animation looks off without them.
	•	We likely do not use Draco compression at this stage (no --draco), because we want to inspect and possibly modify the glTF JSON easily in subsequent steps. Draco would complicate editing. We can compress later if needed.
	•	Coordinate System: FBX2glTF should handle conversion from FBX’s coordinate system to glTF’s (Y-up). We should test that the avatar isn’t mirrored or rotated oddly. If needed, FBX2glTF has options to adjust axes (though typically it auto-detects). We can use a small test (like ensuring the model’s forward direction is correct in a glTF viewer or Babylon).
	•	Material Conversion: Use --pbr-metallic-roughness to let the tool attempt converting FBX materials to glTF PBR. MetaHuman materials are complex, but we can’t fully reproduce Unreal shaders in glTF. At minimum, the skin, hair, etc., will convert with textures (albedo, normal, etc.) into a rough PBR approximation. We accept this, as fine visual fidelity is not the primary concern. We mainly need a reasonable appearance and the facial animation working. Ensure the converter inlines or references the texture files correctly. We might use --embed (embed textures in the glTF) to produce a self-contained glb (FBX2glTF by default embeds binary data in .glb automatically if using --binary).
	•	Post-conversion Verification: After running the conversion, we will have a GLB file. We should verify:
	•	The GLB loads without errors (we can use the official Khronos glTF Validator or simply attempt to load it in a Babylon.js or Three.js test).
	•	The count and names of morph targets in the glTF match what we expect (52). This can be done by parsing the glTF or by using Babylon.js to read the morphTargetManager on the mesh at runtime. We can also open the GLB in a viewer that lists blendshapes.
	•	The skeleton (if kept) is present and bones are correctly influencing the mesh. We might check if the head bone can rotate the head (if we have a quick way to test, e.g., by manually editing the glTF node transform for the head or using Babylon to rotate it).
	•	No extraneous nodes: sometimes conversion might include a root dummy node or lights/cameras if present. If found, they can be removed (either by re-running conversion with different settings or by editing the glTF nodes in code).

Logging for this step should capture the FBX2glTF command output (with --verbose flag to get details). If conversion fails (e.g., FBX SDK error), log the error and possibly suggest checking FBX integrity manually. Once conversion succeeds, log summary: number of meshes, materials, morph targets, etc., in the GLB.

Step 5: Enforce Texture Resolution ≤ 1K

Goal: Ensure no texture in the GLB exceeds 1024x1024 resolution, to optimize for web performance. High-res textures (2K, 4K) greatly increase load times with diminishing returns in a real-time engine ￼ ￼. We will downscale any large textures.
	•	Identify Textures: Parse the GLB to find all embedded textures. In the glTF structure, images are typically listed in an “images” array. We can extract each image (which might be stored as a data URI or as binary buffer). Using an image processing library (e.g., Pillow in Python or Sharp in Node), open each image and check its dimensions.
	•	Resize Logic: For each texture:
	•	If both width and height are <= 1024, no change needed (keep as is).
	•	If larger, compute a scaling factor to bring the larger dimension down to 1024, preserving aspect ratio (e.g., a 2048x2048 becomes 1024x1024; a 2048x1024 becomes 1024x512).
	•	Resize using a high-quality downsampling filter to minimize aliasing. We might choose bilinear or Lanczos filtering for good results.
	•	Replace the image in the glTF. In a GLB, this means updating the binary blob for that image. Easiest method: use a glTF library (like gltf-transform or pygltflib) to replace images, or manually edit if comfortable: adjust the image data and update the bufferView lengths accordingly.
	•	Consider Format and Compression: We will maintain the same image format (e.g., if the original was JPEG or PNG). However, if many textures are PNG with alpha but don’t need alpha, converting to JPEG could save space – this might be beyond scope unless easily done. We won’t introduce advanced texture compression (like KTX2 with Basis) to keep the pipeline simple, but note it as a future enhancement for performance. Our main focus is resolution downscaling now.
	•	Validation of Textures: After resizing, iterate through images again and assert none exceed 1024 in either dimension. Log each texture’s name (or index) and new resolution. Also observe file size changes – reducing textures can significantly cut the GLB size. For example, downscaling from 4K to 1K reduces pixel count by ~16x (and often file size by similar factor if format constant).
	•	Performance Rationale: According to real-world guidance, 1K textures are usually sufficient for avatars on web and help with load times on slow connections ￼ ￼. Larger textures (2K, 4K) can cause noticeable delays and memory overhead with minimal visual gain on typical display sizes. By enforcing 1K, we ensure a balance of quality and performance.

If any textures were modified, we should save the GLB with those changes. The pipeline should be careful with GLB binary packing when altering images (to not corrupt offsets). A safer route is to use a library that can rewrite the GLB correctly after changes. We will likely use gltf-transform CLI (with the resize command) as an alternative: for instance, gltf-transform resize --width 1024 --height 1024 input.glb output.glb can automate resizing all textures to a max dimension. This tool is up-to-date and reliable.

Step 6: Final GLB Validation and Babylon.js Compatibility

Goal: Confirm that the resulting .glb is fully ready for use: structurally sound, and compatible with Babylon.js’s requirements for animation.
	•	glTF Validation: Run the GLB through the official glTF Validator (available as a CLI or online). This will catch any errors such as missing references, invalid buffer lengths, non-standard extensions, etc. We expect a clean validation since we controlled the process. Any warnings (like image dimension not a power of two – 1024 is power of two, so fine) or info messages can be reviewed. Ensure no error-level issues.
	•	Babylon.js Test Load: If possible, perform a quick load of the GLB in Babylon.js (this can be part of an automated test or a manual step). Using Babylon.js’s SceneLoader, import the GLB and check:
	•	The mesh appears correctly (not invisible or distorted).
	•	Materials render (textures show up, roughly correct looking).
	•	Morph targets are accessible. In Babylon, when a mesh with morph targets is loaded, it creates a MorphTargetManager. We can programmatically verify that manager has 52 targets with the expected names. For example:

const mesh = scene.getMeshByName("FaceMesh"); 
mesh.morphTargetManager.numTargets === 52;
console.log(mesh.morphTargetManager.getTarget(0).name);

This should list names like “eyeBlinkLeft”, etc.

	•	Skeleton (if present): Check that the skeleton is loaded (scene.skeletons array, or mesh.skeleton). Ensure bones like “head” or “HeadBone” exist. We can also try rotating those bones via Babylon’s API and ensure the mesh moves (which would confirm skinning is working). For eyes, similarly, ensure the eye bones are there.

	•	Azure Blendshape Compatibility: Do a dry run with Azure’s viseme output to ensure mapping is correct. For example, construct a dummy viseme frame where each of the 55 blendshape coefficients is set to some test value (like 1.0 or 0.5 one at a time) and apply it:
	•	For indices 0–51, find the morph target with the corresponding name and set its weight to the coefficient. In Babylon, if names match, we can map by name or ensure the index ordering matches Azure’s order ￼. We have the official order from Azure documentation ￼ ￼, which we followed for naming. We should double-check that the ordering of targets in the GLB is the same as this list; if not, we’ll create a name-index map in our application code. (glTF does not inherently order morph targets by name, only by their order in the file, so we may want to reorder them in the glTF to match the Azure order exactly. Alternatively, always access by name.)
	•	For the last 3 values (index 52–54), apply those to the skeleton: e.g. rotate head bone around vertical axis (for headRoll – assuming that refers to head nod or tilt, we might need to confirm the axis; Azure likely defines headRoll as rotation around forward axis (roll) ￼, not yaw or pitch. We must clarify: if “headRoll” corresponds to turning head side to side or tilting ear to shoulder. Given the term roll, it might mean tilting the head (like ear toward shoulder). We should test a known viseme JSON from Azure or documentation for how headRoll changes. We can assume it’s one of the Euler angles).
	•	Check that extreme values don’t distort incorrectly (e.g., applying mouthOpen = 1.0 fully opens the jaw as expected, etc.). If something looks off, it might indicate a morph target sign issue or a missing corrective shape; however, since these are standard shapes from MetaHuman, they should behave correctly.
	•	Extensive Logging: At this final stage, output a summary: “Final GLB ready. X vertices, Y triangles, 52 morph targets (names listed), skeleton with Z bones (head bone kept: Yes/No), total size N MB, textures M count (max resolution 1024). Validated for Babylon.js.” This gives a quick overview to a developer or QA person that the asset meets the criteria.
	•	Automated Tests: Incorporate checks as unit or integration tests where feasible:
	•	A test that runs the validator on the GLB and asserts no errors.
	•	A test that loads the GLB in a minimal Babylon.js scene (perhaps using a headless GLTF loader or Node version of Babylon if available) and inspects the morph target count/names.
	•	If writing these in code is complex, at least keep reference expected values (like we know exactly what morph names we expect). We can use a small glTF parser in tests to read the JSON and verify the target names array matches the known list. This ensures future modifications don’t accidentally drop or rename a blendshape.

By completing these validations, we ensure that when this GLB is deployed, it will plug into a Babylon.js app and simply work: the avatar will lip-sync correctly using Azure Cognitive Services’ output, with good performance (lean mesh, moderate texture sizes, no redundant data).

Code Structure and Orchestration

We will implement the pipeline in a clear, modular way:
	•	Orchestrator Function: A top-level function (e.g., convert_fbx_to_glb(fbx_path)) will coordinate the steps. It will log the start of each step, call the corresponding sub-function, and handle errors. This function reflects the overall flow described, making it easy to see the sequence at a glance.
	•	Step Functions: Each major step (validation, morph mapping, cleanup, conversion, texture processing, final validate) will be implemented in its own function or class method. For example: validate_fbx(fbx_path), prepare_blendshapes(data), optimize_skeleton(data), run_fbx2gltf(fbx_path, tmp_gltf_path), resize_textures(gltf_path), final_check(glb_path). The data passing between steps can be done via file paths (e.g., an intermediate glTF file) or an in-memory structure. A simple design is:
	•	Step 1 reads the FBX (maybe via FBX SDK or by conversion to JSON) and returns a Python object with details or simply flags that it’s OK.
	•	Step 2 might not need to output a file but could output a list of required blendshape mappings.
	•	We could combine Steps 2 and 3 by preparing a “configuration” for the conversion: e.g., a list of morphs to keep, a mapping for names. Then feed that into conversion or apply post-conversion.
However, combining 2 and 3 can streamline the implementation: e.g., using Blender or an FBX processing library, we could delete unwanted morphs and then export to glTF in one go. But doing it stepwise is clearer to debug.
	•	Use of External Tools: We’ll incorporate external tools calls in our code:
	•	fbx2gltf will be invoked (ensuring the binary is accessible). Capture its output and error codes.
	•	Possibly gltf-transform for resizing textures (unless we write our own image handling code).
	•	If using Blender in the pipeline (optional approach), we could drive Blender via its Python API to do morph deletion and glTF export. But that introduces a heavy dependency and potential version issues (given Blender 4.4.3 is mentioned, but using Blender means users must have it installed which might not be desired in a CLI tool). The preferred approach is to avoid requiring Unreal or Blender and do operations either with the FBX SDK or on the glTF text.
	•	Logging: Every step function will log what it’s doing and any noteworthy information. For example, validate_fbx will output counts of morphs and list missing ones if any. prepare_blendshapes will log the mapping of names and any shapes removed. run_fbx2gltf will log the exact command run and success/failure. resize_textures will log each texture’s original vs new size ￼. Logging on success is as important as on error, to trace the pipeline’s decisions. Use a consistent format (perhaps timestamps and step identifiers) since this is a long process and debugging it requires knowing which step produced which output.
	•	Error Handling: If any step fails (e.g., conversion fails, validation fails), the orchestrator should catch the exception or error code and log a clear message. Depending on usage, we might want to raise an exception up to CLI level or return an error code from the program. Ensuring partial files are cleaned up (temporary files deleted) is also good practice in error cases.
	•	Performance Considerations: Since performance is crucial, the tool should avoid unnecessary data copies or extremely slow operations:
	•	Using compiled tools (FBX2glTF, gltf-transform) where possible rather than parsing large files in pure Python (which could be slow for heavy meshes).
	•	If modifying glTF JSON, watch out for memory overhead if it’s huge. Possibly stream processing if needed (though likely fine since even a detailed MetaHuman GLB might be a few hundred MB at most).
	•	The pipeline processes one avatar at a time, so that simplifies things (no parallel processing needed, but also means we can allocate memory liberally within one run).
	•	Testing Strategy: Develop tests for each step in isolation:
	•	For validation, create a dummy FBX (or a lightweight stand-in, maybe a glTF converted from known good FBX) where you know how many morphs and test that the validator catches a missing one. Since generating a real FBX in tests is hard, we might abstract the FBX reading so we can inject a fake data structure for tests.
	•	For morph mapping, test the mapping dictionary logic: give it a list of known names and see if it correctly identifies missing ones or renames.
	•	For texture resizing, one can test the image scaling function with a sample image buffer to ensure it outputs the right size.
By keeping functions small (e.g., a function that just takes an image and returns a resized image), we can unit test easily. Heavier integration (like end-to-end converting a small FBX to glb) could be tested if a small FBX sample is included (maybe a simple cube with a couple of morphs).
The key is to have “confidence checkpoints” after each step, as the user requested, so that if a future change breaks something, tests catch it early at the responsible step.

Iterative Development with Cursor AI Agents

To implement this design successfully using Cursor IDE’s AI agents, we’ll follow a disciplined, step-by-step approach. The idea is to let the AI assist with one component at a time, verify it, then proceed – ensuring we always work with up-to-date and correct information. Below are instructions for setting up the development flow and an example prompt to guide the Cursor agent:
	1.	Define the Environment and Tools: Start by specifying the development stack (e.g. Python 3.x with required libraries or Node.js if preferred). Ensure any external tool dependencies (like fbx2gltf and gltf-transform) are noted. For instance, the agent might need to know the command to install or where the binaries are. (In a real scenario, you’d install fbx2gltf manually and ensure it’s in PATH. The AI can be told to assume it’s available via command line.)
	2.	Break Down Tasks: Divide the implementation into the steps outlined:
	•	Step 1: Implement FBX validation logic.
	•	Step 2 & 3: Implement morph target processing (mapping and removal) – these could be combined into one code module since they’re closely related.
	•	Step 4: Implement conversion invocation.
	•	Step 5: Implement texture resizing.
	•	Step 6: Implement final validation (which could just call external validators or do checks).
	•	Additionally, set up logging utility and any data structures needed (like a config of required morph names).
	•	Write tests alongside for critical functions.
	3.	Iterate and Verify: Use Cursor’s agents to code each part, running tests or sample data through them:
	•	After writing validate_fbx, run it on a known sample or a stub that simulates an FBX structure to ensure it correctly identifies problems (since actual FBX parsing may be complex, perhaps initially stub out a fake “FBX reader” that returns a structure of names for testing).
	•	After writing morph mapping, test with a sample list of names (including some that need renaming or are extra) to see if the filtering works.
	•	Only move to the next step when the current one is satisfactory (each step “done” when extensively validated, per requirements).
	4.	Logging and Debug Mode: Instruct the agent to include detailed logging statements. Each function should announce when it starts and confirm what it found/did. For example, after listing morphs: “Found 820 morph targets; 52 match required list, 768 will be removed.” These logs will help in debugging and confirming each stage’s effect.
	5.	Small Commits: Keep each AI generation focused. It’s better to have the agent produce 50-100 lines of correct, tested code than 500 lines at once. Utilize Cursor’s ability to refine prompts. For example:
	•	“Now implement the function to resize textures in the GLB. Use Pillow to open images from a GLB (you may need to extract them via pygltflib). Ensure it only downsizes if larger than 1024 and writes back the binary. Let’s do this step by step.”
	6.	Stay Updated: When the agent might hallucinate outdated tool usage (a known issue), correct it by referencing official docs. For instance, if it uses an outdated API of gltf-transform or FBX2glTF, guide it with up-to-date info (we might feed in snippets from current docs or use the references we gathered, such as Azure’s blendshape list or Avaturn’s guidelines on textures ￼ to reinforce requirements).

Sample Initial Prompt for Cursor Agent

You can use a prompt like the following to initialize the coding session with the AI, incorporating the design decisions and step-by-step plan:

System/Tool Prompt:
You are an expert Python developer and 3D pipeline engineer. We are building a CLI tool to convert a MetaHuman FBX (Unreal 5.5.4, LOD0) into an optimized GLB for Babylon.js, specifically to support Azure Cognitive Services viseme blendshape animation. The pipeline includes:
	1.	FBX validation (check for required 52 ARKit blendshapes, skeleton presence, etc.).
	2.	Morph target processing (retain/rename 52 ARKit blendshapes, drop others).
	3.	Skeleton optimization (possibly remove unused bones or entire armature if not needed).
	4.	Conversion to glTF (using FBX2glTF).
	5.	Texture downscaling to 1K.
	6.	Final validation (glTF integrity and Babylon compatibility).

Requirements:
	•	Write clean, modular Python code with functions for each step.
	•	Use logging extensively to trace progress and issues.
	•	Each step should be thoroughly validated (include unit tests for critical parts).
	•	No interactive tools (no Unreal Editor usage); use available libraries or external CLI tools (fbx2gltf, etc.).
	•	Ensure up-to-date methods (as of 2025) – e.g., use pygltflib or gltf-transform for glTF edits, Pillow for image processing, etc.
	•	Performance is important: avoid loading entire huge files into inefficient structures unnecessarily.

We will proceed step by step. First, implement the FBX validation step (validate_fbx) that checks an FBX file for the presence of a list of required blendshape names and certain bones. For now, you can simulate FBX reading by using a placeholder (we will integrate actual FBX reading later or via a stub). The function should return a structure (or raise) indicating if validation passed and details (like found morph names). Include a test for a case where a required morph is missing.

Let’s start with that.

This initial prompt sets the stage and instructs the agent on the first concrete coding task. After this, you would interact with Cursor’s agent to refine the validate_fbx implementation. Then move on to the next steps, progressively feeding context (e.g., results from previous steps, or new instructions like “Great, now that validation is done, implement the morph filtering using the known ARKit names…”).

By following the design and using the agent in iterative mode, you ensure each part is built on solid ground and the agent stays focused on one piece at a time, reducing the chance of outdated or incorrect assumptions derailing the project. Each iteration can be tested and corrected before moving forward, which aligns with the requirement that “each step must be considered done only when validated extensively.”