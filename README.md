# Blender Ideation Agent

An AI-powered agent for Blender ideation sessions using Claude 3.7 and Python 3.11.

## Features

- 🎨 **Ideation Whiteboard**: Visual canvas for brainstorming Blender projects
- 🤖 **AI-Powered**: Leverages Claude 3.7 for natural language understanding
- 🖌️ **Sketch to 3D**: Convert rough sketches into 3D models
- 📝 **Text to 3D**: Generate 3D models from text descriptions
- 🔄 **Visual Pipeline**: See the transformation from idea to 3D model
- 🧩 **Blender Integration**: Seamlessly move from ideation to Blender

## Installation

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)
- Blender 3.6+ (optional, for direct Blender integration)

### Setup

1. Clone the repository:
   ```bash
   git clone git@github.com:kevinlu1996/sketch-ideation.git
   ```

2. Install dependencies with Poetry:
   ```bash
   poetry lock
   poetry install
   ```

3. Create a `.env` file in the project root with your API keys:
   ```
   ANTHROPIC_API_KEY=your_claude_api_key_here
   ```

## Usage

1. Start the application:
   ```bash
   poetry run streamlit run blender_ideation/app.py
   ```

2. Navigate to the provided URL (typically `http://localhost:8501`)

3. Create a new ideation session by entering:
   - Concept (e.g., "3D robot")
   - Project Type (e.g., "Video Game")
   - Genre (e.g., "Sci-Fi")
   - Optional description

4. Upload a sketch or drawing

5. Follow the ideation pipeline:
   - Sketch → Image → 3D model
   - Text → 3D model

6. Save your ideation whiteboard for future reference

7. (Optional) Export to Blender for further development

## Project Structure

```
blender-ideation-agent/
├── blender_ideation/        # Main package
│   ├── app.py               # Streamlit application
│   ├── ai_services.py       # Integration with Claude and other AI services
│   ├── blender_integration.py  # Blender connectivity
│   ├── data_models.py       # Data structures
│   └── utils.py             # Helper functions
└── assets/                  # Static assets
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Formatting Code

```bash
poetry run black blender_ideation
poetry run isort blender_ideation
```

## License

[MIT License](LICENSE)

## Acknowledgements

- Anthropic's Claude 3.7 for natural language processing
- Streamlit for the web application framework
- Blender Foundation for the amazing 3D software
