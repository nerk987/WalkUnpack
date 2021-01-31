# ##### BEGIN GPL LICENSE BLOCK #####
#
#  WalkUnpack.py  -- a script 
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

# version comment: V0.1.1 Relase Version

import bpy
import mathutils, os
from mathutils import Matrix
from mathutils import Vector
from mathutils import Euler
from mathutils import Quaternion
import math
from bpy.props import FloatProperty, FloatVectorProperty, IntProperty, BoolProperty, EnumProperty, StringProperty
import copy
# from random import random

#Misc Rountines
def PrintMatrix(mat, desc):
    ret = mat.decompose()
    print(desc)
    print("Trans: ", ret[0])
    print("Rot: (%.2f, %.2f, %.2f), %.2f" % (ret[1].axis[:] + (math.degrees(ret[1].angle), )))  

def PrintQuat(quat, desc):
    print(desc)
    print("Rot: (%.2f, %.2f, %.2f), %.2f" % (quat.axis[:] + (math.degrees(quat.angle), )))  

#Remove keyframes from selected bones
def RemoveKeyframes2(armature, bones):
    dispose_paths = []
    for bone in bones:
        if bone.name[-5:] == "_flex":
            dispose_paths.append('pose.bones["{}"].rotation_quaternion'.format(bone.name))
            dispose_paths.append('pose.bones["{}"].scale'.format(bone.name))
    try:
        dispose_curves = [fcurve for fcurve in armature.animation_data.action.fcurves if fcurve.data_path in dispose_paths]
        for fcurve in dispose_curves:
            armature.animation_data.action.fcurves.remove(fcurve)
    except AttributeError:
        pass
        
#Find the matching fcurve
def FindMatchingFCurve(fcurves, data_path, array_index):
    for fcurve in fcurves:
        if fcurve.data_path == data_path and fcurve.array_index == array_index:
            return fcurve
    return None

#Copy all the keyframe parameters
def CopyKeyframeParams(newKF, oldKF):
            newKF.type = oldKF.type
            newKF.amplitude = oldKF.amplitude
            newKF.back = oldKF.back
            newKF.easing = oldKF.easing
            newKF.handle_left[0] = newKF.co[0] + (oldKF.handle_left[0] - oldKF.co[0])
            newKF.handle_left[1] = (oldKF.handle_left[1] - oldKF.co[1]) + newKF.co[1]
            newKF.handle_right[0] = newKF.co[0] + (oldKF.handle_right[0] - oldKF.co[0])
            newKF.handle_right[1] = (oldKF.handle_right[1] - oldKF.co[1]) + newKF.co[1]
            newKF.handle_left_type = oldKF.handle_left_type
            newKF.handle_right_type = oldKF.handle_right_type
            newKF.interpolation = oldKF.interpolation
            newKF.period = oldKF.period
        

class ARMATURE_OT_WalkUnpack(bpy.types.Operator):
    """Unpack the walk cycle to a new action"""
    bl_idname = "armature.walkunpack"
    bl_label = "Bake"
    bl_options = {'REGISTER', 'UNDO'}
    sStartFrame = 0
    sEndFrame = 0
    
    sRootBone = None
    sIKBones = []
    keyStack = {}

    # modified function for searching fcurves
    # generates a local matrix for the specified bone and frame
    def find_fcurve_matrix(self, id_data, bone_name, sourceaction, frame):
        # anim_data = id_data.animation_data
        location = Vector([0.0, 0.0, 0.0])
        quat_rotation = Quaternion()
        # print("Rot mode: ", id_data.pose.bones[bone_name].rotation_mode)
        pose_bone = id_data.pose.bones[bone_name]
        rot_mode = pose_bone.rotation_mode
        if len(rot_mode) > 3:
            rot_mode = "XYZ"
        euler_rotation = Euler((0,0,0), rot_mode)
        rotmat = None
        for fcurve in sourceaction.fcurves:
            # print(fcurve.data_path)
            if '["' + bone_name + '"]' in fcurve.data_path:
                if ".location" in fcurve.data_path:
                    location[fcurve.array_index] = fcurve.evaluate(frame)
                if "_quaternion" in fcurve.data_path:
                    quat_rotation[fcurve.array_index] = fcurve.evaluate(frame)
                    rotmat = quat_rotation.to_matrix()
                if "_euler" in fcurve.data_path:
                    euler_rotation[fcurve.array_index] = fcurve.evaluate(frame)
                    rotmat = quat_rotation.to_matrix()
        mat = Matrix.Translation(location)
        # print("Reading loc: ", bone_name, frame, location)
        if rotmat is not None:
            rotmat.resize_4x4()
            # print("rotmat: ", rotmat)
            mat = mat @ rotmat
        posemat = pose_bone.id_data.convert_space(matrix=mat, pose_bone=pose_bone, from_space='LOCAL', to_space='POSE')
        return posemat
       
#
# Copy the keyframes cyclically to a new action over the correct range
#
    def BuildNewAction(self, context):
        ob = context.active_object
        original_action = ob.animation_data.action
        sFPM = context.scene.WUProps
        cyclic_action = bpy.data.actions[sFPM.wu_cyclic_action]
        matrixDict = {}
        rootMatrix_n = None
        oldRootLoc = None
        
        #Obtain the pose matrix of the root bone for future calculations
        rootMatrix0 = self.find_fcurve_matrix(ob, self.sRootBone.name, original_action, self.sStartFrame)
        
        #if the new action has already been generated, then delete it first
        if original_action.name + "_wu" in bpy.data.actions:
            prog_action = bpy.data.actions[original_action.name + "_wu"]
            bpy.data.actions.remove(prog_action)
        
        #Copy the current action and rename
        context.active_object.animation_data.action = cyclic_action.copy()
        prog_action = context.active_object.animation_data.action
        prog_action.name = original_action.name + "_wu"
        sFPM.wu_prog_action = prog_action.name
        
        #Clear all keyframes in the desired range of the new action (except for the root bone keyframes)
        # del_list = []
        for fcurve in prog_action.fcurves:
            while len(fcurve.keyframe_points) > 0:
                fcurve.keyframe_points.remove(fcurve.keyframe_points[0])
            # if self.sRootBone.name not in fcurve.data_path:
                # for keyframe in fcurve.keyframe_points:
                    # if keyframe.co[0] >= self.sStartFrame and keyframe.co[0] <= self.sEndFrame:
                        # del_list.append([fcurve.data_path, keyframe.co[0], fcurve.array_index])
        
        # for del_item in del_list:
            # print("del_item: ", del_item[0], del_item[1], del_item[2])
            # bpy.context.active_object.keyframe_delete(del_item[0], frame = del_item[1], index = del_item[2])
        
        #Copy the keyframes one by one
        old_f = -1.0
        cycleFrame = sFPM.wu_start_cycle
        for frame in range(self.sStartFrame, self.sEndFrame):
            print("Frame: ", frame)
            
            for fcurve in cyclic_action.fcurves:
                # print("Fcurve return: ", fc_no, " ", fcurve.data_path)
                
                #Read the root bone location and check the distance moved each frame 
                #to allow calculation of how quickly to progress the writing of frames
                # in the new action.
                if rootMatrix_n == None:
                    rootMatrix_n = self.find_fcurve_matrix(ob, self.sRootBone.name, original_action, frame)
                    if frame == self.sStartFrame:
                        frameInc = 1.0
                        cycleFrame = sFPM.wu_start_cycle
                        oldRootLoc = rootMatrix_n.translation
                        # print("frame, cycleFrame: ", frame, cycleFrame)
                    else:
                        if sFPM.wu_ignore_z:
                            dist = (Vector((rootMatrix_n.translation.x, rootMatrix_n.translation.y)) - Vector((oldRootLoc.x, oldRootLoc.y))).length
                        else:
                            dist = (rootMatrix_n.translation - oldRootLoc).length
                        # print("root loc and oldloc: ", frame, rootMatrix_n.translation, oldRootLoc)
                        if sFPM.wu_sync_speed:
                            frameInc = 1
                        else:
                            frameInc = dist *  (sFPM.wu_end_cycle - sFPM.wu_start_cycle)/sFPM.wu_cycle_dist
                        cycleFrame = cycleFrame + frameInc
                        if cycleFrame > sFPM.wu_end_cycle:
                            cycleFrame = cycleFrame - (sFPM.wu_end_cycle - sFPM.wu_start_cycle)
                        oldRootLoc = rootMatrix_n.translation
                        # print("frameinc, cycleFrame, nextCycleFrame: ", dist, frameInc, cycleFrame, frameInc+cycleFrame)

                #Find an fcurve in the new action matching with the current cyclic action fcurve.
                newfcurve = FindMatchingFCurve(prog_action.fcurves, fcurve.data_path, fcurve.array_index)
                if newfcurve == None:
                    print("Missing FCurve: ", fcurve.data_path)
                elif self.sRootBone.name not in newfcurve.data_path:
                    for keyframe in fcurve.keyframe_points:
                        if keyframe.co[0] >= cycleFrame and keyframe.co[0] < (cycleFrame + frameInc):
                            if frame != old_f:
                                # print("Key: ", keyframe.co[0], cycleFrame, cycleFrame + frameInc, frame)
                                old_f = frame
                            newKeyValue = keyframe.co[1]
                            
                            #Get a pose matrix at this frame for the IK bones
                            for b in self.sIKBones:
                                if '["' + b.name + '"]' in fcurve.data_path and b.name not in matrixDict:
                                    Bn = self.find_fcurve_matrix(ob, b.name, cyclic_action, cycleFrame)
                                    matrixDict[b.name] = Bn.copy()
                                    R1 = rootMatrix0
                                    Rn = rootMatrix_n
                                    Bnew = Rn @ R1.inverted() @ Bn
                                    localmat = b.id_data.convert_space(matrix=Bnew, pose_bone=b, from_space='POSE', to_space='LOCAL')

                                    # print("Read IK pose matrix: ", frame, b.name, matrixDict[b.name].translation, Bnew.translation, localmat.translation )
                                    
                                #Replace key value for the IK bones by calculating a new pose matrix:
                                #    Bnew = Rn * R1_inv * Bn (Rn: root at current frame, R1 = root at start, Bn = IK bone at current frame)

                                if  '["' + b.name + '"]' in fcurve.data_path:
                                    # print("Offset: ", (Rn @ R1.inverted()).translation)
                                    if ".location" in fcurve.data_path:
                                        newKeyValue = localmat.translation[fcurve.array_index]
                                    if "_euler" in fcurve.data_path:
                                        newKeyValue = localmat.to_euler()[fcurve.array_index]
                                    if "_quaternion" in fcurve.data_path:
                                        newKeyValue = localmat.to_quaternion()[fcurve.array_index]
                            
                            #Prevent Foot slipping
                            #If enabled, for 'EXTREME' keyframe types, push keyframe value
                            # and for 'JITTER' types, pop the previous value
                            #for other types, delete the entry
                            fsindex = fcurve.data_path + '_' + str(fcurve.array_index)
                            if sFPM.wu_prevent_slip:
                                if keyframe.type == 'EXTREME':
                                    self.keyStack[fsindex] = newKeyValue
                                    # print("Push keyframe: ", fsindex, newKeyValue)
                                elif keyframe.type == 'JITTER':
                                    if fsindex in self.keyStack:
                                        newKeyValue = self.keyStack[fsindex]
                                        # print("Pop keyframe: ", fsindex, newKeyValue)
                                else:
                                    if fsindex in self.keyStack:
                                        del self.keyStack[fsindex]
                                        # print("Remove keyframe: ", fsindex)
                            #Insert the keyframe
                            newkeyframe = newfcurve.keyframe_points.insert(frame, newKeyValue)
                            print("New, Old: ", newkeyframe.handle_left[1], keyframe.handle_left[1])
                            CopyKeyframeParams(newkeyframe, keyframe)
            rootMatrix_n = None
            matrixDict = {}
                
        
        return 

#
# Perform the unpack action
#

    def execute(self, context):
        #
        #Check Member variables are reset
        #
        self.sRootBone = None
        self.sIKBones = []
        self.keyStack = {}
        #
        # Set up initial variables
        #
        sFPM = context.scene.WUProps
        # print("cyclic Action: ", sFPM.wu_cyclic_action)
        scene = context.scene
        ob = context.object
        sFPM.wu_original_action = ob.animation_data.action.name
        original_action = ob.animation_data.action
        self.sStartFrame = int(original_action.frame_range[0])
        self.sEndFrame = int(original_action.frame_range[1])
        if sFPM.wu_start_frame > 0 and sFPM.wu_start_frame > self.sStartFrame:
            self.sStartFrame = sFPM.wu_start_frame
        if sFPM.wu_end_frame > 0 and sFPM.wu_end_frame < self.sEndFrame:
            self.sEndFrame = sFPM.wu_end_frame
        # print("Action Frame Range: ", self.sStartFrame, self.sEndFrame)
        #
        # Record the IK and the root bones
        #
        
        self.sRootBone = context.active_pose_bone
        self.sIKBones = []
        for b in context.selected_pose_bones:
            if b != self.sRootBone:
                self.sIKBones.append(b)
        print("Root: ", self.sRootBone.name)
        for b in self.sIKBones:
            print("IKBone: ", b.name)
            
        #
        # Generate the new action
        #
        self.BuildNewAction(context)
        #
        # Update the keyframes in the new action
        #
        
        print("Finished")
        return {'FINISHED'}

class ARMATURE_OT_WalkUnpackRevert(bpy.types.Operator):
    """Revert to the original action"""
    bl_idname = "armature.walkunpackrevert"
    bl_label = "Revert"
    bl_options = {'REGISTER', 'UNDO'}


    def execute(self, context):
        sFPM = context.scene.WUProps
        scene = context.scene
        ob = context.object
        
        if sFPM.wu_original_action in bpy.data.actions:
            ob.animation_data.action = bpy.data.actions[sFPM.wu_original_action]
        return {'FINISHED'}
