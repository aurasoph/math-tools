from flask import render_template
from . import page2_blueprint

@page2_blueprint.route('/')
def page2_home():
    return render_template('page2.html')
