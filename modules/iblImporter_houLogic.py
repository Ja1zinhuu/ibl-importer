import hou
import os

def create_HDRI(ibl, file, renderer, matNet, intensity=1, exposure=0):
    # Set up file texture
    file_path = os.path.join(ibl['path'], file)
    
    if renderer == "arnold":
        print("creating arnold light")
        obj = hou.node("/obj")
        
        # Create Arnold light
        light = obj.createNode("arnold_light", "LGT_Env_001")
        light.parm("ar_light_type").set(6)  # Skydome light
        light.parm("ar_intensity").set(intensity)
        light.parm("ar_exposure").set(exposure)
        light.parm("ar_light_color_type").set("shader")  # Changed to shader mode
        light.parm("ar_format").set("latlong")  # LatLong ball format
        light.parm("ar_camera").set(0)
        
        
        # Create material network for light shader
        mat_builder = hou.node(matNet).createNode("arnold_materialbuilder", f"LGT_Env_{ibl['name']}_Shader")
        
        # Delete the default material output node
        for child in mat_builder.children():
            if child.type().name() == "arnold_material":
                child.destroy()
        
        # Create light shader node
        light_output = mat_builder.createNode("arnold_light", "light_shader")
        multiply = mat_builder.createNode("arnold::multiply", "multiply1")
        blackbody = mat_builder.createNode("arnold::blackbody", "temperature")
        image = mat_builder.createNode("arnold::image",f"{ibl['name']}")
        blackbody.parm("normalize").set(1)
        image.parm("filename").set(f"{file_path}")
        image.parm("color_family").set("Utility")
        image.parm("color_space").set("Utility - Raw")
        image.parm("autotx").set(0)

        multiply.setInput(0, image)
        multiply.setInput(1, blackbody)

        light_output.setInput(0, multiply)

        

        light.parm("ar_light_color_shader").set(f"../LGT_Shaders/{mat_builder}/{light_output}")


        # Layout nodes
        mat_builder.layoutChildren()
        matNet.layoutChildren()
        obj.layoutChildren()
        
        return light, mat_builder
    
    #ADD SOLARIS


    elif renderer == "solaris":
        print("creating solaris light")
        # Solaris implementation would go here
        return None, None
    


def create_lightMap(ibl, file, renderer, matNet, intensity=1, exposure=0):
    # Set up file texture
    file_path = os.path.join(ibl['path'], file)

    if renderer == "arnold":
        print("creating arnold light")
        obj = hou.node("/obj")
        
        # Create Arnold light
        light = obj.createNode("arnold_light", f"LGT_{ibl['name']}_001")
        light.parm("ar_light_type").set("quad")  # quad light
        light.parm("ar_intensity").set(intensity)
        light.parm("ar_exposure").set(exposure)
        light.parm("ar_light_color_type").set("shader")  # Changed to shader mode
        light.parm("ar_camera").set(0)
        
        
        # Create material network for light shader
        mat_builder = hou.node(matNet).createNode("arnold_materialbuilder", f"LGT_{ibl['name']}_Shader")
        
        # Delete the default material output node
        for child in mat_builder.children():
            if child.type().name() == "arnold_material":
                child.destroy()
        
        # Create light shader node
        light_output = mat_builder.createNode("arnold_light", "light_shader")
        multiply = mat_builder.createNode("arnold::multiply", "multiply1")
        blackbody = mat_builder.createNode("arnold::blackbody", "temperature")
        image = mat_builder.createNode("arnold::image",f"{ibl['name']}")
        blackbody.parm("normalize").set(1)
        image.parm("filename").set(f"{file_path}")
        image.parm("color_family").set("Utility")
        image.parm("color_space").set("Utility - Raw")
        image.parm("autotx").set(0)

        multiply.setInput(0, image)
        multiply.setInput(1, blackbody)

        light_output.setInput(0, multiply)

        

        light.parm("ar_light_color_shader").set(f"../LGT_Shaders/{mat_builder}/{light_output}")

        matNet_path = hou.node(matNet)
        

        # Layout nodes
        mat_builder.layoutChildren()
        matNet_path.layoutChildren()
        obj.layoutChildren()
        
        return light, mat_builder

def create_matNet_for_lights():
    nodepath = "/obj/LGT_Shaders"
    if hou.node(nodepath) is None:
        node = hou.node("/obj").createNode("matnet", "LGT_Shaders")
    else:
        node = hou.node(nodepath)
    return node.path()  # Return path instead of node object

def create_light(ibl, file, renderer, intensity=1, exposure=0):
    matNet = create_matNet_for_lights()
    
    if ibl['itemType'] == "HDRI":
        return create_HDRI(ibl, file, renderer, matNet, intensity, exposure)
    elif ibl['itemType'] == "Lightmap":
        return create_lightMap(ibl, file, renderer, matNet, intensity, exposure)