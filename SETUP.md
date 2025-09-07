# Notebooker Setup Guide

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- Git (for version control)
- At least 4GB RAM (for LLM models)
- 2GB free disk space

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/idkwhatitshouldbeman/Notebooker.git
cd Notebooker

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p en_files images backups static templates
```

### 3. First Run

```bash
# Start the web interface
python app.py
```

Open your browser to `http://localhost:5000`

## Detailed Setup

### Environment Setup

1. **Create Virtual Environment** (Recommended):
```bash
python -m venv notebooker_env
source notebooker_env/bin/activate  # On Windows: notebooker_env\Scripts\activate
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

### LLM Backend Configuration

#### Option 1: GPT4All (Recommended)
```bash
# GPT4All will automatically download models on first use
# No additional setup required
```

#### Option 2: HuggingFace Transformers
```bash
# Models will be downloaded automatically
# Ensure you have sufficient disk space (2-4GB per model)
```

#### Option 3: Fallback Mode
- No additional setup required
- Uses template-based responses

### Directory Structure

```
Notebooker/
├── app.py                 # Main Flask application
├── en_writer.py          # Core EN writer module
├── llm_backend.py        # LLM backend integration
├── image_handler.py      # Image processing
├── backup_system.py      # Automated backup system
├── requirements.txt      # Python dependencies
├── en_files/            # Engineering notebook files
│   ├── system_overview.txt
│   ├── hardware_design.txt
│   ├── software_architecture.txt
│   └── testing_procedures.txt
├── images/              # Image files and metadata
├── backups/             # Automated backups
├── static/              # Web interface assets
├── templates/           # HTML templates
└── README.md           # Project documentation
```

## Configuration

### Basic Configuration

1. **Edit `app.py`** to modify:
   - Port number (default: 5000)
   - Host address (default: 0.0.0.0)
   - Debug mode

2. **Backup Settings** in `backup_system.py`:
   - Auto-backup interval
   - Retention policy
   - File inclusion/exclusion patterns

### Advanced Configuration

#### Custom LLM Models
Edit `llm_backend.py` to add custom models:

```python
# Add your custom model
class CustomBackend(LLMBackend):
    def __init__(self, model_path):
        # Initialize your model
        pass
```

#### Custom File Formats
Modify `en_writer.py` to support additional file formats:

```python
def parse_en_file(self, filepath: str) -> str:
    # Add support for .md, .rst, etc.
    pass
```

## Usage

### Web Interface

1. **Dashboard**: Overview of system status
2. **Sections**: View and manage EN sections
3. **Analyze**: Run gap analysis on content
4. **Draft**: Create new sections with LLM assistance
5. **Planning**: Manage planning sheet and tasks
6. **Settings**: Configure system settings

### Command Line Usage

```bash
# Run core EN writer
python en_writer.py

# Test LLM backends
python llm_backend.py

# Create manual backup
python backup_system.py

# Test image handling
python image_handler.py
```

### API Usage

The system provides REST API endpoints:

```python
# Analyze content
POST /api/analyze_content
{
    "content": "Your engineering notebook content"
}

# Update planning sheet
POST /api/update_planning
{
    "sections_needing_work": ["section1", "section2"]
}

# Switch LLM backend
POST /api/switch_backend
{
    "backend_index": 0
}
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Change port in app.py
   app.run(port=5001)
   ```

2. **LLM Model Download Fails**:
   ```bash
   # Check internet connection
   # Ensure sufficient disk space
   # Try fallback mode
   ```

3. **Permission Errors**:
   ```bash
   # Ensure write permissions for en_files/, images/, backups/
   chmod 755 en_files images backups
   ```

4. **Memory Issues**:
   ```bash
   # Use smaller LLM models
   # Increase system RAM
   # Use fallback mode
   ```

### Performance Optimization

1. **For Large Projects**:
   - Use SSD storage
   - Increase RAM to 8GB+
   - Enable auto-backup cleanup

2. **For Better LLM Performance**:
   - Use GPU acceleration if available
   - Optimize model parameters
   - Use smaller, faster models

## Backup and Recovery

### Automatic Backups
- Enabled by default
- Runs every 30 minutes
- Keeps 10 most recent backups
- 7-day retention policy

### Manual Backups
```bash
# Create backup via web interface
# Or use command line:
python -c "from backup_system import BackupManager; BackupManager().create_backup()"
```

### Recovery
```bash
# Restore from backup
python -c "from backup_system import BackupManager; BackupManager().restore_backup('backup_name')"
```

## Development

### Adding New Features

1. **New LLM Backend**:
   - Extend `LLMBackend` class
   - Implement required methods
   - Add to `LLMManager`

2. **New File Format**:
   - Modify `parse_en_file()` method
   - Add format-specific parsing
   - Update file extensions

3. **New Web Interface**:
   - Add routes to `app.py`
   - Create HTML templates
   - Update navigation

### Testing

```bash
# Run basic tests
python -m pytest tests/

# Test specific modules
python -c "import en_writer; print('EN Writer OK')"
python -c "import llm_backend; print('LLM Backend OK')"
```

## Support

### Getting Help

1. **Check Documentation**: README.md and this file
2. **Review Logs**: Check console output for errors
3. **GitHub Issues**: Report bugs and request features
4. **Community**: Join discussions in GitHub Discussions

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- Core EN writer functionality
- LLM backend integration
- Web interface
- Image handling
- Automated backup system
