from flask import render_template, current_app, jsonify, request, url_for
from flask_login import login_required
import os
from datetime import datetime
import yaml
import subprocess
import shutil
import logging

from app.deploy import bp

@bp.route('/prepare/<path:node_path>', methods=['GET'])
@login_required
def prepare(node_path):
    try:
        logging.info("="*50)
        logging.info(f"Prepare route called")
        logging.info(f"Request path: {request.path}")
        logging.info(f"Request full path: {request.full_path}")
        logging.info(f"Request args: {request.args}")
        logging.info(f"Node path: {node_path}")
        logging.info(f"URL for this route: {url_for('deploy.prepare', node_path=node_path)}")
        logging.info("="*50)
        
        # Get selected templates from query parameters
        templates = request.args.getlist('template')
        logging.info(f"Selected templates: {templates}")
        
        if not templates:
            return render_template('deploy/prepare.html', 
                                error="No templates selected. Please select at least one template before deploying.")
        
        # Get the root folder from config
        root_folder = current_app.config.get('ROOT_FOLDER', '')
        logging.info(f"Root folder: {root_folder}")
        
        if not root_folder:
            return render_template('deploy/prepare.html', 
                                error="Configuration error: ROOT_FOLDER not set.")
        
        # Construct the full path to the preview directory
        preview_dir = os.path.join(root_folder, node_path, 'preview')
        logging.info(f"Preview directory: {preview_dir}")
        
        if not os.path.exists(preview_dir):
            return render_template('deploy/prepare.html', 
                                error=f"Preview directory not found: {preview_dir}")
        
        # Get the latest configuration file
        config_content = None
        if os.path.exists(preview_dir):
            files = [f for f in os.listdir(preview_dir) if f.endswith('.yaml')]
            if files:
                latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(preview_dir, x)))
                with open(os.path.join(preview_dir, latest_file), 'r') as f:
                    config_content = f.read()
        
        # Gather variables for each template
        variables = {}
        for template in templates:
            template_path = os.path.join(root_folder, node_path, 'templates', f"{template}.yaml")
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    template_data = yaml.safe_load(f)
                    if template_data and 'variables' in template_data:
                        variables[template] = template_data['variables']
        
        logging.info(f"Rendering template with node_path: {node_path}, templates: {templates}")
        return render_template('deploy/prepare.html',
                            node_path=node_path,
                            templates=templates,
                            variables=variables,
                            config_file=config_content)
                            
    except Exception as e:
        logging.error(f"Error in prepare route: {str(e)}")
        return render_template('deploy/prepare.html', 
                            error=f"An error occurred: {str(e)}")

@bp.route('/api/verify', methods=['POST'])
@login_required
def verify():
    try:
        data = request.get_json()
        node_path = data.get('node_path')
        
        if not node_path:
            return jsonify({'success': False, 'output': 'No node path provided'}), 400
        
        root_folder = current_app.config.get('ROOT_FOLDER', '')
        if not root_folder:
            return jsonify({'success': False, 'output': 'ROOT_FOLDER not configured'}), 500
        
        # Construct the path to the verification script
        verify_script = os.path.join(root_folder, node_path, 'verify.py')
        
        if not os.path.exists(verify_script):
            return jsonify({'success': False, 'output': 'Verification script not found'}), 404
        
        # Run the verification script
        result = subprocess.run(['python3', verify_script], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'output': result.stdout})
        else:
            return jsonify({'success': False, 'output': result.stderr})
            
    except Exception as e:
        logging.error(f"Error in verify route: {str(e)}")
        return jsonify({'success': False, 'output': str(e)}), 500

@bp.route('/api/deploy', methods=['POST'])
@login_required
def deploy():
    try:
        data = request.get_json()
        node_path = data.get('node_path')
        
        if not node_path:
            return jsonify({'success': False, 'output': 'No node path provided'}), 400
        
        root_folder = current_app.config.get('ROOT_FOLDER', '')
        if not root_folder:
            return jsonify({'success': False, 'output': 'ROOT_FOLDER not configured'}), 500
        
        # Construct the path to the deployment script
        deploy_script = os.path.join(root_folder, node_path, 'deploy.py')
        
        if not os.path.exists(deploy_script):
            return jsonify({'success': False, 'output': 'Deployment script not found'}), 404
        
        # Run the deployment script
        result = subprocess.run(['python3', deploy_script], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'output': result.stdout})
        else:
            return jsonify({'success': False, 'output': result.stderr})
            
    except Exception as e:
        logging.error(f"Error in deploy route: {str(e)}")
        return jsonify({'success': False, 'output': str(e)}), 500 