"""
Data models for the Blender Ideation Agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
import uuid


@dataclass
class IdeationSession:
    """Represents an ideation session for a Blender project."""
    
    # Basic metadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Untitled Project"
    project_type: str = "Unknown"
    genre: str = "Unknown"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Asset paths
    sketch_path: Optional[str] = None
    rendered_image_path: Optional[str] = None
    sketch_3d_path: Optional[str] = None
    text_3d_path: Optional[str] = None
    blender_file_path: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert the session to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "project_type": self.project_type,
            "genre": self.genre,
            "description": self.description,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "sketch_path": self.sketch_path,
            "rendered_image_path": self.rendered_image_path,
            "sketch_3d_path": self.sketch_3d_path,
            "text_3d_path": self.text_3d_path,
            "blender_file_path": self.blender_file_path,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IdeationSession":
        """Create a session from a dictionary."""
        session_data = data.copy()
        
        # Convert string timestamps to datetime objects
        if "created_at" in session_data and isinstance(session_data["created_at"], str):
            session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
        
        if "updated_at" in session_data and isinstance(session_data["updated_at"], str):
            session_data["updated_at"] = datetime.fromisoformat(session_data["updated_at"])
        
        return cls(**session_data)


@dataclass
class IdeationTag:
    """Represents a searchable tag for ideation sessions."""
    
    name: str
    category: str  # e.g., "concept", "project_type", "genre", "description"
    session_id: str
    
    def to_dict(self) -> dict:
        """Convert the tag to a dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "session_id": self.session_id,
        }


@dataclass
class AppSettings:
    """Application settings."""
    
    blender_executable_path: Optional[str] = None
    default_save_directory: Optional[str] = None
    api_keys: dict = field(default_factory=dict)
    theme: str = "light"
    
    def to_dict(self) -> dict:
        """Convert the settings to a dictionary."""
        return {
            "blender_executable_path": self.blender_executable_path,
            "default_save_directory": self.default_save_directory,
            "api_keys": self.api_keys,
            "theme": self.theme,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        """Create settings from a dictionary."""
        return cls(**data)