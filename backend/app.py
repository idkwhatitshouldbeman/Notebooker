"""
Flask Web Interface for Agentic Engineering Notebook Writer
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response, send_file
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path
import logging
import hashlib
import secrets

from en_writer import ENWriter
from database_manager import SmartNotebookerDB
from auth import AuthManager
from ai_service_client import initialize_ai_service, get_ai_client, get_task_manager

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

# Configure CORS - More permissive for immediate testing
CORS(app, 
     origins=[
         "https://notebooker.netlify.app",
         "http://localhost:8080",
         "http://localhost:3000",
         "http://127.0.0.1:8080",
         "http://127.0.0.1:3000",
         "https://*.netlify.app"  # Allow all Netlify subdomains
     ],
     allow_headers=["Content-Type", "X-API-Key", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

# API Key for authentication
API_KEY = os.environ.get('API_KEY', 'notebooker-api-key-2024')

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
    
    # Additional CORS headers for immediate fix
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    
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
    en_writer = ENWriter(str(base_dir))
    
    # Initialize AI service
    ai_service_url = os.environ.get('AI_SERVICE_URL', 'https://your-render-app-name.onrender.com')
    ai_api_key = os.environ.get('AI_API_KEY')
    initialize_ai_service(ai_service_url, ai_api_key)

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        # Check for session token in localStorage (handled by JavaScript)
        # For now, we'll allow access and handle auth in the frontend
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_api_key(f):
    """Decorator to require API key authentication"""
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            logger.warning(f"Invalid API key attempt from {request.remote_addr}")
            return jsonify({'success': False, 'error': 'Invalid API key'}), 401
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
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({'success': False, 'error': 'Name, email, and password are required'})
        
        # Validate Gmail address
        if not email.endswith('@gmail.com'):
            return jsonify({'success': False, 'error': 'Only Gmail addresses are accepted'})
        
        # Use email as username
        username = email
        
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

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "NTBK_AI Flask API", "timestamp": datetime.now().isoformat()}, 200

@app.route('/')
def index():
    """Main dashboard - redirect to auth if not logged in"""
    return redirect(url_for('auth_page'))

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
    
    status = en_writer.get_status_summary()
    return render_template('dashboard.html', status=status, projects=projects)

@app.route('/sections')
def sections():
    """View all sections"""
    if not en_writer:
        initialize_en_writer()
    
    sections = en_writer.sections
    return render_template('sections.html', sections=sections)

@app.route('/analyze')
def analyze():
    """Analyze sections for gaps"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        # Load sections if not already loaded
        if not en_writer.sections:
            en_writer.load_en_sections("en_files")
        
        gap_analysis = en_writer.analyze_sections_for_gaps(en_writer.sections)
        questions = en_writer.generate_user_questions(gap_analysis)
        
        return render_template('analyze.html', 
                             gap_analysis=gap_analysis, 
                             questions=questions)
    except Exception as e:
        logger.error(f"Error in analyze route: {e}")
        return f"Error: {str(e)}", 500

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
        draft_content = en_writer.draft_new_entry(section_name, user_inputs)
        
        # Save the draft
        en_writer.sections[section_name] = draft_content
        en_writer.save_en_files({section_name: draft_content})
        
        # Log activity
        en_writer.log_agent_activity(
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
    
    if section_name not in en_writer.sections:
        flash(f'Section {section_name} not found', 'error')
        return redirect(url_for('sections'))
    
    if request.method == 'POST':
        improvement_focus = request.form.get('improvement_focus', 'clarity and technical rigor')
        original_content = en_writer.sections[section_name]
        
        # Rewrite using LLM
        improved_content = en_writer.rewrite_entry(original_content)
        
        # Save the improved version
        en_writer.sections[section_name] = improved_content
        en_writer.save_en_files({section_name: improved_content})
        
        # Log activity
        en_writer.log_agent_activity(
            "activity_log.json",
            {
                'action': 'section_rewritten',
                'section': section_name,
                'improvement_focus': improvement_focus
            }
        )
        
        flash(f'Section {section_name} has been improved', 'success')
        return redirect(url_for('sections'))
    
    section_content = en_writer.sections[section_name]
    return render_template('rewrite.html', 
                         section_name=section_name, 
                         section_content=section_content)

@app.route('/section/<section_name>')
def view_section(section_name):
    """View specific section"""
    if not en_writer:
        initialize_en_writer()
    
    if section_name not in en_writer.sections:
        flash(f'Section {section_name} not found', 'error')
        return redirect(url_for('sections'))
    
    section_content = en_writer.sections[section_name]
    return render_template('view_section.html', 
                         section_name=section_name, 
                         section_content=section_content)

@app.route('/planning')
def planning():
    """View planning sheet"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        planning_data = en_writer.planning_data
        return render_template('planning.html', planning_data=planning_data)
    except Exception as e:
        logger.error(f"Error in planning route: {e}")
        return f"Error: {str(e)}", 500

@app.route('/api/update_planning', methods=['POST'])
def update_planning():
    """Update planning sheet via API"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        updates = request.get_json()
        en_writer.update_planning_sheet(updates)
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
        # Simple content analysis - could be enhanced with actual LLM
        analysis = {
            'status': 'success',
            'analysis': f'Content length: {len(content)} characters. This is a basic analysis.',
            'suggestions': ['Add more technical details', 'Include diagrams', 'Provide examples']
        }
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    """Create project page and handle form submission"""
    if request.method == 'GET':
        # Show create project form
        return render_template('create_project.html')
    
    elif request.method == 'POST':
        # Handle form submission
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Project name is required', 'error')
                return render_template('create_project.html')
            
            user_id = session.get('user_id')
            if not user_id:
                flash('Please log in to create a project', 'error')
                return redirect(url_for('auth_page'))
            
            project_id = db.create_project(user_id, name, description)
            if project_id:
                flash(f'Project "{name}" created successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Failed to create project', 'error')
                return render_template('create_project.html')
        
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            flash(f'Error creating project: {str(e)}', 'error')
            return render_template('create_project.html')

@app.route('/api/projects', methods=['POST'])
def create_project_api():
    """Create a new project via API"""
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
    """Backup page"""
    return render_template('backup.html')

@app.route('/backup/create', methods=['POST'])
def create_backup():
    """Create backup of current state"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.json"
        
        backup_data = {
            'sections': en_writer.sections,
            'planning_data': en_writer.planning_data,
            'activity_log': en_writer.activity_log,
            'timestamp': timestamp
        }
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        flash(f'Backup created: {backup_file}', 'success')
        return redirect(url_for('backup'))
    
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
    gap_analysis = en_writer.analyze_sections_for_gaps(project_sections)
    questions = en_writer.generate_user_questions(gap_analysis)
    
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
    
    # Simple settings without AI model selection
    return render_template('settings_simple.html')

@app.route('/api/switch_model', methods=['POST'])
def switch_model():
    """Switch AI model (placeholder for n8n integration)"""
    if not en_writer:
        initialize_en_writer()
    
    try:
        data = request.get_json()
        model_index = data.get('model_index', 0)
        
        # Placeholder for n8n model switching
        models = [
            "deepseek/deepseek-chat-v3.1:free",
            "gpt-oss-20b:free", 
            "sonoma-dusk-alpha:free",
            "kimi-k2:free",
            "gemma-3n-2b:free",
            "mistral-small-3.2-24b:free"
        ]
        
        if 0 <= model_index < len(models):
            return jsonify({
                'status': 'success', 
                'current_model': models[model_index],
                'message': 'Model switching will be available when n8n is deployed'
            })
        else:
            return jsonify({'status': 'error', 'message': 'Invalid model index'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# AI Service Integration
AI_SERVICE_URL = os.environ.get('AI_SERVICE_URL', 'https://your-render-app-name.onrender.com')

@app.route('/api/ai/status')
def ai_status():
    """Check AI service connection status"""
    try:
        import requests
        response = requests.get(f"{AI_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({'status': 'connected', 'url': AI_SERVICE_URL})
        else:
            return jsonify({'status': 'error', 'message': 'AI service not responding'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/ai/webhook/<workflow_id>', methods=['POST'])
def ai_webhook(workflow_id):
    """Send data to AI service workflow"""
    try:
        import requests
        data = request.get_json()
        webhook_url = f"{AI_SERVICE_URL}/webhook/{workflow_id}"
        response = requests.post(webhook_url, json=data, timeout=30)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# AI Service Task Management Endpoints
@app.route('/api/ai/tasks', methods=['POST'])
def create_ai_task():
    """Create a new AI task"""
    try:
        data = request.get_json()
        prompt_context = data.get('prompt_context', '')
        agent_config = data.get('agent_config', {})
        external_tool_endpoints = data.get('external_tool_endpoints', {})
        
        if not prompt_context:
            return jsonify({'error': 'prompt_context is required'}), 400
        
        task_manager = get_task_manager()
        task_id = task_manager.start_task(prompt_context, agent_config, external_tool_endpoints)
        
        return jsonify({
            'task_id': task_id,
            'status': 'created',
            'message': 'Task created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating AI task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/tasks/<task_id>', methods=['GET'])
def get_ai_task_status(task_id):
    """Get AI task status"""
    try:
        task_manager = get_task_manager()
        response = task_manager.update_task_status(task_id)
        
        return jsonify({
            'task_id': response.task_id,
            'status': response.status,
            'agent_reply': response.agent_reply,
            'next_step': response.next_step,
            'logs': response.logs,
            'error': response.error
        })
        
    except Exception as e:
        logger.error(f"Error getting AI task status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/tasks/<task_id>', methods=['DELETE'])
def cancel_ai_task(task_id):
    """Cancel an AI task"""
    try:
        task_manager = get_task_manager()
        success = task_manager.cancel_task(task_id)
        
        return jsonify({
            'success': success,
            'message': 'Task cancelled' if success else 'Failed to cancel task'
        })
        
    except Exception as e:
        logger.error(f"Error cancelling AI task: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/tasks', methods=['GET'])
def list_ai_tasks():
    """List all AI tasks"""
    try:
        task_manager = get_task_manager()
        active_tasks = task_manager.get_active_tasks()
        task_history = task_manager.get_task_history(limit=20)
        
        return jsonify({
            'active_tasks': active_tasks,
            'task_history': task_history
        })
        
    except Exception as e:
        logger.error(f"Error listing AI tasks: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai/health', methods=['GET'])
def ai_service_health():
    """Check AI service health"""
    try:
        ai_client = get_ai_client()
        is_healthy = ai_client.health_check()
        
        return jsonify({
            'healthy': is_healthy,
            'service_url': ai_client.base_url,
            'message': 'AI service is available' if is_healthy else 'AI service is unavailable'
        })
        
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}")
        return jsonify({'error': str(e)}), 500

# New API endpoints for frontend integration
@app.route('/api/ai/chat', methods=['POST'])
@require_api_key
def ai_chat():
    """AI chat endpoint for conversational assistance"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        message = data.get('message', '')
        project_id = data.get('projectId', '')
        context = data.get('context', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        logger.info(f"AI Chat request - Project: {project_id}, Message: {message[:100]}...")
        
        # Create prompt context for AI service
        prompt_context = f"""
        As an engineering notebook assistant, help with the following request:
        
        User Message: {message}
        Project Context: {context}
        Project ID: {project_id}
        
        Provide helpful, technical assistance for engineering documentation and project management.
        Be specific and actionable in your response.
        """
        
        # Use AI service to generate response
        ai_client = get_ai_client()
        task_manager = get_task_manager()
        
        from ai_service_client import AgentConfig
        agent_config = AgentConfig(
            model="flan-t5-small",
            temperature=0.7,
            max_tokens=1000
        )
        
        task_id = task_manager.start_task(prompt_context, agent_config)
        response = ai_client.poll_task_completion(task_id, max_wait_time=60)
        
        if response.status == "completed" and response.agent_reply:
            # Generate suggestions based on the response
            suggestions = [
                "Add technical details",
                "Include implementation steps", 
                "Document testing procedures",
                "Create project timeline"
            ]
            
            return jsonify({
                'success': True,
                'response': response.agent_reply,
                'suggestions': suggestions
            })
        else:
            return jsonify({
                'success': False,
                'error': f'AI service error: {response.error or "Unknown error"}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in AI chat: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/ai/analyze', methods=['POST'])
@require_api_key
def ai_analyze():
    """AI analysis endpoint for content analysis"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        content = data.get('content', '')
        project_id = data.get('projectId', '')
        
        if not content:
            return jsonify({'success': False, 'error': 'Content is required'}), 400
        
        logger.info(f"AI Analyze request - Project: {project_id}, Content length: {len(content)}")
        
        # Create prompt context for AI service
        prompt_context = f"""
        As an engineering documentation expert, analyze the following content and provide detailed feedback:
        
        Content to analyze:
        {content}
        
        Project ID: {project_id}
        
        Please provide:
        1. Technical accuracy assessment
        2. Completeness analysis
        3. Clarity and structure evaluation
        4. Specific improvement recommendations
        5. Missing elements identification
        
        Focus on engineering documentation standards and best practices.
        """
        
        # Use AI service for analysis
        ai_client = get_ai_client()
        task_manager = get_task_manager()
        
        from ai_service_client import AgentConfig
        agent_config = AgentConfig(
            model="flan-t5-small",
            temperature=0.5,
            max_tokens=1500
        )
        
        task_id = task_manager.start_task(prompt_context, agent_config)
        response = ai_client.poll_task_completion(task_id, max_wait_time=90)
        
        if response.status == "completed" and response.agent_reply:
            # Extract improvements from AI response
            improvements = [
                "Add technical specifications",
                "Include implementation details",
                "Document testing procedures",
                "Improve structure and organization"
            ]
            
            return jsonify({
                'success': True,
                'analysis': response.agent_reply,
                'improvements': improvements
            })
        else:
            return jsonify({
                'success': False,
                'error': f'AI service error: {response.error or "Unknown error"}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in AI analyze: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/ai/draft', methods=['POST'])
@require_api_key
def ai_draft():
    """AI draft endpoint for content generation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        topic = data.get('topic', '')
        project_id = data.get('projectId', '')
        style = data.get('style', 'technical')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        logger.info(f"AI Draft request - Project: {project_id}, Topic: {topic}, Style: {style}")
        
        # Create prompt context for AI service
        prompt_context = f"""
        As an engineering documentation expert, create a comprehensive draft for the following topic:
        
        Topic: {topic}
        Project ID: {project_id}
        Style: {style}
        
        Create a well-structured engineering document that includes:
        1. Clear introduction and overview
        2. Technical specifications and details
        3. Implementation methodology
        4. Testing and validation procedures
        5. Results and analysis framework
        6. Future improvements and recommendations
        
        Use professional engineering documentation standards and ensure technical accuracy.
        """
        
        # Use AI service for drafting
        ai_client = get_ai_client()
        task_manager = get_task_manager()
        
        from ai_service_client import AgentConfig
        agent_config = AgentConfig(
            model="flan-t5-small",
            temperature=0.7,
            max_tokens=2000
        )
        
        task_id = task_manager.start_task(prompt_context, agent_config)
        response = ai_client.poll_task_completion(task_id, max_wait_time=120)
        
        if response.status == "completed" and response.agent_reply:
            # Generate suggestions for the draft
            suggestions = [
                "Add technical diagrams",
                "Include code examples",
                "Document testing procedures",
                "Create implementation timeline"
            ]
            
            return jsonify({
                'success': True,
                'content': response.agent_reply,
                'suggestions': suggestions
            })
        else:
            return jsonify({
                'success': False,
                'error': f'AI service error: {response.error or "Unknown error"}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in AI draft: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/ai/plan', methods=['POST'])
@require_api_key
def ai_plan():
    """AI planning endpoint for project planning"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        project_id = data.get('projectId', '')
        goals = data.get('goals', [])
        
        if not goals:
            return jsonify({'success': False, 'error': 'Goals are required'}), 400
        
        logger.info(f"AI Plan request - Project: {project_id}, Goals: {goals}")
        
        # Create prompt context for AI service
        prompt_context = f"""
        As an engineering project management expert, create a comprehensive project plan based on the following goals:
        
        Project ID: {project_id}
        Goals: {', '.join(goals)}
        
        Create a detailed project plan that includes:
        1. Project overview and objectives
        2. Technical requirements and specifications
        3. Implementation phases and milestones
        4. Resource requirements and timeline
        5. Risk assessment and mitigation strategies
        6. Quality assurance and testing procedures
        7. Documentation and reporting requirements
        
        Focus on engineering project management best practices and ensure all goals are addressed.
        """
        
        # Use AI service for planning
        ai_client = get_ai_client()
        task_manager = get_task_manager()
        
        from ai_service_client import AgentConfig
        agent_config = AgentConfig(
            model="flan-t5-small",
            temperature=0.6,
            max_tokens=2500
        )
        
        task_id = task_manager.start_task(prompt_context, agent_config)
        response = ai_client.poll_task_completion(task_id, max_wait_time=120)
        
        if response.status == "completed" and response.agent_reply:
            # Extract sections from the plan
            sections = [
                "Project Overview",
                "Technical Requirements", 
                "Implementation Plan",
                "Testing Procedures",
                "Documentation Requirements"
            ]
            
            return jsonify({
                'success': True,
                'plan': response.agent_reply,
                'sections': sections
            })
        else:
            return jsonify({
                'success': False,
                'error': f'AI service error: {response.error or "Unknown error"}'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in AI plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    Path("en_files").mkdir(exist_ok=True)
    Path("backups").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    # Initialize EN Writer
    initialize_en_writer()
    
    # Get port from environment variable (for Render)
    port = int(os.environ.get('PORT', 5002))
    
    # Run the app with proper auto-reload configuration
    import os
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=True, use_debugger=True, 
            extra_files=[template_dir])
