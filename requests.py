import numpy as np
import pandas as pd
from flask import request
from pandas.core.dtypes.common import is_string_dtype
from sklearn import linear_model

from MathScience import Statistics
from MathScience.Tables.Tables import Tables
from Utils.Utils import Utils


def upload_report():
    file = request.files['file']

    try:
        file_name = Utils.save_file(file)
    except (Exception, ) as e:
        return Utils.generate_error_response(str(e))

    return Utils.generate_successful_response(href=file_name)


def get_table():
    file_name = request.args['file']
    table_type = request.args['type']

    try:
        data = Utils.convert_dataframe_to_dict({
            'source': Tables.get_source_table,
            'normalized': Tables.get_normalized_table,
            'statistic': Tables.get_statistic_table,
            'chi_square': Tables.get_chi_square_table,
            'correlation': Tables.get_correlation_table,
            'student': Tables.get_student_table,
            'partial_correlation': Tables.get_partial_correlation_table
        }[table_type](file_name))

        return Utils.generate_successful_response(data=data)
    except (Exception, ) as e:
        return Utils.generate_error_response(str(e))


def get_intervals():
    file_name = request.args['file']

    try:
        data = Utils.get_charts_data(file_name)

        return Utils.generate_successful_response(data=data)
    except (Exception, ) as e:
        return Utils.generate_error_response(str(e))


def get_linear_regression_coefficients():
    file_name = request.args['file']
    y_column = request.args['y']

    try:
        linear_regression_coefficients = Tables.get_linear_regression_coefficients(file_name, y_column)

        response_data_frame = Utils.convert_dataframe_to_dict(linear_regression_coefficients)

        return Utils.generate_successful_response(data=response_data_frame)
    except (Exception, ) as e:
        return Utils.generate_error_response(str(e))


def get_linear_regression_student_coefficients():
    file_name = request.args['file']
    y_column = request.args['y']

    data_frame = Tables.get_normalized_table(file_name)

    try:
        linear_regression_coefficients = Tables.get_linear_regression_coefficients(file_name, y_column).to_dict()

        columns = data_frame.columns.tolist()

        incorrect_columns = list()

        for column in columns:
            if is_string_dtype(data_frame[column]):
                incorrect_columns.append(column)

        for column in incorrect_columns:
            columns.remove(column)

        for i, value in enumerate(linear_regression_coefficients['Значение']):
            linear_regression_coefficients['Значение'][i] /= Statistics.standard_deviation(data_frame[columns[i]])

        linear_regression_coefficients['t'] = linear_regression_coefficients['Значение']

        del linear_regression_coefficients['Значение']

        linear_regression_student_data_frame = pd.DataFrame(linear_regression_coefficients)

        response_dict = Utils.convert_dataframe_to_dict(linear_regression_student_data_frame)

        return Utils.generate_successful_response(data=response_dict)
    except (Exception,) as e:
        return Utils.generate_error_response(str(e))
