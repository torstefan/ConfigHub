from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app.config import bp
from app.config.git import sync_with_repo
from app.config.template import get_node_structure, get_template_variables, update_variable_value, generate_config
import os
import yaml
from datetime import datetime

@bp.route('/')
@login_required
def index():
    """Main configuration page"""
    return render_template('config/index.html')

@bp.route('/sync', methods=['POST'])
@login_required
def sync_repo():
    """Sync with git repository"""
    try:
        message = sync_with_repo()
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        current_app.logger.error(f"Git sync error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/structure')
@login_required
def get_structure():
    """Get the node structure"""
    try:
        structure = get_node_structure()
        return jsonify(structure)
    except Exception as e:
        current_app.logger.error(f"Error getting node structure: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/templates/<path:node_path>')
@login_required
def get_templates(node_path):
    """Get available templates for a node"""
    try:
        # Split the path into components
        parts = node_path.split('/')
        if len(parts) != 3:  # node_family/node_class/node_name
            raise ValueError("Invalid node path")
        
        node_family, node_class, node_name = parts
        template_dir = os.path.join(current_app.config['ROOT_FOLDER'], 
                                  'template', node_family, node_class)
        vars_dir = os.path.join(current_app.config['ROOT_FOLDER'],
                              'nodes', node_family, node_class, node_name, 'vars')
        
        # Get all .j2 files from template directory
        templates = []
        if os.path.exists(template_dir):
            for file in os.listdir(template_dir):
                if file.endswith('.j2'):
                    template_name = file[:-3]  # Remove .j2 extension
                    yml_file = os.path.join(vars_dir, f"{template_name}.yml")
                    templates.append({
                        'name': template_name,
                        'has_vars': os.path.exists(yml_file),
                        'warning': None if os.path.exists(yml_file) else "No matching YAML file"
                    })
        
        return jsonify(templates)
    except Exception as e:
        current_app.logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/variables/<path:node_path>/<template_name>', methods=['GET', 'POST'])
@login_required
def get_variables(node_path, template_name):
    """Get or update variables for a template"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            update_variable_value(node_path, template_name, data['variable'], data['value'])
            return jsonify({'status': 'success'})
        else:
            variables = get_template_variables(node_path, template_name)
            return jsonify(variables)
    except Exception as e:
        current_app.logger.error(f"Error handling variables: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/preview/<path:node_path>')
@login_required
def get_preview(node_path):
    """Get the configuration preview"""
    try:
        preview_dir = os.path.join(current_app.config['ROOT_FOLDER'],
                                 'nodes', *node_path.split('/'), 'preview')
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir)
        
        preview_file = os.path.join(preview_dir, 'generated-config')
        
        # Clear the preview file before generating new content
        with open(preview_file, 'w') as f:
            f.write('')
            
        # Get selected templates from query parameters
        templates = request.args.getlist('template')
        
        # Generate configuration for each template
        for template in templates:
            variables = get_template_variables(node_path, template)
            generate_config(node_path, template, variables)
        
        # Read and return the generated configuration
        if os.path.exists(preview_file):
            with open(preview_file, 'r') as f:
                content = f.read()
            return jsonify({'content': content})
        else:
            return jsonify({'content': 'No preview available'})
    except Exception as e:
        current_app.logger.error(f"Error getting preview: {str(e)}")
        return jsonify({'error': str(e)}), 500 