from flask import Blueprint

page2_blueprint = Blueprint('page2', __name__, template_folder='templates', static_folder='static')

from .page2 import *
