# ConfigHub

A web-based configuration management and deployment tool for network devices.

## Features

- Configuration management through Jinja2 templates
- YAML-based variable management
- Git integration for version control
- Configuration verification and deployment
- Support for local and LDAP authentication
- Ansible-based deployment engine

## Project Structure

```
confighub/
├── app/                    # Web application
│   ├── __init__.py        # Flask app initialization
│   ├── auth/              # Authentication module
│   │   ├── __init__.py
│   │   ├── models.py      # User models
│   │   └── routes.py      # Auth routes
│   ├── config/            # Configuration management
│   │   ├── __init__.py
│   │   ├── git.py         # Git operations
│   │   ├── template.py    # Template operations
│   │   └── verify.py      # Verification logic
│   ├── deploy/            # Deployment module
│   │   ├── __init__.py
│   │   ├── ansible.py     # Ansible integration
│   │   └── routes.py      # Deployment routes
│   ├── models/            # Database models
│   │   ├── __init__.py
│   │   └── audit.py       # Audit logging model
│   ├── static/            # Static files
│   │   ├── css/
│   │   └── js/
│   ├── templates/         # Jinja2 HTML templates
│   │   ├── auth/
│   │   ├── config/
│   │   └── deploy/
│   └── utils/             # Utility functions
│       ├── __init__.py
│       └── logger.py      # Logging setup
├── instance/              # Instance-specific files
├── logs/                  # Application logs
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_config.py
│   └── test_deploy.py
├── .env.example          # Example environment variables
├── .gitignore           # Git ignore file
├── config.py            # Application config
├── requirements.txt     # Python dependencies
└── run.py              # Application entry point
```

## Network Configuration Repository Structure

```
NetworkConfigGenerator/
├── template/
│   ├── ASR/              # Node family
│   │   ├── Core/         # Node class
│   │   │   └── *.j2     # Jinja2 templates
│   │   ├── Distribution/
│   │   └── Edge/
│   ├── Catalyst/
│   └── Nexus/
└── nodes/
    ├── ASR/
    │   └── Core/
    │       └── node-name/
    │           ├── inventory/
    │           │   └── inventory.yml
    │           ├── vars/
    │           │   └── *.yml
    │           ├── preview/
    │           │   └── generated-config
    │           ├── logs/
    │           │   └── deployment_date_time/
    │           └── verification/
    │               └── *.py
    ├── Catalyst/
    └── Nexus/
```

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure your environment variables
5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. Run the application:
   ```bash
   flask run
   ```

## Development

- Use `black` for code formatting
- Use `flake8` for linting
- Run tests with `pytest`

## License

This project is licensed under the MIT License. 