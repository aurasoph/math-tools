# pages/distribution/distribution.py
from flask import render_template, request
from . import distribution_blueprint
from .generate_excel import generate_distribution_data

@distribution_blueprint.route('/')
def distribution_home():
    return render_template('distribution.html')

@distribution_blueprint.route('/generate', methods=['POST'])
def generate_distribution_table():
    n = int(request.form['n'])
    s = int(request.form['s'])
    data = generate_distribution_data(n, s)  # Get the data as a list of dictionaries
    return render_template('distribution.html', table_data=data, n=n, s=s)
