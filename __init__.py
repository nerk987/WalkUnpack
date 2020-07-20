# ##### BEGIN GPL LICENSE BLOCK #####
#
#  WalkUnpack.py  -- Unpack a walk cycle
#  by Ian Huish (nerk)
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Addon Actions
# 1. Pre-req armature selected root bone animated
# 2. Enter name of walk cycle action and the desired range, and the walk cycle axis, and walk cycle period and stride
# 3. Create new action, and 
# 4. Determine all bones which have both keyframes and have root as a parent
# 5. Walk the root bone animation through the range and record matrix for each frame
# 6. Walk through fcurves, and for all relevant bones, add root bone delta to each keyframe    

# version comment: V0.0.1 pre-Alpha

bl_info = {
    "name": "WalkUnpack",
    "author": "Ian Huish (nerk)",
    "version": (0, 0, 1),
    "blender": (2, 81, 0),
    "location": "Toolshelf>WalkUnpack",
    "description": "Unpack a walk cycle",
    "warning": "",
    "category": "Animation"}
    

if "bpy" in locals():
    import imp
    imp.reload(WalkUnpack)
else:
    from . import WalkUnpack

import bpy
# import mathutils,  math, os
from bpy.props import FloatProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
# from random import random
from bpy.types import Operator, Panel, Menu
# from bl_operators.presets import AddPresetBase
# import shutil




class WUProps(bpy.types.PropertyGroup):
    wu_targetrig : StringProperty(name="Name of the target rig", default="")  
    wu_start_frame : IntProperty(name="Simulation Start Frame", default=1)  
    wu_end_frame : IntProperty(name="Simulation End Frame", default=250)  
    wu_cycle_dist : FloatProperty(name="Distance traveled by static walk cycle", default=1.0)  
    wu_start_cycle : IntProperty(name="Static Walk cycle Start Frame", default=1)  
    wu_end_cycle : IntProperty(name="Static Walk cycle End Frame", default=24)  
    wu_cyclic_action : StringProperty(name="Name of the cyclic action", default="")  
    wu_prog_action : StringProperty(name="Name of the progressive action", default="")  
   




class ARMATURE_PT_WalkUnpackPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "WalkUnpack"
    # bl_idname = "armature.walkunpackdpanel"
    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "data"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "WalkUnpack"
    


    @classmethod
    def poll(cls, context):
        if context.object != None:
            return (context.mode in {'OBJECT', 'POSE'}) and (context.object.type == "ARMATURE")
        else:
            return False

    def draw(self, context):
        layout = self.layout

        # obj1 = context.object
        scene = context.scene
        
        # box = layout.box()
        layout.label(text="Main1")
        # layout.prop(scene.WUProps, "wu_start_frame")
        # layout.prop(scene.WUProps, "wu_end_frame")
        layout.prop(scene.WUProps, "wu_start_cycle")
        layout.prop(scene.WUProps, "wu_end_cycle")
        layout.prop(scene.WUProps, "wu_cycle_dist")
        layout.operator('armature.walkunpack')
        layout.operator('armature.walkunpackrevert')

classes = (
    WUProps,
    ARMATURE_PT_WalkUnpackPanel,
    WalkUnpack.ARMATURE_OT_WalkUnpack,
    WalkUnpack.ARMATURE_OT_WalkUnpackRevert,
)        

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.WUProps = bpy.props.PointerProperty(type=WUProps)
    # from . import WalkUnpack
    # WalkUnpack.registerTypes()
    


def unregister():
    del bpy.types.Scene.WUProps
    # from . import WalkUnpack
    # WalkUnpack.unregisterTypes()
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()

