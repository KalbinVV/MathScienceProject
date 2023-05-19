from math import sqrt

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_string_dtype


def partial_corr(data_frame: pd.DataFrame) -> pd.DataFrame:
    removes_list = list()

    for column in data_frame.columns:
        if is_string_dtype(data_frame[column]):
            removes_list.append(column)

    data_frame = data_frame.drop(labels=removes_list, axis=1)
    array = np.asarray(data_frame)

    p = array.shape[1]
    correlation_array = np.zeros((p, p), dtype=float)

    for i in range(p):
        correlation_array[i, i] = 1

        for j in range(i + 1, p):
            idx = np.ones(p, dtype=bool)
            idx[i] = False
            idx[j] = False

            beta_i = np.linalg.lstsq(array[:, idx].astype('float'), array[:, j].astype('float'), rcond=None)[0]
            beta_j = np.linalg.lstsq(array[:, idx].astype('float'), array[:, i].astype('float'), rcond=None)[0]

            res_j = array[:, j] - array[:, idx].dot(beta_i)
            res_i = array[:, i] - array[:, idx].dot(beta_j)

            corr = pearsonr(res_i, res_j)
            correlation_array[i, j] = corr
            correlation_array[j, i] = corr

    correlation_dictionary = dict()

    for i_column in data_frame.columns:
        correlation_dictionary[i_column] = dict()

        for j_column in data_frame.columns:
            correlation_dictionary[i_column][j_column] = 0

    for i_index, i_column in enumerate(data_frame.columns):
        for j_index, j_column in enumerate(data_frame.columns):
            correlation_dictionary[i_column][j_column] = correlation_array[i_index, j_index]

    return pd.DataFrame(correlation_dictionary)


def geometric_mean(values: pd.DataFrame) -> float:
    result = 1

    for value in values:
        result *= value

    return result ** (1 / values.count())


def mode(values: pd.DataFrame) -> float:
    dictionary = dict()

    for value in values:
        dictionary[value] = dictionary.get(value, 0) + 1

    item, count = max(dictionary.items(), key=lambda pair: pair[1])

    return item


def standard_deviation(values: pd.DataFrame) -> float:
    result = 0
    average = 0

    for value in values:
        average += value

    average /= len(values)

    for value in values:
        result += pow(value - average, 2)

    result /= (len(values) - 1)

    return sqrt(result)


def dispersion(values: pd.DataFrame) -> float:
    result = 0.0
    average = mean(values)

    for value in values:
        result += pow(value - average, 2)

    return result / (len(values) - 1)


def median(values: pd.DataFrame) -> float:
    array_of_values = list(sorted(list(values)))

    length_of_array = len(array_of_values)
    middle_of_array = length_of_array // 2

    if length_of_array % 2 != 0:
        return array_of_values[middle_of_array]
    else:
        return (array_of_values[middle_of_array] + array_of_values[middle_of_array - 1]) / 2


def mean(values: pd.DataFrame) -> float:
    return sum(values) / len(values)


def sample_size(values: pd.DataFrame) -> float:
    variance_value = dispersion(values)
    delta = (0.5 * (((variance_value / 12) * (1 - 12 / 100)) ** 0.5))
    test = ((variance_value * 0.25) / round(delta, 2) / round(delta, 2))

    return round(test)


def average_sampling_error(values: pd.DataFrame) -> float:
    return (dispersion(values) / 15 * (1 - 15 / 100)) ** 0.5


def marginal_sampling_error(values: pd.DataFrame) -> float:
    return 2 * ((dispersion(values) / 15 * (1 - 15 / 100)) ** 0.5)


def kurtosis(values: pd.DataFrame) -> float:
    std = standard_deviation(values)
    average = mean(values)
    result = 0
    count = len(values)

    for value in values:
        result += pow((value - average) / std, 4)

    result *= (count * (count + 1)) / ((count - 1) * (count - 2) * (count - 3))
    result -= (3 * pow((count - 1), 2)) / ((count - 2) * (count - 3))

    return result


def asymmetry(values: pd.DataFrame) -> float:
    return (mean(values) - mode(values)) / standard_deviation(values)


def corr(data_frame: pd.DataFrame) -> pd.DataFrame:
    result_dictionary = dict()

    for i_column in data_frame:
        result_dictionary[i_column] = dict()
        for j_column in data_frame:
            result_dictionary[i_column][j_column] = pearsonr(data_frame[i_column], data_frame[j_column])

    return pd.DataFrame(result_dictionary)


# Парная корреляция
def pearsonr(x, y):
    n = len(x)
    sum_x = float(sum(x))
    sum_y = float(sum(y))
    sum_x_sq = sum(xi * xi for xi in x)
    sum_y_sq = sum(yi * yi for yi in y)
    psum = sum(xi * yi for xi, yi in zip(x, y))
    num = psum - (sum_x * sum_y / n)
    den = pow((sum_x_sq - pow(sum_x, 2) / n) * (sum_y_sq - pow(sum_y, 2) / n), 0.5)
    if den == 0:
        return 0

    return num / den


def least_squares(X, Y):
    if not isinstance(X[0], list):
        X = [X]
    if not isinstance(type(Y[0]), list):
        Y = [Y]

    if len(X) < len(X[0]):
        X = np.transpose(X)
    if len(Y) < len(Y[0]):
        Y = np.transpose(Y)

    for i in range(len(X)):
        X[i].append(1)

    AT = np.transpose(X)
    ATA = np.dot(AT, X)
    ATB = np.dot(AT, Y)
    coefs = np.linalg.solve(ATA, ATB)

    return coefs