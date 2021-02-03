# Blender WalkUnpack Addon

Blender 2.8 - 2.93

Files:
[WalkUnpack_v0_1_2.zip](https://github.com/nerk987/WalkUnpack/releases/download/v0.1.2/WalkUnpack_v0_1_2.zip) - the addon


## Introduction

It’s common to develop a walk cycle so that the character walks on the spot. Let’s call this a ‘static’ walk cycle. For games development, that’s generally all you need. For animations and films, this is not ideal. To use it the root bone must be animated to smoothly move at the walking speed, and it’s hard to avoid foot slipping. Customising the animation is also difficult as the keyframes are relative to the moving root bone.
Developing the walk cycle as a ‘progressive’ cycle alleviates some of the issues, but there are still downsides.
This addon aims to treat the static walkcycle as a motion template which can be unpacked and applied to the motion of the root bone of the character.

## Installation

Download the ZIP file the link above. Open Blender and go to Preferences then the Add-ons tab.
Use the Install Addon button to select the txa_ant.zip file. Once installed, enable the WalkUnpack addon.
## The Aim of the Addon
The idea is that you animate the root bone of the character to follow the required path. The addon will create a new action and will then take keyframes from the static walk cycle and place them at the appropriate intervals for the speed of the root bone, and it will add the offset of the root bone from it’s starting position to the keyframes of control bones like the feet IK targets and the torso. When it’s finished, the keyframes of the root bone are removed.

## Usage

### Gather walk cycle information
I’ll assume you character already has a ‘static’ walk cycle. The walk cycle will have a start and an end frame for the walk cycle motion, and the keyframes on the first frame should be the same as the keyframes on the last frame. You will also need to determine the distance that the character must travel in that frame range so that the feet have no slip. This can be a little tricky to find in some cases, but it’s often twice the distance between the feet IK bones in the traditional ‘contact’ pose.
Determine the root bone and the control bones
Your character will likely have a ‘master’, or ‘root’ bone. Also determine the ‘Control Bones’ of the character that are effectively parented to the root bone. Typically, these will be the feet IK bones and the torso bone, but may in some cases include the eye target bone and other miscellaneous controls. 
### Animate the root bone
For your armature, select the action that requires walk cycle keyframes, or start a new action. Animate the root bone of the character to follow the required path of the character. Typically you would animate at a speed that matches the walk cycle speed, although the addon will compensate with keyframe spacing if not. At this time, the addon requires the root bone animation be done in keyframes, not constraints, so if you use a curve animation or other constraint you must bake that action to keyframes prior to using the addon.
Select the control bones, then the root bone
Select your character’s armature in pose mode. Select all of the ‘control bones’ and then shift select the ‘root’ bone. Typically, that means the IK target bones of the feet, the torso bone and the root bone are all selected, with the root bone being the active bone.
### Run the WalkUnpack addon 
Look for the WalkUnpack tab on the N-Panel. In the tab. Enter the start and end frame for the static walk cycle, and the distance the walk action travels as mentioned earlier.
There are some tick box options that are discussed a bit later. Press the ‘Bake’ button.
Check the result
A new action should have been created and should be active. It should be named like the previous action with a ‘_wu’ appended. This action should have no keyframes for the root bone, and progressive key frames for the rest of the model. When played, the character should walk for the whole action, but it’s likely the feet will be slipping at least a bit.
### Revert
The Revert button on the WalkUnpack addond tab will switch back to the previous action so that you can adjust the root bone animation if you’re not happy with the result.
Slipping Feet and keyframe locations
How does it all work? The addon checks the amount of root bone movement for each frame of the action. It compares that to the static walk cycle movement per frame (WalkcycleDist/(Endframe-Startframe). If they are the same for each frame, the walk cycle keyframes will be placed with the same spacing in the new action. If the root bone moves faster, the keyframes will be place more frequently. If the root bone moves slower, the keyframes will be placed less frequently.
At this time, the addon will place the keyframes exactly on integral frames, and it doesn’t do any interpolation, so there may be a little unevenness in the motion. There is a limit to how fast you can go without things going wrong! If your walk cycle has keyframes
If the root bone is animated in a straight line at exactly at the same speed as the walk cycle the feet shouldn’t slip significantly. If they do, double check your estimation of the walk cycle distance. If you speed up, slow down, turn, or rise and fall, then they’ll skip, but it’s easy to correct now that the keyframes are relative to the pose space. In the next section, there are some options to help with these issues.
## Addon Options
### Sync Speed
If enabled, this option forces the keyframe spacing present in the static walk cycle to be repeated in the final action.
This is useful if you are trying to keep the walk cycle at the original speed, and you have animated the root bone with this in mind. Without the sync speed option, some keyframes may be a frame out here or there giving an uneven walk. However, if you haven’t animated the root bone to go at the native walk cycle speed, the feet will slip.
### Ignore Vertical
By default, vertical movements of the root bone are ignored when generating new keyframe spacing. This is suitable for normal walking where characters normally don’t walk faster when going up stairs for example. However, you can turn this option off if you have a spider walking up a wall, or a character climbing a ladder.
### Prevent slip
In some ways, I don’t think slipping feet are a big problem. When generating a new animation, you will likely have to run over the whole animation and tweak just about everything anyway, and foot position is one of those things. Still, it’s satisfying if the addon can produce nice looking results.
This option lets you identify the keyframes in the walkcycle action that should result in a fixed location or rotation when applied along the path. This is done by using keyframe types. (If you’re not familiar with keyframe types, they don’t normally do anything, they just help you organise. I’m hi-jacking this function to identify different keyframes to the addon).
For the static walk cycle keyframes associated with the control bones for the feet, identify the first set of keyframes where the foot contacts the ground. Change the keyframe type to ‘EXTREME’ for those keyframes. (In programming terms, this will push the keyframe value onto a stack). For every subsequent keyframe where the foot should be still, set the keyframe type to ‘JITTER’. (This will pop the value off the stack and use this value for the current keyframe). All other keyframes should be of some other type. (And will clear the stack). Be aware that the addon treats the first and last keyframes of the walk cycle as interchangeable, so it’s best to have the same type at both ends.
The image below shows a traditional 24 frame walk cycle with keyframes for contact, down, passing and up. (or whichever version of this you prefer.) The red ‘EXTREME’ keyframes indicate the foot touching, the green ‘JITTER’ keyframes will hold both rotation and location.

This method requires a little bit of effort to set up but gives a lot of flexibility. For example, you can lock the location of the feet, but not the rotation and allow the foot to twist on the ground. It also allows for rigs that use the same control bone to rotate from heel to toe and for location.
