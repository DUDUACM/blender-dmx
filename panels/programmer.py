#
#   BlendexDMX > Panels > Programmer
#
#   - Set selected fixtures color
#   - Set selected fixtures intensity
#   - Clear selection
#
#   http://www.github.com/open-stage/BlenderDMX
#

import bpy
from bpy.types import Operator, Panel
from dmx.osc_utils import DMX_OSC_Handlers

# Operators #

class DMX_OT_Programmer_Set_Ignore_Movement(Operator):
    bl_label = "Lock Movement"
    bl_idname = "dmx.ignore_movement_true"
    bl_description = "Ignore pan/tilt DMX data"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        selected = []
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if obj in bpy.context.selected_objects:
                    selected.append(fixture)

        for fixture in dmx.fixtures:
            if fixture in selected:
                fixture.ignore_movement_dmx = True
        return {'FINISHED'}

class DMX_OT_Programmer_Unset_Ignore_Movement(Operator):
    bl_label = "Unlock Movement"
    bl_idname = "dmx.ignore_movement_false"
    bl_description = "Allow pan/tilt DMX data"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        selected = []
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if obj in bpy.context.selected_objects:
                    selected.append(fixture)

        for fixture in dmx.fixtures:
            if fixture in selected:
                fixture.ignore_movement_dmx = False
        return {'FINISHED'}

class DMX_OT_Programmer_DeselectAll(Operator):
    bl_label = "Deselect All"
    bl_idname = "dmx.deselect_all"
    bl_description = "Deselect every object in the Scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')

        DMX_OSC_Handlers.fixture_clear()
        bpy.context.scene.dmx.updatePreviewVolume()
        return {'FINISHED'}

class DMX_OT_Programmer_SelectAll(Operator):
    bl_label = "Select All"
    bl_idname = "dmx.select_all"
    bl_description = "Select every object in the Scene"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        for fixture in dmx.fixtures:
            fixture.select()
        bpy.context.scene.dmx.updatePreviewVolume()
        return {'FINISHED'}

class DMX_OT_Programmer_SelectFiltered(Operator):
    bl_label = "Select Visible (only filtered)"
    bl_idname = "dmx.select_filtered"
    bl_description = "Select every object in the Scene which is visible in the fixtures list"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        for fixture, enabled in zip(dmx.fixtures, dmx.fixtures_filter):
            if enabled:
                fixture.select()
        bpy.context.scene.dmx.updatePreviewVolume()
        return {'FINISHED'}

class DMX_OT_Programmer_SelectInvert(Operator):
    bl_label = "Invert selection"
    bl_idname = "dmx.select_invert"
    bl_description = "Invert the selection"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        selected = []
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if (obj in bpy.context.selected_objects):
                    selected.append(fixture)
                    fixture.unselect() 

        for fixture in dmx.fixtures:
            if fixture not in selected:
                fixture.select()

        bpy.context.scene.dmx.updatePreviewVolume()
        return {'FINISHED'}

class DMX_OT_Programmer_SelectEveryOther(Operator):
    bl_label = "Select every other light"
    bl_idname = "dmx.select_every_other"
    bl_description = "Select every other light"
    bl_options = {'UNDO'}

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        dmx = context.scene.dmx
        for idx, fixture in enumerate(dmx.fixtures):
            if idx % 2 == 0:
                fixture.select()

        bpy.context.scene.dmx.updatePreviewVolume()
        return {'FINISHED'}

class DMX_OT_Programmer_Clear(Operator):
    bl_label = "Clear"
    bl_idname = "dmx.clear"
    bl_description = "Clear all DMX values to default and update fixtures"
    bl_options = {'UNDO'}

    def execute(self, context):
        scene = context.scene
        if (not len(bpy.context.selected_objects)):
            for fixture in scene.dmx.fixtures:
                fixture.clear()
        else:
            for fixture in scene.dmx.fixtures:
                for obj in fixture.collection.objects:
                    if (obj in bpy.context.selected_objects):
                        fixture.clear()
                        break
        scene.dmx.programmer_color = (1.0, 1.0, 1.0, 1.0)
        scene.dmx.programmer_dimmer = 0.0
        scene.dmx.programmer_pan = 0.0
        scene.dmx.programmer_tilt = 0.0
        scene.dmx.programmer_zoom = 0
        scene.dmx.programmer_shutter = 0
        return {'FINISHED'}

class DMX_OT_Programmer_TargetsToZero(Operator):
    bl_label = "Targets to zero"
    bl_idname = "dmx.targets_to_zero"
    bl_description = "Set Targets to 0"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        select_targets(dmx)
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if (obj in bpy.context.selected_objects):
                    if ('Target' in fixture.objects):
                        fixture.objects['Target'].object.location = ((0,0,0))
                    break

        return {'FINISHED'}

class DMX_OT_Programmer_SelectBodies(Operator):
    bl_label = "Select Bodies"
    bl_idname = "dmx.select_bodies"
    bl_description = "Select body from every fixture element selected"
    bl_options = {'UNDO'}


    def execute(self, context):
        dmx = context.scene.dmx
        bodies = []
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if (obj in bpy.context.selected_objects):
                    for body in fixture.collection.objects:
                        if body.get("geometry_root", False):
                            bodies.append(body)
                    break

        if (len(bodies)):
            bpy.ops.object.select_all(action='DESELECT')
            for body in bodies:
                body.select_set(True)
        return {'FINISHED'}

class DMX_OT_Programmer_SelectTargets(Operator):
    bl_label = "Select Targets"
    bl_idname = "dmx.select_targets"
    bl_description = "Select target from every fixture element selected"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        select_targets(dmx)
        return {'FINISHED'}

class DMX_OT_Programmer_SelectCamera(Operator):
    bl_label = "Select Camera"
    bl_idname = "dmx.toggle_camera"
    bl_description = "Select camera of the selected fixture"
    bl_options = {'UNDO'}

    def execute(self, context):
        dmx = context.scene.dmx
        region = next(iter([area.spaces[0].region_3d for area in bpy.context.screen.areas if area.type == 'VIEW_3D']), None)
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if (obj in bpy.context.selected_objects):
                    for obj in fixture.collection.objects:
                        if "MediaCamera" in obj.name:
                            bpy.context.scene.camera=obj
                            if region:
                                if region.view_perspective == "CAMERA":
                                    region.view_perspective = "PERSP"
                                else:
                                    region.view_perspective = "CAMERA"
                            break
        return {'FINISHED'}

# Panels #

class DMX_PT_Programmer(Panel):
    bl_label = "Programmer"
    bl_idname = "DMX_PT_Programmer"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DMX"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        dmx = scene.dmx

        locked = False

        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if obj in bpy.context.selected_objects:
                    if fixture.ignore_movement_dmx is True:
                        locked = True

        selected = len(bpy.context.selected_objects) > 0

        row = layout.row()
        row.operator("dmx.select_all", text='', icon='SELECT_EXTEND')
        row.operator("dmx.select_invert", text='', icon='SELECT_SUBTRACT')
        row.operator("dmx.select_every_other", text='', icon='SELECT_INTERSECT')
        c0 = row.column()
        c1 = row.column()
        c2 = row.column()
        c3 = row.column()
        c4 = row.column()
        c0.operator("dmx.select_filtered", text='', icon="SELECT_DIFFERENCE")
        c1.operator("dmx.deselect_all", text='', icon='SELECT_SET')
        c2.operator("dmx.targets_to_zero", text="", icon="LIGHT_POINT")
        c3.operator("dmx.ignore_movement_true", text="", icon="LOCKED")
        c4.operator("dmx.ignore_movement_false", text="", icon="UNLOCKED")
        c1.enabled = c2.enabled = c3.enabled = selected
        c4.enabled = locked and selected

        row = layout.row()
        row.operator("dmx.select_bodies", text="Bodies")
        row.operator("dmx.select_targets", text="Targets")
        if len(bpy.context.selected_objects) == 1:
            for fixture in dmx.fixtures:
                for obj in fixture.collection.objects:
                    if (obj in bpy.context.selected_objects):
                        for obj in fixture.collection.objects:
                            if "MediaCamera" in obj.name:
                                row.operator("dmx.toggle_camera", text="Camera")
        row.enabled = selected

        layout.template_color_picker(scene.dmx,"programmer_color", value_slider=True)
        layout.prop(scene.dmx, "programmer_color")
        layout.prop(scene.dmx,"programmer_dimmer", text="Dimmer")

        layout.prop(scene.dmx,"programmer_pan", text="Pan")
        layout.prop(scene.dmx,"programmer_tilt", text="Tilt")

        layout.prop(scene.dmx,"programmer_zoom", text="Zoom")
        layout.prop(scene.dmx,"programmer_shutter", text="Strobe")

        if (selected):
            layout.operator("dmx.clear", text="Clear")
        else:
            layout.operator("dmx.clear", text="Clear All")

def select_targets(dmx):
        targets = []
        for fixture in dmx.fixtures:
            for obj in fixture.collection.objects:
                if (obj in bpy.context.selected_objects):
                    if ('Target' in fixture.objects):
                        targets.append(fixture.objects['Target'].object)
                    break

        if (len(targets)):
            bpy.ops.object.select_all(action='DESELECT')
            for target in targets:
                target.select_set(True)
