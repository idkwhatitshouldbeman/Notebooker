"""
Flask Web Interface for Agentic Engineering Notebook Writer
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response
import os
import json
from datetime import datetime
from pathlib import Path
import logging

from en_writer import ENWriter
from openrouter_backend import OpenRouterENWriter
from database_manager import SmartNotebookerDB
from auth import AuthManager

# Import livereload for development
try:
    from flask_livereload import LiveReload
    LIVERELOAD_AVAILABLE = True
except ImportError:
    LIVERELOAD_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change this in production

# Enable template auto-reload in debug mode
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Force Jinja2 to reload templates
app.jinja_env.auto_reload = True

# Add cache control headers for development
@app.after_request
def add_header(response):
    if 'no-cache' not in request.headers.get('Cache-Control', ''):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# Initialize livereload for development
if LIVERELOAD_AVAILABLE and app.debug:
    livereload = LiveReload(app)
    livereload.watch('templates/')
    livereload.watch('static/')

# Global instances
en_writer = None
db = None
auth = None

def initialize_en_writer():
    """Initialize the EN Writer with default directory"""
    global en_writer, db, auth
    base_dir = Path("en_files")
    base_dir.mkdir(exist_ok=True)
    
    # Initialize smart database (SQLite locally, Supabase if configured)
    db = SmartNotebookerDB()
    auth = AuthManager(db)
    en_writer = OpenRouterENWriter(str(base_dir))

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        # Check for session token in localStorage (handled by JavaScript)
        # For now, we'll allow access and handle auth in the frontend
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/auth')
def auth_page():
    """Authentication page"""
    return render_template('auth_standalone.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    if not auth:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'})
        
        result = auth.create_user(username, email, password)
        
        if result['success']:
            return jsonify({
                'success': True,
                'user_id': result['user_id'],
                'username': result['username'],
                'session_token': result['session_token']
            })
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': 'Registration failed'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    if not auth:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'})
        
        result = auth.login_user(username, password)
        
        if result['success']:
            # Set Flask session
            session['user_id'] = result['user_id']
            session['username'] = result['username']
            session['session_token'] = result['session_token']
            
            return jsonify({
                'success': True,
                'user_id': result['user_id'],
                'username': result['username'],
                'session_token': result['session_token']
            })
        else:
            return jsonify({'success': False, 'error': result['error']})
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'success': False, 'error': 'Login failed'})

@app.route('/api/auth/verify', methods=['POST'])
def verify_session():
    """Verify session token"""
    if not auth:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        session_token = data.get('session_token')
        
        if not session_token:
            return jsonify({'valid': False})
        
        user_info = auth.validate_session(session_token)
        
        if user_info:
            return jsonify({'valid': True, 'user': user_info})
        else:
            return jsonify({'valid': False})
            
    except Exception as e:
        logger.error(f"Session verification error: {e}")
        return jsonify({'valid': False})

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    if not auth:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        session_token = data.get('session_token')
        
        if session_token:
            auth.logout_user(session_token)
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'success': False, 'error': 'Logout failed'})

@app.route('/')
def index():
    """Main dashboard - redirect to auth if not logged in"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard (authenticated)"""
    if not en_writer:
        initialize_en_writer()
    
    # Get current user ID from session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_page'))
    
    # Get user's projects from database
    projects = db.get_user_projects(user_id) if db else []
    
    status = en_writer.en_writer.get_status_summary()
    return render_template('dashboard.html', status=status, projects=projects)

@app.route('/sections')
def sections():
    """View all sections"""
    if not en_writer:
        initialize_en_writer()
    
    sections = en_writer.en_writer.sections
    return render_template('sections.html', sections=sections)

@app.route('/analyze')
def analyze():
    """Analyze sections for gaps"""
    if not en_writer:
        initialize_en_writer()
    
    # Load sections if not already loaded
    if not en_writer.en_writer.sections:
        en_writer.en_writer.load_en_sections("en_files")
    
    gap_analysis = en_writer.en_writer.analyze_sections_for_gaps(en_writer.en_writer.sections)
    questions = en_writer.generate_contextual_questions(gap_analysis)
    
    return render_template('analyze.html', 
                         gap_analysis=gap_analysis, 
                         questions=questions)

@app.route('/draft', methods=['GET', 'POST'])
def draft():
    """Draft new section"""
    if not en_writer:
        initialize_en_writer()
    
    if request.method == 'POST':
        section_name = request.form.get('section_name')
        user_inputs = {
            'title': request.form.get('title', section_name),
            'overview': request.form.get('overview', ''),
            'technical_details': request.form.get('technical_details', ''),
            'implementation': request.form.get('implementation', ''),
            'testing': request.form.get('testing', ''),
            'results': request.form.get('results', ''),
            'improvements': request.form.get('improvements', ''),
            'tags': request.form.get('tags', 'robotics, engineering'),
            'comment': request.form.get('comment', '')
        }
        
        # Generate draft using LLM
        draft_content = en_writer.draft_new_entry_with_llm(section_name, user_inputs)
        
        # Save the draft
        en_writer.en_writer.sections[section_name] = draft_content
        en_writer.en_writer.save_en_files({section_name: draft_content})
        
        # Log activity
        en_writer.en_writer.log_agent_activity(
            "activity_log.json",
            {
                'action': 'draft_created',
                'section': section_name,
                'user_inputs': user_inputs
            }
        )
        
        flash(f'Draft created for section: {section_name}', 'success')
        return redirect(url_for('sections'))
    
    return render_template('draft.html')

@app.route('/rewrite/<section_name>', methods=['GET', 'POST'])
def rewrite(section_name):
    """Rewrite existing section"""
    if not en_writer:
        initialize_en_writer()
    
    if section_name not in en_writer.en_writer.sections:
        flash(f'Section {section_name} not found', 'error')
        return redirect(url_for('sections'))
    
    if request.method == 'POST':
        improvement_focus = request.form.get('improvement_focus', 'clarity and technical rigor')
        original_content = en_writer.en_writer.sections[section_name]
        
        # Rewrite using LLM
        improved_content = en_writer.rewrite_entry_with_llm(original_content, improvement_focus)
        
        # Save the improved version
        en_writer.en_writer.sections[section_name] = improved_content
        en_writer.en_writer.save_en_files({section_name: improved_content})
        
        # Log activity
        en_writer.en_writer.log_agent_activity(
            "activity_log.json",
            {
                'action': 'section_rewritten',
                'section': section_name,
                'improvement_focus': improvement_focus
            }
        )
        
        flash(f'Section {section_name} has been improved', 'success')
        return redirect(url_for('sections'))
    
    section_content = en_writer.en_writer.sections[section_name]
    return render_template('rewrite.html', 
                         section_name=section_name, 
                         section_content=section_content)

@app.route('/section/<section_name>')
def view_section(section_name):
    """View specific section"""
    if not en_writer:
        initialize_en_writer()
    
    if section_name not in en_writer.en_writer.sections:
        flash(f'Section {section_name} not found', 'error')
        return redirect(url_for('sections'))
    
    section_content = en_writer.en_writer.sections[section_name]
    return render_template('view_section.html', 
                         section_name=section_name, 
                         section_content=section_content)

@app.route('/planning')
def planning():
    """View planning sheet"""
    if not en_writer:
        initialize_en_writer()
    
    planning_data = en_writer.en_writer.planning_data
    return render_template('planning.html', planning_data=planning_data)

@app.route('/api/update_planning', methods=['POST'])
def update_planning():
    """Update planning sheet via API"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        updates = request.get_json()
        en_writer.en_writer.update_planning_sheet(updates)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/analyze_content', methods=['POST'])
def analyze_content():
    """Analyze content using LLM"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        content = data.get('content', '')
        analysis = en_writer.analyze_content_with_llm(content)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'status': 'error', 'message': 'Project name is required'})
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Not authenticated'})
        
        project_id = db.create_project(user_id, name, description)
        if project_id:
            return jsonify({'status': 'success', 'project_id': project_id})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to create project'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Update a project"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        status = data.get('status')
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Not authenticated'})
        
        success = db.update_project(project_id, name, description, status)
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update project'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Delete a project"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Not authenticated'})
        
        success = db.delete_project(project_id)
        if success:
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete project'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/backup')
def backup():
    """Create backup of current state"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        backup_data = {
            'sections': en_writer.en_writer.sections,
            'planning_data': en_writer.en_writer.planning_data,
            'activity_log': en_writer.en_writer.activity_log,
            'timestamp': timestamp
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        flash(f'Backup created: {backup_file}', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Backup failed: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/project/<int:project_id>')
def project_workspace(project_id):
    """Project workspace - main view for working on a specific project"""
    if not en_writer:
        initialize_en_writer()
    
    # Get current user ID from session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_page'))
    
    # Get project details
    project = db.get_project_by_id(project_id) if hasattr(db, 'get_project_by_id') else None
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Get project-specific EN files
    project_en_files = db.get_project_en_files(project_id) if hasattr(db, 'get_project_en_files') else []
    
    # Get project planning data
    project_planning = db.get_project_planning(project_id) if hasattr(db, 'get_project_planning') else {}
    
    # Get project statistics
    project_stats = db.get_project_stats(project_id) if hasattr(db, 'get_project_stats') else {}
    
    return render_template('project_workspace.html', 
                         project=project,
                         project_en_files=project_en_files,
                         project_planning=project_planning,
                         project_stats=project_stats)

@app.route('/project/<int:project_id>/sections')
def project_sections(project_id):
    """Project-specific sections view"""
    if not en_writer:
        initialize_en_writer()
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_page'))
    
    project = db.get_project_by_id(project_id) if hasattr(db, 'get_project_by_id') else None
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Get project-specific sections
    project_sections = db.get_project_en_files(project_id) if hasattr(db, 'get_project_en_files') else []
    
    return render_template('project_sections.html', 
                         project=project,
                         sections=project_sections)

@app.route('/project/<int:project_id>/analyze')
def project_analyze(project_id):
    """Project-specific content analysis"""
    if not en_writer:
        initialize_en_writer()
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_page'))
    
    project = db.get_project_by_id(project_id) if hasattr(db, 'get_project_by_id') else None
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Get project sections for analysis
    project_sections = db.get_project_en_files(project_id) if hasattr(db, 'get_project_en_files') else []
    
    # Run gap analysis on project sections
    gap_analysis = en_writer.en_writer.analyze_sections_for_gaps(project_sections)
    questions = en_writer.generate_contextual_questions(gap_analysis)
    
    return render_template('project_analyze.html', 
                         project=project,
                         gap_analysis=gap_analysis, 
                         questions=questions)

@app.route('/project/<int:project_id>/planning')
def project_planning(project_id):
    """Project-specific planning sheet"""
    if not en_writer:
        initialize_en_writer()
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth_page'))
    
    project = db.get_project_by_id(project_id) if hasattr(db, 'get_project_by_id') else None
    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Get project planning data
    project_planning = db.get_project_planning(project_id) if hasattr(db, 'get_project_planning') else {}
    
    return render_template('project_planning.html', 
                         project=project,
                         planning_data=project_planning)

@app.route('/settings')
def settings():
    """Settings page"""
    if not en_writer:
        initialize_en_writer()
    
    available_models = en_writer.openrouter.get_available_models()
    current_model = en_writer.openrouter.get_current_model()
    
    # Convert to list of tuples (index, model) for template
    available_models_with_index = list(enumerate(available_models))
    
    return render_template('settings.html', 
                         available_models=available_models_with_index,
                         current_model=current_model)

@app.route('/api/switch_model', methods=['POST'])
def switch_model():
    """Switch OpenRouter model"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        model_index = data.get('model_index', 0)
        success = en_writer.openrouter.switch_model(model_index)
        
        if success:
            return jsonify({'status': 'success', 
                          'current_model': en_writer.openrouter.get_current_model()})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid model index'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """Chat with AI assistant for project-specific help"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        project_id = data.get('project_id')
        
        if not message:
            return jsonify({'status': 'error', 'message': 'Message is required'})
        
        # Get current user ID from session (allow unauthenticated for now)
        user_id = session.get('user_id', 1)  # Default to user 1 for testing
        
        # Get project data for context
        project_context = ""
        project_sections = []
        
        if project_id:
            project = db.get_project_by_id(project_id) if hasattr(db, 'get_project_by_id') else None
            if project:
                project_context = f"Project: {project.get('name', 'Unknown')} - {project.get('description', 'No description')}"
                project_sections = db.get_project_en_files(project_id) if hasattr(db, 'get_project_en_files') else []
        
        # Get user's EN files for context
        user_en_files = db.get_en_files(user_id) if db else []
        
        # Build context for the AI
        context_info = f"""
Project Context: {project_context}

Current Project Sections ({len(project_sections)} total):
"""
        for section in project_sections[:10]:  # Limit to first 10 sections
            context_info += f"- {section.get('filename', 'Unknown')}: {section.get('title', 'No title')}\n"
        
        if len(project_sections) > 10:
            context_info += f"... and {len(project_sections) - 10} more sections\n"
        
        context_info += f"""
User's Total EN Files: {len(user_en_files)}

User Message: {message}
"""
        
        # Create a conversational prompt
        prompt = f"""You are an AI assistant helping with an engineering notebook project. Be conversational and helpful.

{context_info}

The user asked: "{message}"

Respond naturally to the user's message. If they ask about sections, provide specific information about their current sections. If they want to create something new, offer to help. Be friendly and encouraging.

Keep your response concise but helpful. If they ask "how many sections do I have", tell them the exact number and list a few examples. Do NOT provide template content unless specifically asked to create a new section."""

        # Generate AI response using OpenRouter
        ai_response = en_writer.openrouter.generate_text(prompt, max_tokens=300)
        
        # Log the interaction
        if db:
            db.log_llm_interaction(
                user_id=user_id,
                model_name=en_writer.openrouter.get_current_model(),
                prompt=prompt,
                response=ai_response,
                tokens_used=len(prompt.split()) + len(ai_response.split()),
                cost=0.0
            )
        
        return jsonify({
            'status': 'success',
            'response': ai_response,
            'project_sections_count': len(project_sections),
            'total_en_files': len(user_en_files)
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    # Create necessary directories
    Path("en_files").mkdir(exist_ok=True)
    Path("backups").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    # Initialize EN Writer
    initialize_en_writer()
    
    # Get port from environment variable (for Render)
    port = int(os.environ.get('PORT', 5001))
    
    # Run the app with proper auto-reload configuration
    import os
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=True, use_debugger=True, 
            extra_files=[template_dir])
