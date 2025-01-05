from flask import Blueprint

simulation_blueprint = Blueprint('simulation', __name__, template_folder='templates', static_folder='static')

from .simulation import *
