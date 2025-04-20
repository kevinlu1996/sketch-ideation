"""
Blender Integration Component for the Ideation Agent.
Handles the connection between the ideation agent and Blender.
"""

import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from blender_ideation.utils import find_blender_executable


class BlenderIntegration:
    """
    Handles integration with Blender for the ideation agent.
    This is a simplified implementation that would need to be expanded
    based on your specific Blender workflow.
    """
    
    def __init__(self, blender_executable_path: Optional[str] = None):
        """
        Initialize the Blender integration component.
        
        Args:
            blender_executable_path: Path to the Blender executable.
                If None, will try to find Blender in standard locations.
        """
        self.blender_path = blender_executable_path or find_blender_executable()
        if not self.blender_path:
            raise ValueError("Could not find Blender executable. Please specify the path manually.")
    
    def import_3d_model(
        self, 
        model_path: str, 
        blender_project_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Import a 3D model into a Blender project.
        
        Args:
            model_path: Path to the 3D model file (glb, obj, fbx, etc.)
            blender_project_path: Path to save the resulting Blender file.
                If None, creates a temporary file.
        
        Returns:
            Path to the created Blender project file.
        """
        if not os.path.exists(model_path):
            print(f"Model file not found: {model_path}")
            return None
        
        if blender_project_path is None:
            # Create a temporary file for the Blender project
            temp_dir = tempfile.gettempdir()
            blender_project_path = os.path.join(temp_dir, f"ideation_{int(time.time())}.blend")
        
        # Create a Python script for Blender to execute
        script_content = f"""
import bpy
import os

# Clear default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Import the 3D model
model_path = r"{model_path}"
file_extension = os.path.splitext(model_path)[1].lower()

if file_extension == '.obj':
    bpy.ops.import_scene.obj(filepath=model_path)
elif file_extension == '.fbx':
    bpy.ops.import_scene.fbx(filepath=model_path)
elif file_extension == '.glb' or file_extension == '.gltf':
    bpy.ops.import_scene.gltf(filepath=model_path)
elif file_extension == '.stl':
    bpy.ops.import_mesh.stl(filepath=model_path)
elif file_extension == '.ply':
    bpy.ops.import_mesh.ply(filepath=model_path)
elif file_extension == '.dae':
    bpy.ops.wm.collada_import(filepath=model_path)
else:
    print(f"Unsupported file format: {{file_extension}}")

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=r"{blender_project_path}")"""
        
        # Write the script to a temporary file
        script_path = os.path.join(tempfile.gettempdir(), "import_script.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Run Blender with the script
        try:
            subprocess.run([
                self.blender_path,
                "--background",
                "--python", script_path
            ], check=True)
            
            print(f"Model imported and saved to {blender_project_path}")
            return blender_project_path
            
        except subprocess.CalledProcessError as e:
            print(f"Error importing model: {e}")
            return None
        finally:
            # Clean up the temporary script
            if os.path.exists(script_path):
                os.remove(script_path)
    
    def create_ideation_scene(
        self, 
        session_data: Dict, 
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a complete ideation scene in Blender with all the models
        from the ideation session.
        
        Args:
            session_data: Dictionary containing paths to all models and metadata
            output_path: Path to save the resulting Blender file
        
        Returns:
            Path to the created Blender project file
        """
        if output_path is None:
            # Create a file for the Blender project
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"ideation_scene_{int(time.time())}.blend")
        
        # Extract paths from session data
        sketch_3d_path = session_data.get('sketch_3d_path')
        text_3d_path = session_data.get('text_3d_path')
        title = session_data.get('title', 'Untitled')
        project_type = session_data.get('project_type', 'Unknown')
        genre = session_data.get('genre', 'Unknown')
        
        # Create a Python script for Blender to execute
        script_content = f"""
import bpy
import os
import math

# Clear default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Add metadata as text objects
def add_text(text, location, size=1.0):
    bpy.ops.object.text_add(location=location)
    text_obj = bpy.context.active_object
    text_obj.data.body = text
    text_obj.data.size = size
    return text_obj

# Add scene metadata
add_text("Concept: {title}", (0, 2, 0), 0.5)
add_text("Project Type: {project_type}", (0, 1, 0), 0.5)
add_text("Genre: {genre}", (0, 0, 0), 0.5)

# Import models if they exist
models = []

# Function to import a 3D model
def import_model(model_path, location):
    if not model_path or not os.path.exists(model_path):
        return None
        
    file_extension = os.path.splitext(model_path)[1].lower()
    
    # Store current selection
    selected_objs = [obj for obj in bpy.context.selected_objects]
    active_obj = bpy.context.active_object
    
    # Import based on file extension
    if file_extension == '.obj':
        bpy.ops.import_scene.obj(filepath=model_path)
    elif file_extension == '.fbx':
        bpy.ops.import_scene.fbx(filepath=model_path)
    elif file_extension == '.glb' or file_extension == '.gltf':
        bpy.ops.import_scene.gltf(filepath=model_path)
    elif file_extension == '.stl':
        bpy.ops.import_mesh.stl(filepath=model_path)
    elif file_extension == '.ply':
        bpy.ops.import_mesh.ply(filepath=model_path)
    elif file_extension == '.dae':
        bpy.ops.wm.collada_import(filepath=model_path)
    else:
        print(f"Unsupported file format: {{file_extension}}")
        return None
    
    # Get newly created objects
    new_objs = [obj for obj in bpy.context.selected_objects if obj not in selected_objs]
    
    if new_objs:
        # Group the new objects
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
        parent = bpy.context.active_object
        parent.name = os.path.basename(model_path)
        
        for obj in new_objs:
            obj.select_set(True)
            parent.select_set(False)
        
        bpy.context.view_layer.objects.active = parent
        bpy.ops.object.parent_set(type='OBJECT')
        
        # Move the group to the specified location
        parent.location = location
        return parent
    
    # Restore previous selection
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in selected_objs:
        obj.select_set(True)
    if active_obj:
        bpy.context.view_layer.objects.active = active_obj
        
    return None

# Import the sketch-based 3D model
if "{sketch_3d_path}":
    sketch_model = import_model(r"{sketch_3d_path}", (-3, -3, 0))
    if sketch_model:
        add_text("From Sketch", (-3, -5, 0), 0.3)
        models.append(sketch_model)

# Import the text-based 3D model
if "{text_3d_path}":
    text_model = import_model(r"{text_3d_path}", (3, -3, 0))
    if text_model:
        add_text("From Description", (3, -5, 0), 0.3)
        models.append(text_model)

# Set up a simple studio lighting
def create_studio_lighting():
    # Create a new collection for lights
    light_collection = bpy.data.collections.new("Studio Lighting")
    bpy.context.scene.collection.children.link(light_collection)
    
    # Create three point lighting
    key_light = bpy.data.lights.new(name="Key Light", type='AREA')
    key_light.energy = 300
    key_light_obj = bpy.data.objects.new(name="Key Light", object_data=key_light)
    key_light_obj.location = (5, -5, 5)
    key_light_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
    light_collection.objects.link(key_light_obj)
    
    fill_light = bpy.data.lights.new(name="Fill Light", type='AREA')
    fill_light.energy = 150
    fill_light_obj = bpy.data.objects.new(name="Fill Light", object_data=fill_light)
    fill_light_obj.location = (-5, -2, 3)
    fill_light_obj.rotation_euler = (math.radians(30), 0, math.radians(-45))
    light_collection.objects.link(fill_light_obj)
    
    rim_light = bpy.data.lights.new(name="Rim Light", type='AREA')
    rim_light.energy = 200
    rim_light_obj = bpy.data.objects.new(name="Rim Light", object_data=rim_light)
    rim_light_obj.location = (0, 5, 4)
    rim_light_obj.rotation_euler = (math.radians(60), 0, math.radians(180))
    light_collection.objects.link(rim_light_obj)

create_studio_lighting()

# Set up camera
camera_data = bpy.data.cameras.new("Ideation Camera")
camera_object = bpy.data.objects.new("Ideation Camera", camera_data)
bpy.context.scene.collection.objects.link(camera_object)
bpy.context.scene.camera = camera_object

# Position camera to see all objects
camera_object.location = (0, -10, 2)
camera_object.rotation_euler = (math.radians(80), 0, 0)

# Save the file
bpy.ops.wm.save_as_mainfile(filepath=r"{output_path}")
print(f"Ideation scene created and saved to {{output_path}}")
"""
        
        # Write the script to a temporary file
        script_path = os.path.join(tempfile.gettempdir(), "create_ideation_scene.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Run Blender with the script
        try:
            subprocess.run([
                self.blender_path,
                "--background",
                "--python", script_path
            ], check=True)
            
            print(f"Ideation scene created and saved to {output_path}")
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating ideation scene: {e}")
            return None
        finally:
            # Clean up the temporary script
            if os.path.exists(script_path):
                os.remove(script_path)

    def launch_blender_with_scene(self, blend_file_path: str) -> bool:
        """
        Launch Blender with the specified .blend file.
        
        Args:
            blend_file_path: Path to the Blender file to open
            
        Returns:
            True if Blender was launched successfully, False otherwise
        """
        if not os.path.exists(blend_file_path):
            print(f"Blend file not found: {blend_file_path}")
            return False
        
        try:
            subprocess.Popen([
                self.blender_path,
                blend_file_path
            ])
            return True
        except Exception as e:
            print(f"Error launching Blender: {e}")
            return False