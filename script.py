#Tested with Blender 3.2.2

"""
What is this?
A work-in-progress free alternative to Node Preview https://www.blendermarket.com/products/node-preview

How does it work
Creates a plane and camera
Copies the actively selected object's material to the new plane
Loops through each linked node output in the shader editor, attaches it to the material output node and renders, creating previews of each node output

How do I use this?
In the 3D viewport select an object with a material you would like to view.
Paste this code in Blender's text editor and click the text editor's RUN (right facing arrow) button.
Each output will be saved separately to "/tmp" 
"""

import bpy
import os

original_object = bpy.context.active_object
if original_object.active_material == None:
    print("Error: No selected object / material missing.")
    raise KeyboardInterrupt()

#Scene Setup Guide
#https://spltech.co.uk/blender-3d%E2%80%8A-%E2%80%8Ahow-to-create-and-render-a-scene-in-blender-using-python-api/

#setup plane
bpy.ops.mesh.primitive_plane_add(size=2)
new_object = bpy.context.active_object
new_object.name = "new_object"
new_object.location[2] = -0 #-100
new_object.active_material = original_object.active_material.copy() #Need to delete this copy after running.

#setup camera
cam_data = bpy.data.cameras.new('camera')
new_cam = bpy.data.objects.new('camera', cam_data)
bpy.context.collection.objects.link(new_cam)
scene = bpy.context.scene
scene.camera=new_cam
new_cam.name = "new_cam"
new_cam.location[2] = 4 #-96

originalRes_X = scene.render.resolution_x
originalRes_Y = scene.render.resolution_y
scene.render.resolution_x = 256
scene.render.resolution_y = 256

#adding new node example
#emissionNode = node_tree.nodes.new('ShaderNodeAddShader')
#emissionNode.location = (100,100)

def render(o):
    #https://stackoverflow.com/a/10017169
    chars_to_remove = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    dd = {ord(c):None for c in chars_to_remove}
    filename = str(o).translate(dd)
    
    scene.render.filepath ='/tmp/' + filename
    bpy.ops.render.render(write_still=1)

node_tree = new_object.active_material.node_tree
matOutputSocket = node_tree.nodes['Material Output'].inputs['Surface']

"""
hid_objects = []
for obj in bpy.context.collection.objects:
    if obj.hide_render == False:
        obj.hide_render = True
        hid_objects.append(obj)
new_object.hide_render=False
"""

for n in node_tree.nodes:
    for output in n.outputs:
        if output.is_linked:
            node_tree.links.new(output, matOutputSocket)
            render(output)

#for obj in hid_objects:
#    obj.hide_render = False

#https://blender.stackexchange.com/questions/249902/blender-python-select-object
def select_one_object(obj):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

#Delete the temp camera and plane when not debugging
#bpy.data.objects.remove(new_cam) 
#bpy.data.objects.remove(new_object) 

select_one_object(original_object) #reselect the original active object

scene.render.resolution_x = originalRes_X
scene.render.resolution_y = originalRes_Y
print("SUCCESS")
