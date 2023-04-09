import statistics
from functools import lru_cache

import numpy as np
import pandas as pd
import scipy
from pandas.core.dtypes.common import is_string_dtype
from scipy.stats import poisson, shapiro, chisquare

from Utils.FloatRange import FloatRange
from Utils.Utils import Utils


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

        key_field_name = 'Название'

        characteristic_dictionary = {
            'Название': [],
            'Мода': [],
            'Медиана': [],
            'Дисперсия': [],
            'Среднее арифметическое': [],
            'Стандартное отклонение': [],
            'Математическое ожидание': [],
            'Среднее геометрическое': [],
            'Эксцесс': [],
            'Асимметрия': [],
            'Средняя ошибка выборки': [],
            'Предельная ошибка выборки': [],
            'Объем выборки': []
        }

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            characteristic_dictionary['Название'].append(column)
            characteristic_dictionary['Мода'].append(statistics.mode(data_frame[column]))
            characteristic_dictionary['Медиана'].append(statistics.median(data_frame[column]))
            characteristic_dictionary['Дисперсия'].append(statistics.variance(data_frame[column]))
            characteristic_dictionary['Среднее арифметическое'].append(statistics.mean(data_frame[column]))
            characteristic_dictionary['Стандартное отклонение'].append(statistics.stdev(data_frame[column]))
            characteristic_dictionary['Математическое ожидание'].append(statistics.mean(data_frame[column]))

            try:
                characteristic_dictionary['Среднее геометрическое'].append(
                    statistics.geometric_mean(data_frame[column]))
            except (Exception,):
                characteristic_dictionary['Среднее геометрическое'].append(0)

            characteristic_dictionary['Средняя ошибка выборки'].append(
                ((statistics.variance(data_frame[column])) / 15 * (1 - 15 / 100)) ** 0.5)
            characteristic_dictionary['Предельная ошибка выборки'].append(
                2 * (((statistics.variance(data_frame[column])) / 15 * (1 - 15 / 100)) ** 0.5))
            characteristic_dictionary['Объем выборки'].append(
                (2 * 2 * statistics.variance(data_frame[column]) * 100) / (
                        2 * 2 * statistics.variance(data_frame[column]) + (
                        2 * (((statistics.variance(data_frame[column])) / 15 * (1 - 15 / 100)) ** 0.5)) ** 2 * 100))

            characteristic_dictionary['Эксцесс'].append(scipy.stats.kurtosis(data_frame[column]))
            characteristic_dictionary['Асимметрия'].append(scipy.stats.skew(data_frame[column]))

        return pd.DataFrame(characteristic_dictionary)

    @classmethod
    @lru_cache
    def get_chi_square_table(cls, file_name: str) -> pd.DataFrame:
        amount_of_intervals = 5
        significance = 0.05

        chi_square_dictionary = {
            'Название': [],
            'Количество интервалов': [],
            'Уровень значимости': [],
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

            expected_array = [max_value for _ in range(amount_of_intervals)]

            poisson_array = poisson.rvs(mu=data_frame[column].mean(), size=data_frame[column].count())
            chi_square_measure, p = chisquare(intervals, axis=None)

            chi_square_dictionary['Значение хи-квадрат'].append(chi_square_measure)

            chi_square_dictionary['Результат'].append('Да' if p >= significance else 'Нет')

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
