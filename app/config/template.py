from flask import current_app
import os
import yaml
from jinja2 import Environment, FileSystemLoader
from typing import Dict, List, Any
from datetime import datetime

def get_node_structure() -> Dict[str, Any]:
    """
    Get the hierarchical structure of nodes from the root folder.
    Returns a dictionary representing the node structure.
    """
    root_folder = os.path.join(current_app.config['ROOT_FOLDER'], 'nodes')
    if not os.path.exists(root_folder):
        return {'families': []}

    structure = {'families': []}
    
    # Iterate through node families
    for family in sorted(os.listdir(root_folder)):
        family_path = os.path.join(root_folder, family)
        if not os.path.isdir(family_path):
            continue
            
        family_data = {'name': family, 'classes': []}
        
        # Iterate through node classes
        for node_class in sorted(os.listdir(family_path)):
            class_path = os.path.join(family_path, node_class)
            if not os.path.isdir(class_path):
                continue
                
            class_data = {'name': node_class, 'nodes': []}
            
            # Iterate through nodes
            for node in sorted(os.listdir(class_path)):
                node_path = os.path.join(class_path, node)
                if not os.path.isdir(node_path):
                    continue
                    
                class_data['nodes'].append({
                    'name': node,
                    'path': f"{family}/{node_class}/{node}"
                })
            
            if class_data['nodes']:  # Only add classes that have nodes
                family_data['classes'].append(class_data)
        
        if family_data['classes']:  # Only add families that have classes
            structure['families'].append(family_data)
    
    return structure

def get_template_variables(node_path: str, template_name: str) -> Dict[str, Any]:
    """
    Get variables for a specific template and node.
    Returns a dictionary of variables and their values.
    """
    # Split the path into components
    parts = node_path.split('/')
    if len(parts) != 3:
        raise ValueError("Invalid node path")
        
    node_family, node_class, node_name = parts
    
    # Get the YAML file path
    yaml_path = os.path.join(current_app.config['ROOT_FOLDER'],
                           'nodes', node_family, node_class, node_name,
                           'vars', f"{template_name}.yml")
    
    if not os.path.exists(yaml_path):
        return {}
    
    # Load and return variables
    with open(yaml_path, 'r') as f:
        return yaml.safe_load(f)

def update_variable_value(node_path: str, template_name: str, variable: str, value: Any) -> None:
    """
    Update a variable's value in the YAML file and regenerate the configuration.
    """
    # Split the path into components
    parts = node_path.split('/')
    if len(parts) != 3:
        raise ValueError("Invalid node path")
        
    node_family, node_class, node_name = parts
    
    # Get the YAML file path
    yaml_path = os.path.join(current_app.config['ROOT_FOLDER'],
                           'nodes', node_family, node_class, node_name,
                           'vars', f"{template_name}.yml")
    
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Variables file not found: {yaml_path}")
    
    # Load current variables
    with open(yaml_path, 'r') as f:
        variables = yaml.safe_load(f)
    
    # Update the variable (supports nested paths like 'interfaces.0.ip_address')
    parts = variable.split('.')
    current = variables
    for part in parts[:-1]:
        if part.isdigit():  # Handle list indices
            current = current[int(part)]
        else:
            current = current[part]
    
    if parts[-1].isdigit():
        current[int(parts[-1])] = value
    else:
        current[parts[-1]] = value
    
    # Save updated variables
    with open(yaml_path, 'w') as f:
        yaml.dump(variables, f, default_flow_style=False)
    
    # Regenerate configuration
    generate_config(node_path, template_name, variables)

def generate_config(node_path: str, template_name: str, variables: Dict[str, Any]) -> None:
    """
    Generate configuration using template and variables.
    """
    parts = node_path.split('/')
    node_family, node_class, node_name = parts
    
    # Set up Jinja2 environment
    template_dir = os.path.join(current_app.config['ROOT_FOLDER'],
                              'template', node_family, node_class)
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Load template
    template = env.get_template(f"{template_name}.j2")
    
    # Add timestamp to variables
    variables['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Generate configuration
    config = template.render(**variables)
    
    # Save to preview directory
    preview_dir = os.path.join(current_app.config['ROOT_FOLDER'],
                             'nodes', node_family, node_class, node_name, 'preview')
    if not os.path.exists(preview_dir):
        os.makedirs(preview_dir)
        
    # Append to the generated-config file
    with open(os.path.join(preview_dir, 'generated-config'), 'a') as f:
        f.write(config)
        f.write('\n')  # Add a newline between templates 