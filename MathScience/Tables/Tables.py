import statistics
from functools import lru_cache

import pandas as pd
import scipy
from pandas.core.dtypes.common import is_string_dtype
from scipy.stats import poisson, chisquare

from Configuration.Configuration import Configuration
from Utils.FloatRange import FloatRange
from Utils.Utils import Utils

import pingouin as pg


class Tables:
    @staticmethod
    @lru_cache
    def get_source_table(file_name: str) -> pd.DataFrame:
        return Utils.load_file(file_name)

    @classmethod
    @lru_cache
    def get_normalized_table(cls, file_name: str) -> pd.DataFrame:
        data_frame = Utils.load_file(file_name)

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            data_frame[column] = (data_frame[column] - data_frame[column].min()) / (
                    data_frame[column].max() - data_frame[column].min())

        return data_frame

    @classmethod
    @lru_cache
    def get_statistic_table(cls, file_name: str) -> pd.DataFrame:
        data_frame = pd.DataFrame(cls.get_normalized_table(file_name))

        configuration = Configuration.language['statistic_table']

        array_of_fields = ['name', 'mode', 'median', 'dispersion', 'arithmetical_mean',
                           'standard_deviation', 'expected_value', 'geometric_mean', 'excess',
                           'asymmetry', 'average_sampling_error', 'marginal_sampling_error', 'sample_size']

        characteristic_dictionary = dict()

        for field in array_of_fields:
            characteristic_dictionary[configuration[field]] = list()

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            characteristic_dictionary[configuration['name']].append(column)
            characteristic_dictionary[configuration['mode']].append(statistics.mode(data_frame[column]))
            characteristic_dictionary[configuration['median']].append(statistics.median(data_frame[column]))
            characteristic_dictionary[configuration['dispersion']].append(statistics.variance(data_frame[column]))
            characteristic_dictionary[configuration['arithmetical_mean']].append(statistics.mean(data_frame[column]))
            characteristic_dictionary[configuration['standard_deviation']].append(statistics.stdev(data_frame[column]))
            characteristic_dictionary[configuration['expected_value']].append(statistics.mean(data_frame[column]))

            try:
                characteristic_dictionary[configuration['geometric_mean']].append(statistics.geometric_mean(data_frame[column]))
            except (Exception,):
                characteristic_dictionary[configuration['geometric_mean']].append(0)

            characteristic_dictionary[configuration['average_sampling_error']].append(
                ((statistics.variance(data_frame[column])) / 15 * (1 - 15 / 100)) ** 0.5)
            characteristic_dictionary[configuration['marginal_sampling_error']].append(
                2 * (((statistics.variance(data_frame[column])) / 15 * (1 - 15 / 100)) ** 0.5))
            characteristic_dictionary[configuration['sample_size']].append(
                (2 * 2 * statistics.variance(data_frame[column]) * 100) / (
                        2 * 2 * statistics.variance(data_frame[column]) + (
                        2 * (((statistics.variance(data_frame[column])) / 15 * (1 - 15 / 100)) ** 0.5)) ** 2 * 100))

            characteristic_dictionary[configuration['excess']].append(scipy.stats.kurtosis(data_frame[column]))
            characteristic_dictionary[configuration['asymmetry']].append(scipy.stats.skew(data_frame[column]))

        return pd.DataFrame(characteristic_dictionary)

    # TODO: Add support for all table types
    @classmethod
    @lru_cache
    def get_chi_square_table(cls, file_name: str) -> pd.DataFrame:
        amount_of_intervals = 5
        significance = 0.05

        key_field = 'Название'
        critical_value = 3.33

        chi_square_dictionary = {
            'Название': [],
            'Количество интервалов': [],
            'Уровень значимости': [],
            'Число степеней свободы': [],
            'Критическое значение': [],
            'Минимальное значение': [],
            'Максимальное значение': [],
            'Шаг': [],
            'Интервалы': [],
            'Значение хи-квадрат': [],
            'Результат': []
        }

        data_frame = Tables.get_normalized_table(file_name)

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            chi_square_dictionary['Название'].append(column)
            chi_square_dictionary['Количество интервалов'].append(amount_of_intervals)
            chi_square_dictionary['Уровень значимости'].append(significance)
            chi_square_dictionary['Число степеней свободы'].append(data_frame[key_field].count() - 3)
            chi_square_dictionary['Критическое значение'].append(critical_value)

            min_value = data_frame[column].min()
            max_value = data_frame[column].max()

            chi_square_dictionary['Минимальное значение'].append(min_value)
            chi_square_dictionary['Максимальное значение'].append(max_value)

            interval_step = (max_value - min_value) / amount_of_intervals

            chi_square_dictionary['Шаг'].append(interval_step)

            intervals = []
            for i in range(amount_of_intervals):
                float_range = FloatRange(i * interval_step, (i + 1) * interval_step)

                amount = 0
                for value in data_frame[column]:
                    if value in float_range:
                        amount += 1

                intervals.append(amount)

            chi_square_dictionary['Интервалы'].append(str(intervals))

            chi_square_measure, p = chisquare(intervals, axis=None)

            chi_square_dictionary['Значение хи-квадрат'].append(chi_square_measure)

            chi_square_dictionary['Результат'].append('Да' if chi_square_measure <= critical_value else 'Нет')

        return pd.DataFrame(chi_square_dictionary)

    @classmethod
    @lru_cache
    def get_correlation_table(cls, file_name: str) -> pd.DataFrame:
        data_frame = cls.get_normalized_table(file_name)

        # Fix for PythonAnywhere
        version_of_pandas = float('.'.join(pd.__version__.split('.')[0:1]))

        if version_of_pandas >= 1.5:
            correlation_data_frame = data_frame.corr(numeric_only=True).round(3)
        else:
            correlation_data_frame = data_frame.corr().round(3)

        # Трюк с колонкой названий
        correlation_data_frame.insert(0, " ", correlation_data_frame.columns)

        return correlation_data_frame

    @classmethod
    @lru_cache
    def get_partial_correlation_table(cls, file_name: str, covar: str):
        data_frame: pd.DataFrame = cls.get_source_table(file_name)

        result_dict = {}

        for column in data_frame.columns:
            result_dict[column] = dict()

        array = list()

        for i_column in data_frame.columns:
            for j_column in data_frame.columns:
                if is_string_dtype(data_frame[i_column]):
                    continue

                if is_string_dtype(data_frame[j_column]):
                    continue

                if i_column == j_column:
                    result_dict[i_column][j_column] = 1
                    continue

                if i_column == covar or j_column == covar:
                    continue

                result_dict[i_column][j_column] = float(pg.partial_corr(data=data_frame, x=i_column, y=j_column, covar=covar)['r'].iloc[0])

        keys_to_remove = [covar]

        for key in result_dict:
            if not result_dict[key]:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del result_dict[key]

        result_data_frame = pd.DataFrame(result_dict).fillna(1)

        result_data_frame.insert(0, " ", result_data_frame.columns)

        return result_data_frame
