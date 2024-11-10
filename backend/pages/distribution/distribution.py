from flask import render_template, request, flash, redirect, url_for
from . import distribution_blueprint
from .generate_excel import generate_distribution_data

# Define the limits for n and s
MAX_N = 1000  
MAX_S = 100  

@distribution_blueprint.route('/')
def distribution_home():
    return render_template('distribution.html')

@distribution_blueprint.route('/generate', methods=['POST'])
def generate_distribution_table():
    try:
        n = int(request.form['n'])
        s = int(request.form['s'])

        if n <= 0 or s <= 1:
            flash("Values for n must be greater than zero, and s must be greater than one.", "error")
            return redirect(url_for('distribution.distribution_home'))

        if n > MAX_N or s > MAX_S:
            flash(f"Values for n and s should not exceed {MAX_N} and {MAX_S} respectively.", "error")
            return redirect(url_for('distribution.distribution_home'))

        data = generate_distribution_data(n, s)
        return render_template('distribution.html', table_data=data, n=n, s=s)

    except ValueError:
        flash("Please enter valid integer values for n and s.", "error")
        return redirect(url_for('distribution.distribution_home'))

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('distribution.distribution_home'))
