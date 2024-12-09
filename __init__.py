# This add-on was based on: https://github.com/jquillan/vse_masking_tools
bl_info = {
    "name": "VSE to Camera Background",
    "author": "John C. Quillan, tintwotin",
    "version": (0, 2),
    "blender": (3, 4, 0),
    "location": "3D View > Sidebar > View > Camera Background",
    "description": "Adds VSE to 3D View Camera Background",
    "warning": "",
    "doc_url": "",
    "category": "3D View",
}

import bpy
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, PointerProperty

def vse_opengl_render_handler(dummy):
    bpy.ops.render.opengl(animation=False, render_keyed_only=False, sequencer=True)

def vse_sync_changed_func(self, context):
    if context.scene.vse_sync.vse_sync:
        if vse_opengl_render_handler not in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.append(vse_opengl_render_handler)
            render_result = next(image for image in bpy.data.images if image.type == "RENDER_RESULT")
            # Get the current active camera
            camera = context.scene.camera
            if camera:
                # Ensure the camera has a background image
                if not camera.data.background_images:
                    camera.data.background_images.new()
                background_image = camera.data.background_images[0]
                background_image.image = render_result
                background_image.alpha = 1.0  # Set alpha to 1
                camera.data.show_background_images = True  # Show background images
    else:
        if vse_opengl_render_handler in bpy.app.handlers.frame_change_post:
            bpy.app.handlers.frame_change_post.remove(vse_opengl_render_handler)
            camera = context.scene.camera
            if camera and camera.data.background_images:
                camera.data.show_background_images = False  # Hide background images

class VSESYNC_settings(PropertyGroup):
    vse_sync : BoolProperty(
        name="Sync VSE",
        description="Keep Render Layer in sync with Sequencer Preview",
        default=False,
        update=vse_sync_changed_func
    )

def append_to_view3d_properties(self, context):
    layout = self.layout
    scene = context.scene
    vse_sync = scene.vse_sync

    row = layout.row(heading="Camera Background")
    row.use_property_split = True
    row.use_property_decorate = False
    row.prop(vse_sync, "vse_sync", text="Sequencer")

def register():
    bpy.utils.register_class(VSESYNC_settings)
    bpy.types.Scene.vse_sync = PointerProperty(type=VSESYNC_settings)
    bpy.types.VIEW3D_PT_view3d_properties.append(append_to_view3d_properties)

def unregister():
    bpy.utils.unregister_class(VSESYNC_settings)
    del bpy.types.Scene.vse_sync
    bpy.types.VIEW3D_PT_view3d_properties.remove(append_to_view3d_properties)

if __name__ == "__main__":
    register()
