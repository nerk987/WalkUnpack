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

# version comment: V0.1.2 released (euler issue fix)

bl_info = {
    "name": "WalkUnpack",
    "author": "Ian Huish (nerk)",
    "version": (0, 1, 2),
    "blender": (2, 91, 0),
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
    def GetActions(self, context):
        items = []
        if len(bpy.data.actions) > 0:
            for action in bpy.data.actions:
                items.append((action.name, action.name, action.name))
        else:
            items = [("No action","No action","No action")]
        return items
        
    wu_targetrig : StringProperty(name="Name of the target rig", default="")  
    wu_start_frame : IntProperty(name="Limit Start of Range", description="Limit the target animation range (0 is disabled)", default=0)  
    wu_end_frame : IntProperty(name="Limit End of ange", description="Limit the target animation range (0 is disabled)", default=0)  
    wu_cycle_dist : FloatProperty(name="Walk Cycle Distance", description="Distance traveled by static walk cycle", default=1.0)  
    wu_start_cycle : IntProperty(name="Walk Cycle Start Frame", description="Static Walk cycle Start Frame", default=1)  
    wu_end_cycle : IntProperty(name="Walk Cycle End Frame",description="Static Walk cycle End Frame", default=24)  
    # wu_cyclic_action : StringProperty(name="Name of the cyclic action", default="")  
    wu_prog_action : StringProperty(name="Name of the progressive action", default="")  
    wu_original_action : StringProperty(name="Name of the original action", default="")  
    wu_sync_speed : BoolProperty(name="Sync Speed", description="Copy the spacing of the cyclic action exactly", default=False)  
    wu_ignore_z : BoolProperty(name="Ignore Vertical", description="Ignore vertical movements when calculating distance travelled", default=True)  
    wu_prevent_slip : BoolProperty(name="Prevent Slip", description="Use keyframe types you configure to prevent foot slipping", default=False)  
    wu_cyclic_action : EnumProperty(
        items=GetActions,
        name="Walk Cycle Action",
        description="Static Walk Cycle Action",
        default=None,
        options={'ANIMATABLE'},
        update=None,
        get=None,
        set=None)
   




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
        layout.label(text="Walk Cycle Details")
        layout.prop(scene.WUProps, "wu_cyclic_action", text="")
        layout.prop(scene.WUProps, "wu_start_cycle")
        layout.prop(scene.WUProps, "wu_end_cycle")
        layout.prop(scene.WUProps, "wu_cycle_dist")

        layout.label(text="Animation Range")
        layout.prop(scene.WUProps, "wu_start_frame")
        layout.prop(scene.WUProps, "wu_end_frame")

        layout.label(text="Options")
        layout.prop(scene.WUProps, "wu_sync_speed")
        layout.prop(scene.WUProps, "wu_ignore_z")
        layout.prop(scene.WUProps, "wu_prevent_slip")
        # layout.prop(scene, "WUAction")

        layout.label(text="Actions")
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
    # bpy.types.Scene.WUAction = EnumProperty(items=GetActions, description="offers....",  default="None",)
    


def unregister():
    del bpy.types.Scene.WUProps
    # from . import WalkUnpack
    # WalkUnpack.unregisterTypes()
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)


if __name__ == "__main__":
    register()

