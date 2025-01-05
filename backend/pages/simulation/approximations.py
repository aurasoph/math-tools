import numpy as np

# Helper function to calculate acceleration
def compute_acceleration_2d(pos1, pos2, mass):
    G = 6.67430e-20
    distance_vector = pos2 - pos1
    distance = np.linalg.norm(distance_vector)
    acceleration = -G * (mass / distance**3) * distance_vector
    return acceleration

# Euler's Method
def euler_method_2d(pos1, pos2, vel2, time_step, steps):
    mass = 1.989e30
    positions = [pos2]
    velocity = vel2

    for _ in range(steps):
        acceleration = compute_acceleration_2d(pos1, pos2, mass)
        pos2 = pos2 + velocity * time_step
        velocity = velocity + acceleration * time_step
        positions.append(pos2)

    return np.array(positions)

# Verlet's Method
def verlet_method_2d(pos1, pos2, vel2, time_step, steps):
    mass = 1.989e30
    positions = [pos2]
    prev_pos = pos2 - vel2 * time_step

    for _ in range(steps):
        acceleration = compute_acceleration_2d(pos1, pos2, mass)
        new_pos = 2 * pos2 - prev_pos + acceleration * time_step**2
        prev_pos = pos2
        pos2 = new_pos
        positions.append(pos2)

    return np.array(positions)