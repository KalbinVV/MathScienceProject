import numpy as np
import pandas as pd
from flask import request
from pandas.core.dtypes.common import is_string_dtype
from sklearn import linear_model

from MathScience import Statistics, Tables
from Utils import Helpers


def upload_report():
    file = request.files['file']

    try:
        file_name = Helpers.save_file(file)
    except (Exception, ) as e:
        return Helpers.generate_error_response(str(e))

    return Helpers.generate_successful_response(href=file_name)


def get_table():
    file_name = request.args['file']
    table_type = request.args['type']

    try:
        data = Helpers.convert_dataframe_to_dict({
            'source': Tables.get_source_table,
            'normalized': Tables.get_normalized_table,
            'statistic': Tables.get_statistic_table,
            'chi_square': Tables.get_chi_square_table,
            'correlation': Tables.get_correlation_table,
            'student': Tables.get_student_table,
            'student_partial': Tables.get_partial_student_table,
            'partial_correlation': Tables.get_partial_correlation_table
        }[table_type](file_name))

        return Helpers.generate_successful_response(data=data)
    except (Exception, ) as e:
        return Helpers.generate_error_response(str(e))


def get_intervals():
    file_name = request.args['file']

    try:
        data = Helpers.get_charts_data(file_name)

        return Helpers.generate_successful_response(data=data)
    except (Exception, ) as e:
        return Helpers.generate_error_response(str(e))


def get_linear_regression_coefficients_matrix():
    file_name = request.args['file']
    y_column = request.args['y']

    try:
        linear_regression_coefficients = Tables.get_linear_regression_coefficients(file_name, y_column)

        response_data_frame = Helpers.convert_dataframe_to_dict(linear_regression_coefficients)

        return Helpers.generate_successful_response(data=response_data_frame)
    except (Exception, ) as e:
        return Helpers.generate_error_response(str(e))


def get_linear_regression_coefficients():
    file_name = request.args['file']
    y = request.args['y']

    data_frame = Tables.get_normalized_table(file_name)

    incorrect_columns = list()

    for column in data_frame.columns:
        if is_string_dtype(data_frame[column]):
            incorrect_columns.append(column)

    data_frame = data_frame.drop(labels=incorrect_columns, axis=1)

    y_data_frame = data_frame[y]
    x_data_frame = data_frame.drop(labels=y, axis=1)

    regression = linear_model.LinearRegression()
    regression.fit(x_data_frame, y_data_frame)

    return Helpers.generate_successful_response(data={
        'coef': [regression.intercept_, *regression.coef_.tolist()],
        'intercept': regression.intercept_.tolist()})


def get_regression_student_coefficients_matrix():
    file_name = request.args['file']
    y = request.args['y']

    file_name = request.args['file']
    y = request.args['y']

    data_frame = Tables.get_normalized_table(file_name)

    data_frame = Helpers.remove_string_columns(data_frame)

    y_data_frame = data_frame[y]
    x_data_frame = data_frame.drop(labels=y, axis=1)

    regression = linear_model.LinearRegression()
    regression.fit(x_data_frame, y_data_frame)

    result_dict = {
        'Параметр': [f'b{i + 1}' for i in range(len(regression.coef_))],
        't': []
    }

    columns = x_data_frame.columns

    try:
        linear_regression_coefficients = regression.coef_

        for i in range(len(columns)):
            result_dict['t'].append(linear_regression_coefficients[i] / Statistics.average_sampling_error(x_data_frame[columns[i]]))

        linear_regression_student_data_frame = pd.DataFrame(result_dict)

        response_dict = Helpers.convert_dataframe_to_dict(linear_regression_student_data_frame)

        return Helpers.generate_successful_response(data=response_dict)
    except (Exception,) as e:
        return Helpers.generate_error_response(str(e))


# Not work
def get_regression_fault():
    file_name = request.args['file']
    y = request.args['y']

    data_frame = Tables.get_normalized_table(file_name)

    incorrect_columns = list()

    for column in data_frame.columns:
        if is_string_dtype(data_frame[column]):
            incorrect_columns.append(column)

    data_frame = data_frame.drop(labels=incorrect_columns, axis=1)

    y_data_frame = data_frame[y]
    x_data_frame = data_frame.drop(labels=y, axis=1)

    regression = linear_model.LinearRegression()
    regression.fit(x_data_frame, y_data_frame)

    result_dict = {'Исходное значение': [],
                   'Полученное значение': [],
                   'Погрешность': []}

    x_data_frame = x_data_frame
    y_data_frame = y_data_frame.values.tolist()

    for i, column in enumerate(x_data_frame.columns):
        source_value = y_data_frame[i]

        result_dict['Исходное значение'].append(source_value)

        predicted_value = regression.predict(x_data_frame[column])

        result_dict['Полученное значение'].append(predicted_value)
        result_dict['Погрешность'].append(abs(source_value - predicted_value))

    response_data_frame = pd.DataFrame(result_dict)

    return Helpers.generate_successful_response(data=Helpers.convert_dataframe_to_dict(response_data_frame))


def get_multiple_correlation_coefficients():
    file_name = request.args['file']

    response = Helpers.convert_dataframe_to_dict(Tables.get_multiple_correlation_coefficients_table(file_name))

    return Helpers.generate_successful_response(data=response)


def get_phisher_regression_coefficients():
    file_name = request.args['file']
    y = request.args['y']

    response = Helpers.convert_dataframe_to_dict(Tables.get_phisher_correlation_coefficients_table(file_name, y))

    return Helpers.generate_successful_response(data=response)
