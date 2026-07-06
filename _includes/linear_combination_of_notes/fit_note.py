import numpy as np


def off_diagonal_integral(frequency_0, frequency_1, upper_limit, lower_limit) -> float:
    frequency_diff = frequency_1 - frequency_0
    frequency_sum = frequency_0 + frequency_1
    term_0 = np.sin(frequency_diff * upper_limit)
    term_1 = np.sin(frequency_sum * upper_limit)
    term_2 = np.sin(frequency_diff * lower_limit)
    term_3 = np.sin(frequency_sum * lower_limit)
    return (term_0 - term_2) / (2 * frequency_diff) + (term_3 - term_1) / (
        2 * frequency_sum
    )


def diagonal_integral(frequency, upper_limit, lower_limit) -> float:
    return (upper_limit - lower_limit) / 2 - (
        np.sin(frequency * 2 * lower_limit) + np.sin(frequency * 2 * upper_limit)
    ) / (4 * frequency)
