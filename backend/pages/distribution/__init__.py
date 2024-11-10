from flask import Blueprint

distribution_blueprint = Blueprint('distribution', __name__, template_folder='templates', static_folder='static')

from .distribution import *
