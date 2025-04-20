"""
Utility functions for the Blender Ideation Agent.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from PIL import Image


def ensure_directory(directory_path: str) -> str:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        The absolute path to the directory
    """
    path = os.path.abspath(directory_path)
    os.makedirs(path, exist_ok=True)
    return path


def save_image(image: Image.Image, directory: str, filename: Optional[str] = None) -> str:
    """
    Save an image to a directory.
    
    Args:
        image: PIL Image object
        directory: Directory to save the image in
        filename: Optional filename (will generate one if not provided)
        
    Returns:
        Path to the saved image
    """
    # Ensure the directory exists
    ensure_directory(directory)
    
    # Generate a filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.png"
    
    # Add extension if not present
    if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filename += '.png'
    
    # Construct the full path
    filepath = os.path.join(directory, filename)
    
    # Save the image
    image.save(filepath)
    
    return filepath


def load_image(filepath: str) -> Optional[Image.Image]:
    """
    Load an image from a file.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        PIL Image object, or None if loading fails
    """
    try:
        return Image.open(filepath)
    except Exception as e:
        print(f"Error loading image {filepath}: {e}")
        return None


def add_color_tint(image: Image.Image, color: Tuple[int, int, int], intensity: float = 0.3) -> Image.Image:
    """
    Add a color tint to an image.
    
    Args:
        image: PIL Image object
        color: RGB tuple (0-255 for each channel)
        intensity: How strong the tint should be (0.0-1.0)
        
    Returns:
        New image with color tint applied
    """
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Create a solid color image with the same size
    tint = Image.new('RGBA', image.size, (*color, int(255 * intensity)))
    
    # Composite the images
    return Image.alpha_composite(image, tint)


def find_blender_executable() -> Optional[str]:
    """
    Find the Blender executable on the system.
    
    Returns:
        Path to Blender executable if found, None otherwise
    """
    # Common locations for Blender
    possible_locations = [
        # Windows
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        # macOS
        "/Applications/Blender.app/Contents/MacOS/Blender",
        # Linux
        "/usr/bin/blender",
        "/usr/local/bin/blender",
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            return location
    
    return None


def create_temp_file(suffix: str = '.txt') -> str:
    """
    Create a temporary file.
    
    Args:
        suffix: File extension
        
    Returns:
        Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        return tmp.name


def save_session_to_json(session: Dict, filepath: str) -> bool:
    """
    Save a session dictionary to a JSON file.
    
    Args:
        session: Session dictionary
        filepath: Path to save the JSON file
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(session, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving session to {filepath}: {e}")
        return False


def load_session_from_json(filepath: str) -> Optional[Dict]:
    """
    Load a session dictionary from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Session dictionary if loaded successfully, None otherwise
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading session from {filepath}: {e}")
        return None


def extract_tags_from_text(text: str) -> List[str]:
    """
    Extract potential tags from text using simple heuristics.
    This is a fallback method when AI services are not available.
    
    Args:
        text: Text to extract tags from
        
    Returns:
        List of potential tags
    """
    # Convert to lowercase and split by common separators
    words = text.lower().replace(',', ' ').replace(';', ' ').replace('.', ' ').split()
    
    # Filter out common stop words and short words
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'of'}
    potential_tags = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Deduplicate
    return list(set(potential_tags))