"""
Flask Web Interface for Agentic Engineering Notebook Writer
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
import json
from datetime import datetime
from pathlib import Path
import logging

from en_writer import ENWriter
from openrouter_backend import OpenRouterENWriter
from cloud_database import CloudNotebookerDB
from auth import AuthManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Global instances
en_writer = None
db = None
auth = None

def initialize_en_writer():
    """Initialize the EN Writer with default directory"""
    global en_writer, db, auth
    base_dir = Path("en_files")
    base_dir.mkdir(exist_ok=True)
    
    # Initialize cloud database (PostgreSQL on Render, SQLite locally)
    db = CloudNotebookerDB()
    auth = AuthManager(db)
    en_writer = OpenRouterENWriter(str(base_dir))

@app.route('/')
def index():
    """Main dashboard"""
    if not en_writer:
        initialize_en_writer()
    
    status = en_writer.en_writer.get_status_summary()
    return render_template('index.html', status=status)

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

@app.route('/settings')
def settings():
    """Settings page"""
    if not en_writer:
        initialize_en_writer()
    
    available_models = en_writer.openrouter.get_available_models()
    current_model = en_writer.openrouter.get_current_model()
    
    return render_template('settings.html', 
                         available_models=available_models,
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

if __name__ == '__main__':
    # Create necessary directories
    Path("en_files").mkdir(exist_ok=True)
    Path("backups").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    Path("templates").mkdir(exist_ok=True)
    
    # Initialize EN Writer
    initialize_en_writer()
    
    # Get port from environment variable (for Render)
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(debug=False, host='0.0.0.0', port=port)
