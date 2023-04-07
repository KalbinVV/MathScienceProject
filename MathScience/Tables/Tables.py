import statistics

import pandas as pd
import scipy
from pandas.core.dtypes.common import is_string_dtype
from scipy.stats import poisson, shapiro

from Utils.Utils import Utils


class Tables:
    @staticmethod
    def get_source_table(file_name: str) -> pd.DataFrame:
        return Utils.load_file(file_name)

    @classmethod
    def get_normalized_table(cls, file_name: str) -> pd.DataFrame:
        data_frame = Utils.load_file(file_name)

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            data_frame[column] = (data_frame[column] - data_frame[column].min()) / (
                    data_frame[column].max() - data_frame[column].min())

        return data_frame

    @classmethod
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
    def get_chi_square_table(cls, file_name: str) -> pd.DataFrame:
        amount_of_intervals = 5

        chi_square_dictionary = {
            'Название': [],
            'Количество интервалов': [],
            'Максимальное значение': [],
            'Минимальное значение': [],
            'Интервалы': [],
            'Количество значений, попавших в интервалы': [],
            'Результат статистики': [],
            'p': [],
            'Нормальное распределение?': []
        }

        data_frame = Utils.load_file(file_name)

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            chi_square_dictionary['Название'].append(column)

            poisson_array = poisson.rvs(mu=data_frame[column].mean(), size=data_frame[column].count())

            chi_square_test_result = shapiro(data_frame[column])

            chi_square_dictionary['Количество интервалов'].append(amount_of_intervals)

            min_value = data_frame[column].min()
            max_value = data_frame[column].max()

            intervals_step = (max_value - min_value) / amount_of_intervals

            chi_square_dictionary['Максимальное значение'].append(max_value)
            chi_square_dictionary['Минимальное значение'].append(min_value)
            chi_square_dictionary['Интервалы'].append(intervals_step)

            chi_square_dictionary['Результат статистики'].append(chi_square_test_result[0])
            chi_square_dictionary['p'].append(chi_square_test_result[1])

            intervals_result = ''
            previous_interval = 0
            for i in range(amount_of_intervals):
                interval = range(int(previous_interval), int(data_frame[column][i] + intervals_step))

                amount = 0
                for value in data_frame[column]:
                    if value in interval:
                        amount += 1

                intervals_result += str(amount) + ';'

                previous_interval = data_frame[column][i] + intervals_step

            chi_square_dictionary['Количество значений, попавших в интервалы'].append(intervals_result)

            chi_square_dictionary['Нормальное распределение?'].append(
                'Да' if chi_square_test_result[1] >= 0.05 else 'Нет')

        return pd.DataFrame(chi_square_dictionary)
