from flask import Blueprint

bp = Blueprint('deploy', __name__)

from app.deploy import routes 