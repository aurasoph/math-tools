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
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise RuntimeError(f"API call failed with status {response.status_code}: {response.text}")
    data = response.json()

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

    print(f"DataFrames formatted")

    return euler_df.to_dict(orient="records"), verlet_df.to_dict(orient="records")