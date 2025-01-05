from flask import render_template, request, flash, redirect, url_for
from . import simulation_blueprint
from .generate_excel import generate_simulation_data

@simulation_blueprint.route('/')
def simulation_home():
    return render_template('simulation.html')

@simulation_blueprint.route('/generate', methods=['POST'])
def generate_simulation_tables():
    try:
        start_time = request.form.get("start_time", "2023-09-13")
        stop_time = request.form.get("stop_time", "2025-08-01")
        step_size = request.form.get("step_size", "1 d")

        (
            euler_data,
            verlet_data,
            euler_distance_diff_plot,
            euler_angle_diff_plot,
            verlet_distance_diff_plot,
            verlet_angle_diff_plot,
        ) = generate_simulation_data(start_time, stop_time, step_size)

        return render_template(
            'simulation.html',
            euler_data=euler_data,
            verlet_data=verlet_data,
            euler_distance_diff_plot=euler_distance_diff_plot,
            euler_angle_diff_plot=euler_angle_diff_plot,
            verlet_distance_diff_plot=verlet_distance_diff_plot,
            verlet_angle_diff_plot=verlet_angle_diff_plot
        )

    except ValueError as e:
        flash("Invalid input. Please check your parameters.", "error")
        return redirect(url_for('simulation.simulation_home'))
    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return redirect(url_for('simulation.simulation_home'))
