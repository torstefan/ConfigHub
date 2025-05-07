# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ConfigHub is a web-based configuration management and deployment tool for network devices. It uses Python, Flask, and Jinja2 templates to manage network device configurations through a structured directory system.

Key features:
- Configuration management through Jinja2 templates
- YAML-based variable management
- Git integration for version control
- Configuration verification and deployment
- Support for local and LDAP authentication
- Ansible-based deployment engine

## Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize the database (first time setup)
flask db init
flask db migrate
flask db upgrade

# Run the application
flask run
```

## Development Commands

```bash
# Run the application in development mode
python run.py

# Run tests
pytest

# Code formatting
black app

# Linting
flake8 app

# Database migrations
flask db migrate -m "Migration message"
flask db upgrade

# Run a specific test file
pytest tests/test_auth.py

# Run a specific test
pytest tests/test_auth.py::test_login
```

## Project Architecture

ConfigHub follows a modular architecture using Flask blueprints:

1. **Main Flask App (`app/__init__.py`)** - Initializes the Flask application, registers blueprints, and sets up logging.

2. **Blueprint Structure**:
   - `auth` - Authentication (login, user management)
   - `config` - Configuration management (templates, variables, git operations)
   - `deploy` - Deployment functionality (ansible integration)
   - `main` - Main pages and functionality
   - `api` - API endpoints for frontend communication

3. **Database Models (`app/models.py`)** - SQLAlchemy models for users and other data.

4. **Configuration Management**:
   - `app/config/template.py` - Template handling and rendering
   - `app/config/git.py` - Git repository operations
   - Template processing with Jinja2

5. **Network Configuration Directory Structure**:
   - Templates are organized by node family (e.g., ASR, Catalyst, Nexus) and class (Core, Distribution, Edge)
   - Node-specific configurations are stored in a standard directory structure

## Key Workflow

1. User authenticates through login page
2. User syncs with git repository to get latest configurations
3. User navigates the node structure (family → class → name)
4. User selects templates and edits variables
5. System generates the configuration preview
6. User verifies configuration with validation scripts
7. User deploys configuration to network devices via Ansible

## Important Files and Directories

- `app/config/routes.py` - Main configuration handling routes
- `app/config/template.py` - Template processing functions
- `app/deploy/routes.py` - Deployment handling
- `NetworkConfigGenerator/` - Contains templates and node configurations
- `app/templates/` - Frontend HTML templates (not to be confused with network templates)

## Security Notes

- The application validates all user input rigorously
- Path traversal protections are implemented
- User actions are logged for audit purposes
- YAML content is validated before processing