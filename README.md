# Notebooker

An agentic Engineering Notebook (EN) writer specialized for robotics with localhost web interface.

## 🚀 **Development Workflow**

**Primary Development**: This project is developed on **localhost** for rapid iteration and testing.

**GitHub Deployment**: Only push to GitHub for:
- ✅ Large feature additions
- ✅ Major bug fixes
- ✅ Working implementations
- ✅ Significant UI/UX improvements

**GitHub Repository**: https://github.com/idkwhatitshouldbeman/Notebooker.git

## 🏠 **Local Development Setup**

### **Quick Start (Localhost)**
```powershell
# Navigate to project directory
cd C:\Users\arvin\Downloads\Notebookr

# Install dependencies (if needed)
pip install -r requirements.txt

# Start the application
python app.py

# Access at: http://localhost:5000
```

### **Virtual Environment (Optional)**
```powershell
# Create virtual environment
python -m venv notebooker_env

# Activate (try these in order)
notebooker_env\Scripts\activate.bat
# OR
notebooker_env\Scripts\activate
# OR
& "notebooker_env\Scripts\Activate.ps1"

# Install dependencies
pip install -r requirements.txt

# Start application
python app.py
```

## 🎨 **Current Theme & Features**

### **Beautiful Aesthetic Theme**
- **Flowing Blue & Pitch Black** color scheme
- **Animated background** with 15-second gradient flow
- **Hover animations** on cards and navigation
- **Glass morphism** effects with backdrop blur
- **Custom scrollbars** with blue gradients
- **Responsive design** with Bootstrap integration

### **Core Features**
- **Intelligent Content Analysis**: Automatically analyzes engineering notebook sections
- **Dynamic Planning**: Maintains planning sheet tracking work progress
- **LLM Integration**: Multiple backends (GPT4All, Transformers, Fallback)
- **Web Interface**: Modern Flask-based interface
- **Image Handling**: Automatic placeholder generation with metadata
- **Backup System**: Automated GitHub backups with retention policies

## 📁 **Project Structure**

```
Notebooker/
├── app.py                 # Flask web application (main entry point)
├── wsgi.py               # WSGI entry point for Render deployment
├── en_writer.py          # Core EN writer module
├── llm_backend.py        # LLM backend integration
├── image_handler.py      # Image processing capabilities
├── backup_system.py      # Automated backup system
├── start.py              # Local startup script
├── start_render.py       # Render-optimized startup
├── backup.py             # GitHub backup script
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
├── en_files/            # Engineering notebook files
│   ├── system_overview.txt
│   ├── hardware_design.txt
│   ├── software_architecture.txt
│   └── testing_procedures.txt
├── templates/           # HTML templates with beautiful theme
│   ├── base.html        # Base template with flowing animations
│   ├── index.html       # Dashboard with status cards
│   ├── sections.html    # Section management
│   ├── analyze.html     # Content gap analysis
│   ├── draft.html       # New section creation
│   ├── rewrite.html     # Content improvement
│   ├── view_section.html # Section viewing
│   ├── planning.html    # Planning sheet management
│   └── settings.html    # System configuration
├── images/              # Image files and metadata
├── backups/             # Automated backups
└── README.md           # This file
```

## 🔧 **Development Notes**

### **Theme Customization**
- **CSS Variables**: All colors defined in `:root` in `templates/base.html`
- **Animations**: Flowing background, hover effects, status card animations
- **Responsive**: Bootstrap 5 with custom dark theme
- **Icons**: FontAwesome 6 integration

### **LLM Backend System**
- **Primary**: GPT4All (local, open-source)
- **Fallback**: HuggingFace Transformers
- **Template**: Always-available structured responses
- **Modular**: Easy to add new backends

### **Deployment Status**
- **Localhost**: Fully functional with all features
- **Render**: Deployed with fallback LLM mode (no heavy dependencies)
- **GitHub**: Auto-backup system with consistent version control

## 🚀 **Deployment Commands**

### **Local Development**
```powershell
python app.py
```

### **GitHub Backup**
```powershell
python backup.py
```

### **Render Deployment**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:application`
- **Environment**: Production mode with fallback LLM

## 📝 **Important Development Guidelines**

1. **Test Locally First**: Always test new features on localhost before pushing
2. **Beautiful Theme**: Maintain the flowing blue and pitch black aesthetic
3. **Modular Design**: Keep LLM backends easily swappable
4. **Error Handling**: Graceful fallbacks for missing dependencies
5. **Documentation**: Update this README for major changes

## 🎯 **Current Status**

- ✅ **Core EN Writer**: Fully functional
- ✅ **Beautiful Web Interface**: Flowing blue theme with animations
- ✅ **LLM Integration**: Multiple backend support
- ✅ **Image Handling**: Placeholder system with metadata
- ✅ **Backup System**: Automated GitHub integration
- ✅ **Local Development**: Ready for rapid iteration
- ✅ **Render Deployment**: Live with fallback mode

## 🔮 **Future Development Ideas**

- **Enhanced LLM Models**: Add more local AI models
- **Advanced Image Processing**: BLIP integration for auto-captioning
- **Collaborative Features**: Multi-user support
- **Export Options**: PDF, Word, LaTeX export
- **Template Library**: Pre-built EN templates for different domains
- **Version Control**: Git-like versioning for EN sections

## 📞 **Support & Contributing**

This project is designed for robotics engineering documentation but can be adapted for other engineering domains. The modular architecture makes it easy to extend and customize.

**Remember**: Develop on localhost, push to GitHub for major changes, and maintain the beautiful flowing blue aesthetic! 🎨✨
