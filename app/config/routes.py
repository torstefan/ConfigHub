from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app.config import bp
from app.config.git import sync_with_repo
from app.config.template import get_node_structure, get_template_variables, update_variable_value, generate_config
import os
import yaml
import re
from datetime import datetime
from werkzeug.utils import secure_filename
from urllib.parse import unquote

def validate_node_path(node_path):
    """Validate node path and return components if valid."""
    if not node_path:
        raise ValueError("Node path is required")
    
    # URL decode the path if needed
    try:
        node_path = unquote(node_path)
    except Exception as e:
        current_app.logger.error(f"Failed to decode node path: {str(e)}")
        raise ValueError("Invalid node path encoding")
    
    if '..' in node_path:
        raise ValueError("Invalid node path")
    
    parts = node_path.split('/')
    if len(parts) != 3:  # node_family/node_class/node_name
        raise ValueError("Invalid node path structure")
    
    return parts

def validate_template_name(template_name, allow_empty=False):
    """Validate template name for security."""
    if not template_name:
        if allow_empty:
            return ''
        raise ValueError("Template name is required")
    
    # Only allow alphanumeric chars, underscore, and hyphen
    if not re.match(r'^[\w-]+$', template_name):
        raise ValueError("Invalid template name")
    
    return secure_filename(template_name)

def validate_yaml_content(content):
    """Validate YAML content structure."""
    try:
        data = yaml.safe_load(content)
        if not isinstance(data, dict):
            raise ValueError("YAML root must be a dictionary")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML content: {str(e)}")

def get_relative_path(full_path):
    """Convert full system path to relative path for display."""
    root_folder = current_app.config['ROOT_FOLDER']
    return os.path.relpath(full_path, root_folder)

@bp.route('/')
@login_required
def index():
    # Get the current path from localStorage or use default values
    current_path = {
        'family': None,
        'class': None,
        'node': None,
        'templates': []
    }
    
    return render_template('config/index.html', current_path=current_path)

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
        node_family, node_class, node_name = validate_node_path(node_path)
        
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
                    if re.match(r'^[\w-]+$', template_name):  # Validate template name
                        yml_file = os.path.join(vars_dir, f"{template_name}.yml")
                        templates.append({
                            'name': template_name,
                            'has_vars': os.path.exists(yml_file),
                            'warning': None if os.path.exists(yml_file) else "No matching YAML file"
                        })
        
        return jsonify(templates)
    except ValueError as e:
        current_app.logger.warning(f"Invalid request for templates: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'error': "Failed to get templates"}), 500

@bp.route('/variables/<path:node_path>/<template_name>', methods=['GET', 'POST'])
@login_required
def get_variables(node_path, template_name):
    """Get or update variables for a template"""
    try:
        node_family, node_class, node_name = validate_node_path(node_path)
        template_name = validate_template_name(template_name, allow_empty=False)
        
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'variable' not in data or 'value' not in data:
                raise ValueError("Invalid request data")
            
            update_variable_value(node_path, template_name, data['variable'], data['value'])
            return jsonify({'status': 'success'})
        else:
            variables = get_template_variables(node_path, template_name)
            return jsonify(variables)
    except ValueError as e:
        current_app.logger.warning(f"Invalid request for variables: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error handling variables: {str(e)}")
        return jsonify({'error': "Failed to handle variables"}), 500

@bp.route('/preview/<path:node_path>')
@login_required
def get_preview(node_path):
    """Get the configuration preview"""
    try:
        node_family, node_class, node_name = validate_node_path(node_path)
        
        preview_dir = os.path.join(current_app.config['ROOT_FOLDER'],
                                 'nodes', node_family, node_class, node_name, 'preview')
        if not os.path.exists(preview_dir):
            os.makedirs(preview_dir, mode=0o755)
        
        preview_file = os.path.join(preview_dir, 'generated-config')
        
        # Get selected templates from query parameters
        templates = request.args.getlist('template')
        if not templates:
            return jsonify({'content': 'No templates selected'})
        
        # Validate template names
        templates = [validate_template_name(t, allow_empty=False) for t in templates]
        
        # Clear and create the preview file with proper permissions
        with open(preview_file, 'w') as f:
            f.write('')
        os.chmod(preview_file, 0o644)
        
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
    except ValueError as e:
        current_app.logger.warning(f"Invalid request for preview: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error getting preview: {str(e)}")
        return jsonify({'error': "Failed to generate preview"}), 500

@bp.route('/manage/<path:node_path>', methods=['GET'])
@login_required
def manage_template(node_path):
    """Manage template and variables for a node."""
    try:
        current_app.logger.info(f"Managing template for node path: {node_path}")
        
        try:
            node_family, node_class, node_name = validate_node_path(node_path)
            current_app.logger.debug(f"Validated node path components: family={node_family}, class={node_class}, name={node_name}")
        except ValueError as e:
            current_app.logger.error(f"Invalid node path: {str(e)}")
            return jsonify({'error': f'Invalid node path: {str(e)}'}), 400
        
        # Check if we're creating a new template or editing existing
        template_name = request.args.get('template')
        if template_name:
            template_name = unquote(template_name)
        is_new_template = request.args.get('new', 'false').lower() == 'true'
        current_app.logger.debug(f"Template request params: name={template_name}, is_new={is_new_template}")
        
        try:
            template_name = validate_template_name(template_name, allow_empty=is_new_template)
            current_app.logger.debug(f"Validated template name: {template_name}")
        except ValueError as e:
            current_app.logger.error(f"Invalid template name: {str(e)}")
            return jsonify({'error': f'Invalid template name: {str(e)}'}), 400
        
        # Create paths
        template_path = os.path.join(current_app.config['ROOT_FOLDER'],
                                   'template', node_family, node_class,
                                   f"{template_name}.j2" if template_name else '')
        variables_path = os.path.join(current_app.config['ROOT_FOLDER'],
                                    'nodes', node_family, node_class, node_name,
                                    'vars', f"{template_name}.yml" if template_name else '')
        
        current_app.logger.debug(f"Template path: {template_path}")
        current_app.logger.debug(f"Variables path: {variables_path}")
        
        # Initialize content
        template_content = ''
        variables_content = ''
        
        # Try to read existing files if not creating new template
        if not is_new_template and template_name:
            try:
                if os.path.exists(template_path):
                    with open(template_path, 'r') as f:
                        template_content = f.read()
                        current_app.logger.debug("Successfully read template file")
                else:
                    current_app.logger.debug(f"Template file does not exist: {template_path}")
                
                if os.path.exists(variables_path):
                    with open(variables_path, 'r') as f:
                        variables_content = f.read()
                        current_app.logger.debug("Successfully read variables file")
                else:
                    current_app.logger.debug(f"Variables file does not exist: {variables_path}")
            except Exception as e:
                current_app.logger.warning(f"Failed to read template files: {str(e)}", exc_info=True)
                # Continue with empty content if files can't be read
        
        # Ensure parent directories exist
        try:
            os.makedirs(os.path.dirname(template_path), mode=0o755, exist_ok=True)
            os.makedirs(os.path.dirname(variables_path), mode=0o755, exist_ok=True)
            current_app.logger.debug("Created necessary directories")
        except Exception as e:
            current_app.logger.error(f"Failed to create directories: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to create necessary directories'}), 500
        
        # Convert full paths to relative paths for display
        try:
            template_display_path = get_relative_path(template_path)
            variables_display_path = get_relative_path(variables_path)
            current_app.logger.debug(f"Display paths - template: {template_display_path}, variables: {variables_display_path}")
        except Exception as e:
            current_app.logger.error(f"Failed to convert paths: {str(e)}", exc_info=True)
            return jsonify({'error': 'Failed to process file paths'}), 500
        
        current_app.logger.info("Successfully prepared template management page")
        return render_template('config/manage.html',
                             node_path=node_path,
                             template_name=template_name,
                             template_path=template_display_path,
                             variables_path=variables_display_path,
                             template_content=template_content,
                             variables_content=variables_content,
                             is_new_template=is_new_template)
    except Exception as e:
        current_app.logger.error(f"Error in template management: {str(e)}", exc_info=True)
        return jsonify({'error': "Failed to manage template"}), 500

@bp.route('/manage/<path:node_path>', methods=['POST'])
@login_required
def save_template(node_path):
    """Save template and variables for a node."""
    try:
        node_family, node_class, node_name = validate_node_path(node_path)
        
        data = request.get_json()
        if not data:
            raise ValueError("No data provided")
        
        template_name = data.get('template_name') or request.args.get('template')
        if template_name:
            template_name = unquote(template_name)
        template_content = data.get('template_content')
        variables_content = data.get('variables_content')
        
        if not template_name:
            raise ValueError("Template name not provided")
        
        template_name = validate_template_name(template_name, allow_empty=False)
        
        # Validate YAML content
        if variables_content:
            validate_yaml_content(variables_content)
        
        # Create paths
        template_path = os.path.join(current_app.config['ROOT_FOLDER'],
                                   'template', node_family, node_class,
                                   f"{template_name}.j2")
        variables_path = os.path.join(current_app.config['ROOT_FOLDER'],
                                    'nodes', node_family, node_class, node_name,
                                    'vars', f"{template_name}.yml")
        
        # Ensure directories exist with proper permissions
        os.makedirs(os.path.dirname(template_path), mode=0o755, exist_ok=True)
        os.makedirs(os.path.dirname(variables_path), mode=0o755, exist_ok=True)
        
        # Save files with proper permissions
        with open(template_path, 'w') as f:
            f.write(template_content)
        os.chmod(template_path, 0o644)
        
        with open(variables_path, 'w') as f:
            f.write(variables_content)
        os.chmod(variables_path, 0o644)
        
        current_app.logger.info(f"Template saved successfully: {template_name}")
        return jsonify({'message': 'Changes saved successfully'})
    except ValueError as e:
        current_app.logger.warning(f"Invalid save template request: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Failed to save template: {str(e)}")
        return jsonify({'error': "Failed to save changes"}), 500 