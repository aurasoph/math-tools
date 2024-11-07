# pages/distribution/generate_excel.py
import pandas as pd
from scipy.stats import norm
import math
from fractions import Fraction


def P(p, n, s):
    def binomial_coefficient(n, k):
        coeff = Fraction(1)
        for x in range(k):
            coeff *= (n - x)
            coeff *= Fraction(1, x + 1)
        return coeff

    sum_val = Fraction(0) 
    upper_limit = (p - n) // s

    for k in range(upper_limit + 1):
        sum_val += (-1)**k * binomial_coefficient(n, k) * binomial_coefficient(p - s * k - 1, n - 1)

    return float(sum_val / s**n)


def generate_distribution_data(n, s):
    values = []
    p_values = range(n, n*s + 1)  
    mean = (n + n*s) / 2
    variance = 0

    for p in p_values:
        weight = P(p, n, s)
        values.append(weight)
        variance += weight * (p - mean)**2
    SD = math.sqrt(variance)

    approx_values = []
    z_values = []
    for p in p_values:
        z = (p - mean) / SD
        z_values.append(z)
        f_z = (1/math.sqrt(2*math.pi)) * math.exp(-0.5*z**2)
        approx_values.append(f_z)
    percentiles = [norm.cdf(z) * 100 for z in z_values]

    scale_factor = sum(values) / sum(approx_values)
    approx_values = [f_z * scale_factor for f_z in approx_values]

    percent_errors = []
    for actual, approx in zip(values, approx_values):
        error = abs((actual - approx) / approx) * 100
        percent_errors.append(error)

    df_main = pd.DataFrame({
        'Sum (p)': p_values,
        'Actual Probability of Sum': values,
        'Z-Values': z_values,
        'Percentile (%)': percentiles,
        'Normal Approximation': approx_values,
        'Percent Error (%)': percent_errors
    })

    # Convert the DataFrame to a dictionary for easy HTML rendering
    return df_main.to_dict(orient="records")
