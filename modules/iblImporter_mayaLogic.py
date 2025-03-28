import maya.cmds

def create_HDRI(ibl, file, intensity=1, exposure=0):
    import os
    import maya.cmds as cmds

    # Create transform + shape nodes properly
    skydome_transform = cmds.createNode("transform", name="LGT_Env_001")
    skydome_shape = cmds.createNode("aiSkyDomeLight", parent=skydome_transform)

    # Set up file texture
    file_path = os.path.join(ibl['path'], file)
    file_node = cmds.shadingNode("file", asTexture=True, name=f"{ibl['name']}_FILE")
    
    # Create blackbody and multiply nodes
    blackbody_node = cmds.shadingNode("aiBlackbody", asUtility=True, name=f"{ibl['name']}_BLACKBODY")
    multiply_node = cmds.shadingNode("aiMultiply", asUtility=True, name=f"{ibl['name']}_MULTIPLY")
    
    # Set attributes
    cmds.setAttr(f"{file_node}.fileTextureName", file_path, type="string")
    cmds.setAttr(f"{file_node}.colorSpace", "scene-linear Rec.709-sRGB", type="string")
    cmds.setAttr(f"{blackbody_node}.normalize", 1)
    # Connect nodes
    cmds.connectAttr(f"{file_node}.outColor", f"{multiply_node}.input1", force=True)
    cmds.connectAttr(f"{blackbody_node}.outColor", f"{multiply_node}.input2", force=True)
    cmds.connectAttr(f"{multiply_node}.outColor", f"{skydome_shape}.color", force=True)
    
    # Configure skydome
    cmds.setAttr(f"{skydome_shape}.intensity", intensity)
    cmds.setAttr(f"{skydome_shape}.exposure", exposure)
    cmds.setAttr(f"{skydome_shape}.camera", 0)  # Disable visibility in renders

    return skydome_transform  # Return transform node for further control

def create_lightMap(ibl, file, intensity=1, exposure=0):
    import os
    import maya.cmds as cmds

    # Create transform + shape nodes properly
    area_light_transform = cmds.createNode("transform", name=f"LGT_{ibl['name']}_001")
    area_light_shape = cmds.createNode("aiAreaLight", parent=area_light_transform)

    # Set up file texture
    file_path = os.path.join(ibl['path'], file)
    file_node = cmds.shadingNode("file", asTexture=True, name=f"{ibl['name']}_FILE")
    
    # Create blackbody and multiply nodes
    blackbody_node = cmds.shadingNode("aiBlackbody", asUtility=True, name=f"{ibl['name']}_BLACKBODY")
    multiply_node = cmds.shadingNode("aiMultiply", asUtility=True, name=f"{ibl['name']}_MULTIPLY")
    
    # Set attributes
    cmds.setAttr(f"{file_node}.fileTextureName", file_path, type="string")
    cmds.setAttr(f"{file_node}.colorSpace", "Raw", type="string")
    
    # Connect nodes
    cmds.connectAttr(f"{file_node}.outColor", f"{multiply_node}.input1", force=True)
    cmds.connectAttr(f"{blackbody_node}.outColor", f"{multiply_node}.input2", force=True)
    cmds.connectAttr(f"{multiply_node}.outColor", f"{area_light_shape}.color", force=True)
    
    # Configure area light
    cmds.setAttr(f"{area_light_shape}.intensity", intensity)
    cmds.setAttr(f"{area_light_shape}.exposure", exposure)
    cmds.setAttr(f"{area_light_shape}.aiCamera", 0)  # Disable visibility

    return area_light_transform  # Return transform node for further control

def create_light(ibl, file, intensity, exposure):
    if ibl['itemType'] == "HDRI":
        create_HDRI(ibl, file, intensity, exposure)
    if ibl['itemType'] == "Lightmap":
        create_lightMap(ibl, file, intensity, exposure)