import numpy as np
import pandas as pd

def rotate_data_to_minimize_z_spread(filtered_data_df):
    try:
        filtered_data_df = filtered_data_df.apply(pd.to_numeric, errors='coerce')
        filtered_data_df = filtered_data_df.dropna()  

        # Isolate position (C-E) and velocity (F-H) columns
        position_data = filtered_data_df.iloc[:, 0:3].to_numpy()
        velocity_data = filtered_data_df.iloc[:, 3:6].to_numpy()

        # Center the position data by subtracting the mean
        centered_position = position_data - np.mean(position_data, axis=0)

        # Calculate covariance matrix
        cov_matrix = np.cov(centered_position, rowvar=False)

        # Eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)

        # Find the eigenvector with the smallest eigenvalue
        min_variance_vector = eigenvectors[:, np.argmin(eigenvalues)]

        # Rotation matrix
        z_axis = np.array([0, 0, 1])
        rotation_axis = np.cross(min_variance_vector, z_axis)
        rotation_angle = np.arccos(np.clip(np.dot(min_variance_vector, z_axis), -1.0, 1.0))

        # Normalize rotation axis
        if np.linalg.norm(rotation_axis) != 0:
            rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)

        # Rodrigues' rotation formula
        K = np.array([[0, -rotation_axis[2], rotation_axis[1]],
                      [rotation_axis[2], 0, -rotation_axis[0]],
                      [-rotation_axis[1], rotation_axis[0], 0]])
        rotation_matrix = (
            np.eye(3) +
            np.sin(rotation_angle) * K +
            (1 - np.cos(rotation_angle)) * np.dot(K, K)
        )

        rotated_position = np.dot(centered_position, rotation_matrix.T)
        rotated_velocity = np.dot(velocity_data, rotation_matrix.T)

        rotated_data = np.hstack([rotated_position, rotated_velocity])
        rotated_data_df = pd.DataFrame(rotated_data, columns=[
            'X_rotated', 'Y_rotated', 'Z_rotated', 'VX_rotated', 'VY_rotated', 'VZ_rotated'
        ])

        return rotated_data_df

    except Exception as e:
        raise ValueError(f"Error during data rotation: {e}")
