# Assets Directory

This directory contains static assets for the Blender Ideation Agent.

## Structure

- `images/` - Static images used in the UI (not user uploads)
- `examples/` - Example sketches and models
- `templates/` - Template files for different project types

## Generated Assets

Note that user-generated assets (sketches, images, 3D models) are stored in temporary directories by default.
These are configured in the `app.py` file and typically include:

- `SKETCHES_DIR` - User-uploaded sketches
- `IMAGES_DIR` - AI-enhanced images
- `MODELS_DIR` - Generated 3D models
- `SESSIONS_DIR` - Saved session data

To change the storage location, modify the paths in the `app.py` file.