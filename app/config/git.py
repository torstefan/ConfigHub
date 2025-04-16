from git import Repo
from flask import current_app
import os
from datetime import datetime

def sync_with_repo() -> str:
    """
    Sync with remote git repository.
    Returns a message indicating the sync status.
    """
    root_folder = current_app.config['ROOT_FOLDER']
    repo_url = current_app.config['GIT_REPO_URL']
    git_token = current_app.config['GIT_TOKEN']

    # Ensure root folder exists
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)

    try:
        if not os.path.exists(os.path.join(root_folder, '.git')):
            # Clone repository
            if git_token:
                # Insert token into URL for authentication
                url_parts = repo_url.split('://')
                auth_url = f"{url_parts[0]}://oauth2:{git_token}@{url_parts[1]}"
            else:
                auth_url = repo_url

            repo = Repo.clone_from(auth_url, root_folder)
            return "Repository cloned successfully"
        else:
            # Repository exists, sync changes
            repo = Repo(root_folder)
            
            # Add all changes
            repo.git.add(all=True)
            
            # Check if there are changes to commit
            if repo.is_dirty() or len(repo.untracked_files) > 0:
                # Commit changes
                commit_message = f"Auto-commit: Configuration changes at {datetime.now()}"
                repo.git.commit('-m', commit_message)
            
            # Pull latest changes
            origin = repo.remotes.origin
            origin.pull()
            
            # Push our changes
            if git_token:
                with repo.git.custom_environment(GIT_SSL_NO_VERIFY='true'):
                    origin.push()
            else:
                origin.push()
            
            return "Repository synced successfully"
            
    except Exception as e:
        current_app.logger.error(f"Git sync error: {str(e)}")
        raise Exception(f"Failed to sync repository: {str(e)}")

def get_repo_status() -> dict:
    """
    Get the current status of the repository.
    Returns a dictionary with status information.
    """
    root_folder = current_app.config['ROOT_FOLDER']
    
    try:
        if not os.path.exists(os.path.join(root_folder, '.git')):
            return {
                'initialized': False,
                'status': 'Not initialized'
            }
            
        repo = Repo(root_folder)
        return {
            'initialized': True,
            'status': 'Clean' if not repo.is_dirty() else 'Has changes',
            'branch': repo.active_branch.name,
            'last_commit': {
                'hash': repo.head.commit.hexsha[:7],
                'message': repo.head.commit.message,
                'date': datetime.fromtimestamp(repo.head.commit.committed_date)
            }
        }
        
    except Exception as e:
        current_app.logger.error(f"Git status error: {str(e)}")
        return {
            'initialized': False,
            'status': f'Error: {str(e)}'
        } 