from flask import render_template, current_app
from flask_login import login_required
from app.main import bp
from app.config.git import get_repo_status

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    """Home page route handler"""
    # Get Git repository status
    git_status = get_repo_status()
    
    return render_template('index.html', 
                         git_status=git_status)

@bp.route('/history')
@login_required
def history():
    """Configuration history page"""
    return render_template('history.html') 