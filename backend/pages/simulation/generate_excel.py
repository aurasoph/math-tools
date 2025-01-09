import matplotlib.pyplot as plt
import base64
import io
import requests
import pandas as pd
import numpy as np
from .data_rotation import rotate_data_to_minimize_z_spread
from .approximations import euler_method_2d
from .approximations import verlet_method_2d

def generate_simulation_data(start_time, stop_time, step_size):
    print(f"Generate Function Initiated")
    url = "https://ssd.jpl.nasa.gov/api/horizons.api"
    params = {
        "format": "json",
        "COMMAND": "'499'",
        "EPHEM_TYPE": "VECTORS",
        "CENTER": "'@0'",
        "START_TIME": f"'{start_time}'",
        "STOP_TIME": f"'{stop_time}'",
        "STEP_SIZE": f"'{step_size}'",
        "VEC_TABLE": "2",
        "CSV_FORMAT": "YES"
    }

    # Get API Response
    try:
        response = requests.get(url, params=params, timeout=3)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError("API currently unavailable") from e


    # Extract and Process Data
    raw_data = data["result"]
    lines = raw_data.splitlines()
    rows = [line.split(",") for line in lines if line.strip()]
    df = pd.DataFrame(rows)


    # Process Rotated Data
    filtered_data = df.iloc[46:, 2:8].apply(pd.to_numeric, errors="coerce").dropna()
    rotated_df = rotate_data_to_minimize_z_spread(filtered_data)

    print(f"Rotated Data")

    # Simulation parameters
    time_step = 86400 
    steps = len(rotated_df)

    # Initial Conditions
    initial_position = rotated_df.iloc[0][['X_rotated', 'Y_rotated']].to_numpy()
    initial_velocity = rotated_df.iloc[0][['VX_rotated', 'VY_rotated']].to_numpy()
    sun_position = np.array([0.0, 0.0])

    # Simulate Orbits
    euler_positions = euler_method_2d(sun_position, initial_position, initial_velocity, time_step, steps - 1)
    verlet_positions = verlet_method_2d(sun_position, initial_position, initial_velocity, time_step, steps - 1)

    # Cartesian to Polar Conversion
    def cartesian_to_polar(data):
        modulus = np.sqrt(data[:, 0]**2 + data[:, 1]**2)
        argument = np.arctan2(data[:, 1], data[:, 0])
        return np.column_stack((modulus, argument))

    # Actual Cartesian and Polar Coordinates
    actual_coordinates = rotated_df[['X_rotated', 'Y_rotated']].to_numpy()
    actual_polar = cartesian_to_polar(actual_coordinates)

    # Generate Euler Data
    euler_distances_angles = cartesian_to_polar(euler_positions)
    euler_df = pd.DataFrame({
        'Step': range(steps),
        'X_actual': actual_coordinates[:, 0],
        'Y_actual': actual_coordinates[:, 1],
        'Distance_actual': actual_polar[:, 0],
        'Angle_actual': actual_polar[:, 1],
        'X_simulated': euler_positions[:, 0],
        'Y_simulated': euler_positions[:, 1],
        'Distance_simulated': euler_distances_angles[:, 0],
        'Angle_simulated': euler_distances_angles[:, 1]
    })

    # Generate Verlet Data
    verlet_distances_angles = cartesian_to_polar(verlet_positions)
    verlet_df = pd.DataFrame({
        'Step': range(steps),
        'X_actual': actual_coordinates[:, 0],
        'Y_actual': actual_coordinates[:, 1],
        'Distance_actual': actual_polar[:, 0],
        'Angle_actual': actual_polar[:, 1],
        'X_simulated': verlet_positions[:, 0],
        'Y_simulated': verlet_positions[:, 1],
        'Distance_simulated': verlet_distances_angles[:, 0],
        'Angle_simulated': verlet_distances_angles[:, 1]
    })

    # Scientific Notation Application
    def format_scientific(value):
        return np.format_float_scientific(value, precision=5) if isinstance(value, (float, np.floating)) else value

    for df in [euler_df, verlet_df]:
        for col in ['X_actual', 'Y_actual', 'Distance_actual', 'X_simulated', 'Y_simulated', 'Distance_simulated']:
            df[col] = df[col].apply(format_scientific)

        for col in ['Angle_actual', 'Angle_simulated']:
            df[col] = df[col].apply(lambda x: round(x, 5))

    euler_distance_diff = np.abs(actual_polar[:, 0] - euler_distances_angles[:, 0])
    euler_angle_diff = np.abs(np.arctan2(np.sin(actual_polar[:, 1] - euler_distances_angles[:, 1]),
                                         np.cos(actual_polar[:, 1] - euler_distances_angles[:, 1])))

    verlet_distance_diff = np.abs(actual_polar[:, 0] - verlet_distances_angles[:, 0])
    verlet_angle_diff = np.abs(np.arctan2(np.sin(actual_polar[:, 1] - verlet_distances_angles[:, 1]),
                                          np.cos(actual_polar[:, 1] - verlet_distances_angles[:, 1])))

    # Helper function to create a plot and return it as a base64 string
    def create_plot(x, y, title, xlabel, ylabel, color):
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, label=title, color=color)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.grid()
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plot_data = base64.b64encode(buf.getvalue()).decode("utf-8")
        plt.close()
        return plot_data

    # Generate Euler plots
    euler_distance_diff_plot = create_plot(
        range(steps), euler_distance_diff, "Euler's Distance Difference", "Step", "Distance Difference (km)", "blue"
    )
    euler_angle_diff_plot = create_plot(
        range(steps), euler_angle_diff, "Euler's Angular Difference", "Step", "Angular Difference (radians)", "red"
    )

    # Generate Verlet plots
    verlet_distance_diff_plot = create_plot(
        range(steps), verlet_distance_diff, "Verlet's Distance Difference", "Step", "Distance Difference (km)", "green"
    )
    verlet_angle_diff_plot = create_plot(
        range(steps), verlet_angle_diff, "Verlet's Angular Difference", "Step", "Angular Difference (radians)", "orange"
    )

    # Return data and plots
    return (
        euler_df.to_dict(orient="records"),
        verlet_df.to_dict(orient="records"),
        euler_distance_diff_plot,
        euler_angle_diff_plot,
        verlet_distance_diff_plot,
        verlet_angle_diff_plot,
    )