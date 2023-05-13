from functools import lru_cache

import pandas as pd
from pandas.core.dtypes.common import is_string_dtype
from scipy.stats import chisquare
from sklearn import linear_model

from Configuration.Configuration import Configuration
from MathScience import Statistics
from Utils import Helpers
from Utils.FloatRange import FloatRange


class Tables:
    @staticmethod
    @lru_cache
    def get_source_table(file_name: str) -> pd.DataFrame:
        return Helpers.load_file(file_name)

    @classmethod
    def get_normalized_table(cls, file_name: str) -> pd.DataFrame:
        data_frame = Helpers.load_file(file_name)

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            data_frame[column] = (data_frame[column] - data_frame[column].min()) / (
                    data_frame[column].max() - data_frame[column].min())

        return data_frame

    @classmethod
    def get_statistic_table(cls, file_name: str) -> pd.DataFrame:
        data_frame = pd.DataFrame(cls.get_normalized_table(file_name))

        configuration = Configuration.language['statistic_table']

        # TODO: Change lambdas to functions
        required_fields_mapping = {
            # 'name': (function, fallback_value)
            'mode': (Statistics.mean, 0),
            'standard_deviation': (Statistics.standard_deviation, 0),
            'median': (Statistics.median, 0),
            'dispersion': (Statistics.dispersion, 0),
            'arithmetical_mean': (Statistics.mean, 0),
            'geometric_mean': (Statistics.geometric_mean, 0),
            'average_sampling_error': (Statistics.average_sampling_error, 0),
            'marginal_sampling_error': (Statistics.marginal_sampling_error, 0),
            'sample_size': (Statistics.sample_size, 0),
            'excess': (Statistics.kurtosis, 0),
            'asymmetry': (Statistics.asymmetry, 0)
        }

        characteristic_dictionary = dict()

        characteristic_dictionary[configuration['name']] = list()

        for key in required_fields_mapping:
            characteristic_dictionary[configuration[key]] = list()

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            characteristic_dictionary[configuration['name']].append(column)

            for key, mapping in required_fields_mapping.items():
                function, fallback_value = mapping

                try:
                    characteristic_dictionary[configuration[key]].append(function(data_frame[column]))
                except (Exception, ):
                    characteristic_dictionary[configuration[key]].append(fallback_value)

        return pd.DataFrame(characteristic_dictionary)

    @classmethod
    def get_chi_square_table(cls, file_name: str) -> pd.DataFrame:
        amount_of_intervals = 5
        significance = 0.05

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

        key_field = data_frame.columns.tolist()[0]

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
    def get_partial_correlation_table(cls, file_name: str):
        data_frame = cls.get_normalized_table(file_name)

        correlation_data_frame = Statistics.partial_corr(data_frame)

        # Трюк с колонкой названий
        correlation_data_frame.insert(0, " ", correlation_data_frame.columns)

        return correlation_data_frame

    @classmethod
    def get_student_table(cls, file_name: str):
        correlation = cls.get_correlation_table(file_name).to_dict()

        n = 12
        l = 6

        for i in correlation.keys():
            for j in correlation[i].keys():
                if isinstance(correlation[i][j], str):
                    continue

                try:
                    correlation[i][j] = (correlation[i][j] / ((1 - (correlation[i][j] ** 2)) ** 0.5)) * ((n - l - 2) ** 0.5)
                except (Exception, ):
                    correlation[i][j] = '-'

        return pd.DataFrame(correlation)

    @classmethod
    def get_linear_regression_coefficients(cls, file_name: str, y: str) -> pd.DataFrame:
        data_frame = cls.get_normalized_table(file_name)

        incorrect_columns = list()

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                incorrect_columns.append(column)

        data_frame = data_frame.drop(labels=incorrect_columns, axis=1)

        y_data_frame = data_frame[y]
        x_data_frame = data_frame.drop(labels=y, axis=1)

        regression = linear_model.LinearRegression()
        regression.fit(x_data_frame, y_data_frame)

        response_dictionary = {
            'Параметр': ['b' + str(i) for i in range(len(regression.coef_))],
            'Значение': regression.coef_.tolist()
        }

        response_data_frame = pd.DataFrame(response_dictionary)

        return response_data_frame

