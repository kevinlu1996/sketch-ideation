"""
AI services for the Blender Ideation Agent.
Handles integration with Claude 3.7 and other AI models.
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple

import numpy as np
from anthropic import Anthropic
from PIL import Image

from blender_ideation.utils import add_color_tint


class ClaudeService:
    """Integration with Anthropic's Claude 3.7 API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude service.
        
        Args:
            api_key: Anthropic API key (will use environment variable if not provided)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key is required. Either pass it directly or "
                "set the ANTHROPIC_API_KEY environment variable."
            )
        
        # Initialize the Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        
        # Default model, can be overridden in method calls
        self.default_model = "claude-3-7-sonnet-20250219"  # Changed to correct model name
    
    def extract_tags(self, text_input: str, max_tags: int = 10) -> List[str]:
        """
        Extract relevant tags from user input using Claude.
        
        Args:
            text_input: Text to extract tags from
            max_tags: Maximum number of tags to extract
            
        Returns:
            List of extracted tags
        """
        prompt = f"""
        Extract up to {max_tags} relevant tags from this project description.
        Return only the tags as a JSON array of strings.
        
        Description: {text_input}
        """
        
        response = self.client.messages.create(
            model=self.default_model,
            max_tokens=100,
            system="You extract relevant keywords as tags from text. Respond only with a JSON array of strings.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Extract the JSON array from the response
            content = response.content[0].text
            # Find the JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                tags = json.loads(json_match.group(0))
                return tags
            return []
        except Exception as e:
            print(f"Error extracting tags: {e}")
            return []
    
    def generate_3d_prompt(
        self, 
        concept: str, 
        project_type: str, 
        genre: str, 
        description: str
    ) -> str:
        """
        Generate a detailed prompt for text-to-3D generation.
        
        Args:
            concept: Main concept (e.g., "3D robot")
            project_type: Type of project (e.g., "Video Game")
            genre: Genre (e.g., "Sci-Fi")
            description: Additional description
            
        Returns:
            Detailed prompt for text-to-3D generation
        """
        prompt = f"""
        Create a detailed 3D model description for:
        - Concept: {concept}
        - Project Type: {project_type}
        - Genre: {genre}
        - Description: {description}
        
        Provide specific details about shape, texture, color, and proportions 
        that would help a 3D modeling system create an appropriate model.
        Include details about materials, lighting, and environment if relevant.
        """
        
        response = self.client.messages.create(
            model=self.default_model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def summarize_project(
        self, 
        concept: str, 
        project_type: str, 
        genre: str, 
        description: str
    ) -> str:
        """
        Generate a concise summary of the project.
        
        Args:
            concept: Main concept
            project_type: Type of project
            genre: Genre
            description: Additional description
            
        Returns:
            Concise project summary
        """
        prompt = f"""
        Create a concise summary (2-3 sentences) for this Blender project:
        - Concept: {concept}
        - Project Type: {project_type}
        - Genre: {genre}
        - Description: {description}
        """
        
        response = self.client.messages.create(
            model=self.default_model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text.strip()
    
    def suggest_improvements(self, session_data: Dict) -> List[str]:
        """
        Suggest improvements for the ideation session.
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            List of improvement suggestions
        """
        # Construct a prompt based on the session data
        concept = session_data.get("title", "Unknown")
        project_type = session_data.get("project_type", "Unknown")
        genre = session_data.get("genre", "Unknown")
        description = session_data.get("description", "")
        
        prompt = f"""
        Suggest 3-5 specific improvements or additions for this Blender project:
        - Concept: {concept}
        - Project Type: {project_type}
        - Genre: {genre}
        - Description: {description}
        
        Format your response as a JSON array of strings, where each string is a specific suggestion.
        """
        
        response = self.client.messages.create(
            model=self.default_model,
            max_tokens=350,
            system="You provide helpful suggestions for 3D design projects. Respond only with a JSON array of strings.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            # Extract the JSON array from the response
            content = response.content[0].text
            # Find the JSON array in the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                suggestions = json.loads(json_match.group(0))
                return suggestions
            return []
        except Exception as e:
            print(f"Error extracting suggestions: {e}")
            return []


class MockImageGenerator:
    """
    Mock service for sketch-to-image conversion.
    In a production environment, this would be replaced with a real AI image generation service.
    """
    
    def convert_sketch_to_image(self, sketch_path: str, output_dir: str) -> Optional[str]:
        """
        Convert a sketch to a rendered image.
        
        Args:
            sketch_path: Path to the sketch image
            output_dir: Directory to save the output image
            
        Returns:
            Path to the output image, or None if conversion fails
        """
        try:
            # Load the sketch
            img = Image.open(sketch_path)
            
            # For the mock implementation, just add a blue tint
            # In a real implementation, this would use an AI model
            processed = add_color_tint(img, (100, 100, 255), 0.3)
            
            # Save the processed image
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"rendered_{os.path.basename(sketch_path)}")
            processed.save(output_path)
            
            return output_path
        except Exception as e:
            print(f"Error converting sketch to image: {e}")
            return None


class Mock3DGenerator:
    """
    Mock service for 3D model generation.
    In a production environment, this would be replaced with a real 3D generation service.
    """
    
    def sketch_to_3d(self, image_path: str, output_dir: str) -> Optional[str]:
        """
        Convert an image to a 3D model.
        
        Args:
            image_path: Path to the input image
            output_dir: Directory to save the output model
            
        Returns:
            Path to the output model, or None if conversion fails
        """
        # For the mock implementation, just return a placeholder path
        # In a real implementation, this would use an AI model or API
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"model_from_sketch_{os.path.basename(image_path)}.glb")
        
        # Create an empty file to simulate the output
        with open(output_path, 'wb') as f:
            f.write(b'MOCK 3D MODEL')
        
        return output_path
    
    def text_to_3d(self, text_prompt: str, output_dir: str) -> Optional[str]:
        """
        Generate a 3D model from a text prompt.
        
        Args:
            text_prompt: Text description of the model
            output_dir: Directory to save the output model
            
        Returns:
            Path to the output model, or None if generation fails
        """
        # For the mock implementation, just return a placeholder path
        # In a real implementation, this would use an AI model or API
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename based on the first few words of the prompt
        words = text_prompt.split()[:3]
        filename = "_".join(words).lower()
        filename = re.sub(r'[^\w\-_]', '', filename)  # Remove non-alphanumeric chars
        
        output_path = os.path.join(output_dir, f"model_from_text_{filename}.glb")
        
        # Create an empty file to simulate the output
        with open(output_path, 'wb') as f:
            f.write(b'MOCK 3D MODEL')
        
        return output_path