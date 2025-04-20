"""
Main application for the Blender Ideation Agent.
Streamlit-based user interface for the ideation whiteboard.
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv

from blender_ideation.ai_services import ClaudeService, Mock3DGenerator, MockImageGenerator
from blender_ideation.blender_integration import BlenderIntegration
from blender_ideation.data_models import IdeationSession
from blender_ideation.utils import ensure_directory, save_session_to_json

# Load environment variables from .env file
load_dotenv()

# Define asset directories
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
SKETCHES_DIR = os.path.join(BASE_DIR, "sketches")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SESSIONS_DIR = os.path.join(BASE_DIR, "sessions")


class BlenderIdeationApp:
    """Main application class for the Blender Ideation Agent."""
    
    def __init__(self):
        """Initialize the application."""
        # We'll initialize services later in the run method
        self.claude = None
        self.image_generator = None
        self.model_generator = None
        self.blender = None
    
    def _initialize_services(self):
        """Initialize AI and Blender services."""
        try:
            self.claude = ClaudeService()
            print("Claude service initialized")
        except ValueError as e:
            st.error(f"Error initializing Claude service: {e}")
            self.claude = None
        
        self.image_generator = MockImageGenerator()
        self.model_generator = Mock3DGenerator()
        
        try:
            self.blender = BlenderIntegration()
            print(f"Blender integration initialized with executable: {self.blender.blender_path}")
        except ValueError as e:
            st.warning(f"Blender integration not available: {e}")
            self.blender = None
    
    def _initialize_session_state(self):
        """Initialize Streamlit session state."""
        # Initialize session state for storing sessions
        if 'sessions' not in st.session_state:
            st.session_state.sessions = {}
        
        # Current session
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None
    
    @property
    def current_session(self) -> Optional[IdeationSession]:
        """Get the current ideation session."""
        if not st.session_state.current_session_id:
            return None
        
        return st.session_state.sessions.get(st.session_state.current_session_id)
    
    @current_session.setter
    def current_session(self, session: Optional[IdeationSession]):
        """Set the current ideation session."""
        if session is None:
            st.session_state.current_session_id = None
            return
        
        # Store the session
        st.session_state.sessions[session.id] = session
        st.session_state.current_session_id = session.id
    
    def create_new_session(
        self, 
        title: str, 
        project_type: str, 
        genre: str, 
        description: str
    ) -> IdeationSession:
        """
        Create a new ideation session.
        
        Args:
            title: Project concept/title
            project_type: Type of project
            genre: Genre
            description: Additional description
            
        Returns:
            New ideation session
        """
        # Extract tags using Claude
        tags = []
        if self.claude:
            tags = self.claude.extract_tags(f"{title} {project_type} {genre} {description}")
        
        # Create session
        session = IdeationSession(
            id=str(uuid.uuid4()),
            title=title,
            project_type=project_type,
            genre=genre,
            description=description,
            tags=tags
        )
        
        # Set as current session
        self.current_session = session
        return session
    
    def process_sketch(self, uploaded_file) -> Optional[IdeationSession]:
        """
        Process an uploaded sketch.
        
        Args:
            uploaded_file: Uploaded sketch file
            
        Returns:
            Updated session, or None if processing fails
        """
        if not self.current_session:
            st.error("No active session")
            return None
        
        # Save the uploaded file
        sketch_path = os.path.join(SKETCHES_DIR, f"{self.current_session.id}_{uploaded_file.name}")
        with open(sketch_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        self.current_session.sketch_path = sketch_path
        
        # Convert sketch to image
        st.info("Using sketch-to-image tool...")
        image_path = self.image_generator.convert_sketch_to_image(sketch_path, IMAGES_DIR)
        if not image_path:
            st.error("Failed to convert sketch to image")
            return self.current_session
        
        self.current_session.rendered_image_path = image_path
        
        # Convert image to 3D
        st.info("Using image-to-3D tool...")
        model_path = self.model_generator.sketch_to_3d(image_path, MODELS_DIR)
        if not model_path:
            st.error("Failed to convert image to 3D model")
            return self.current_session
        
        self.current_session.sketch_3d_path = model_path
        
        # Update session
        self.current_session = self.current_session
        return self.current_session
    
    def generate_text_3d(self) -> Optional[IdeationSession]:
        """
        Generate 3D model from text description.
        
        Returns:
            Updated session, or None if generation fails
        """
        if not self.current_session:
            st.error("No active session")
            return None
        
        st.info("Using text-to-3D tool...")
        
        # Generate detailed prompt for 3D model
        prompt = ""
        if self.claude:
            prompt = self.claude.generate_3d_prompt(
                self.current_session.title,
                self.current_session.project_type,
                self.current_session.genre,
                self.current_session.description
            )
        else:
            # Fallback prompt if Claude is not available
            prompt = f"A 3D {self.current_session.title} for a {self.current_session.project_type} in the {self.current_session.genre} genre."
        
        # Generate 3D model from text
        model_path = self.model_generator.text_to_3d(prompt, MODELS_DIR)
        if not model_path:
            st.error("Failed to generate 3D model from text")
            return self.current_session
        
        self.current_session.text_3d_path = model_path
        
        # Update session
        self.current_session = self.current_session
        return self.current_session
    
    def save_session(self) -> bool:
        """
        Save the current session.
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.current_session:
            st.error("No active session to save")
            return False
        
        # Save session data to JSON
        session_path = os.path.join(SESSIONS_DIR, f"{self.current_session.id}.json")
        success = save_session_to_json(self.current_session.to_dict(), session_path)
        
        if success:
            st.success("Ideation Whiteboard saved successfully!")
        else:
            st.error("Failed to save Ideation Whiteboard")
        
        return success
    
    def export_to_blender(self) -> Optional[str]:
        """
        Export the current session to Blender.
        
        Returns:
            Path to the Blender file, or None if export fails
        """
        if not self.current_session:
            st.error("No active session to export")
            return None
        
        if not self.blender:
            st.error("Blender integration not available")
            return None
        
        st.info("Exporting to Blender...")
        
        # Create Blender scene
        blend_file = self.blender.create_ideation_scene(
            self.current_session.to_dict(),
            os.path.join(BASE_DIR, f"{self.current_session.id}.blend")
        )
        
        if not blend_file:
            st.error("Failed to create Blender scene")
            return None
        
        self.current_session.blender_file_path = blend_file
        self.current_session = self.current_session
        
        st.success(f"Exported to Blender: {blend_file}")
        return blend_file
    
    def run(self):
        """Run the Streamlit application."""
        # Initialize services and session state
        self._initialize_services()
        self._initialize_session_state()
        
        st.title("Blender Ideation Whiteboard")
        
        # Sidebar for session management
        with st.sidebar:
            st.header("Session")
            if st.button("New Session"):
                self.current_session = None
            
            # List existing sessions
            if st.session_state.sessions:
                st.subheader("Previous Sessions")
                for session_id, session in st.session_state.sessions.items():
                    if st.button(f"{session.title} ({session.project_type})"):
                        self.current_session = session
        
        # Main area
        if self.current_session is None:
            # New session form
            st.header("Start New Ideation Session")
            with st.form("new_session"):
                title = st.text_input("Concept", "3D robot")
                project_type = st.text_input("Project Type", "Video Game")
                genre = st.text_input("Genre", "Sci-Fi")
                description = st.text_area("Additional Description", "")
                
                submit = st.form_submit_button("Start Session")
                if submit:
                    self.create_new_session(
                        title, project_type, genre, description
                    )
        else:
            # Show existing session
            st.header("Ideation Whiteboard")
            
            # Display session info as tags
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"**Concept**: {self.current_session.title}")
            with col2:
                st.markdown(f"**Project Type**: {self.current_session.project_type}")
            with col3:
                st.markdown(f"**Genre**: {self.current_session.genre}")
            
            if self.current_session.tags:
                st.markdown("**Tags**: " + ", ".join(self.current_session.tags))
            
            if self.current_session.description:
                with st.expander("Description", expanded=False):
                    st.write(self.current_session.description)
            
            # Canvas for sketching or upload
            st.subheader("Your Robot Sketch")
            uploaded_file = st.file_uploader(
                "Upload your sketch", 
                type=["png", "jpg", "jpeg"]
            )
            
            if uploaded_file is not None and not self.current_session.sketch_path:
                if st.button("Process Sketch"):
                    self.process_sketch(uploaded_file)
            
            # Display the processing pipeline
            if self.current_session.sketch_path:
                st.subheader("Ideation Pipeline")
                
                cols = st.columns(3)
                
                # Display the sketch
                with cols[0]:
                    st.markdown("**Original Sketch**")
                    if self.current_session.sketch_path:
                        st.image(self.current_session.sketch_path, use_column_width=True)
                
                # Display the rendered image
                with cols[1]:
                    st.markdown("**AI-Enhanced Image**")
                    if self.current_session.rendered_image_path:
                        st.image(self.current_session.rendered_image_path, use_column_width=True)
                    else:
                        st.info("Image will appear here after processing")
                
                # Display placeholder for 3D model from sketch
                with cols[2]:
                    st.markdown("**3D Model from Sketch**")
                    if self.current_session.sketch_3d_path:
                        st.info("3D model generated from sketch")
                        st.markdown(f"Path: `{self.current_session.sketch_3d_path}`")
                        # In a real app, you would render the 3D model here
                    else:
                        st.info("3D model will appear here")
            
            # Text to 3D section
            if self.current_session.sketch_path and not self.current_session.text_3d_path:
                if st.button("Generate 3D Model from Description"):
                    self.generate_text_3d()
            
            if self.current_session.text_3d_path:
                st.subheader("Text-to-3D Model")
                st.info("3D model generated from text description")
                st.markdown(f"Path: `{self.current_session.text_3d_path}`")
                # In a real app, you would render the 3D model here
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Save Ideation Whiteboard"):
                    self.save_session()
            
            with col2:
                if self.blender and self.current_session.sketch_3d_path:
                    if st.button("Export to Blender"):
                        blend_file = self.export_to_blender()
                        if blend_file and st.button("Open in Blender"):
                            self.blender.launch_blender_with_scene(blend_file)


def main():
    """Main entry point."""
    # Set page config FIRST before any other Streamlit commands
    st.set_page_config(
        page_title="Blender Ideation Whiteboard",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Ensure directories exist
    for directory in [SKETCHES_DIR, IMAGES_DIR, MODELS_DIR, SESSIONS_DIR]:
        ensure_directory(directory)
    
    # Create and run the app
    app = BlenderIdeationApp()
    app.run()


if __name__ == "__main__":
    main()