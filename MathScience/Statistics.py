import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_string_dtype
from scipy.stats import stats


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

            corr = stats.pearsonr(res_i, res_j)[0]
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
    return values.std()


def dispersion(values: pd.DataFrame) -> float:
    return values.var()


def median(values: pd.DataFrame) -> float:
    array_of_values = list(sorted(list(values)))

    length_of_array = len(array_of_values)
    middle_of_array = length_of_array // 2

    if length_of_array % 2 != 0:
        return array_of_values[middle_of_array]
    else:
        return (array_of_values[middle_of_array] + array_of_values[middle_of_array- 1]) / 2


def mean(values: pd.DataFrame) -> float:
    return sum(values) / len(values)


def sample_size(values: pd.DataFrame) -> float:
    return (2 * 2 * dispersion(values) * 100) / (
            2 * 2 * dispersion(values) + (
            2 * (((dispersion(values)) / 15 * (1 - 15 / 100)) ** 0.5)) ** 2 * 100)


def average_sampling_error(values: pd.DataFrame) -> float:
    return (dispersion(values) / 15 * (1 - 15 / 100)) ** 0.5


def marginal_sampling_error(values: pd.DataFrame) -> float:
    return 2 * ((dispersion(values) / 15 * (1 - 15 / 100)) ** 0.5)


def kurtosis(values: pd.DataFrame) -> float:
    return values.kurtosis()


def asymmetry(values: pd.DataFrame) -> float:
    return values.skew()
