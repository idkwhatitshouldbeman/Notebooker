# Notebooker

An agentic Engineering Notebook (EN) writer specialized for robotics with localhost web interface.

## Features

- **Intelligent Content Analysis**: Automatically analyzes engineering notebook sections for completeness and clarity
- **Dynamic Planning**: Maintains a planning sheet tracking sections needing work, user questions, and decisions
- **LLM Integration**: Supports multiple local LLM backends (GPT4All, Transformers, Fallback)
- **Web Interface**: Modern Flask-based web interface for easy interaction
- **Image Handling**: Automatic placeholder generation for images with metadata
- **Modular Design**: Easy to extend and customize for different engineering domains

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Web Interface**:
   ```bash
   python app.py
   ```

3. **Access the Interface**:
   Open your browser to `http://localhost:5000`

## Project Structure

```
Notebooker/
├── app.py                 # Flask web application
├── en_writer.py          # Core EN writer module
├── llm_backend.py        # LLM backend integration
├── image_handler.py      # Image processing capabilities
├── requirements.txt      # Python dependencies
├── en_files/            # Engineering notebook files
├── static/              # Web interface assets
├── templates/           # HTML templates
└── README.md           # This file
```

## Core Functions

- `load_en_sections()` - Load and parse EN files
- `analyze_sections_for_gaps()` - Identify content gaps
- `generate_user_questions()` - Create targeted questions
- `draft_new_entry()` - Generate new content
- `rewrite_entry()` - Improve existing content
- `save_en_files()` - Save updated files
- `log_agent_activity()` - Track agent actions

## LLM Backends

1. **GPT4All** (Primary) - Local, open-source LLM
2. **Transformers** (Fallback) - HuggingFace models
3. **Template-based** (Always available) - Structured responses

## Usage

The system is designed to work iteratively with user feedback:

1. Load your engineering notebook files
2. System analyzes content for gaps
3. Generates targeted questions
4. User provides answers
5. System drafts/improves content
6. Process repeats until complete

## Contributing

This project is designed for robotics engineering documentation but can be adapted for other engineering domains.

## License

Open source - feel free to modify and extend for your needs.
