from flask import request

from MathScience.Tables.Tables import Tables
from Utils.Utils import Utils


def upload_report():
    file = request.files['file']

    try:
        file_name = Utils.save_file(file)
    except (Exception, ) as e:
        return {'status': False, 'reason': str(e)}

    return {'status': True, 'href': file_name}


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

        return {'status': True, 'data': data}
    except (Exception, ) as e:
        return {'status': False, 'reason': str(e)}


def get_intervals():
    file_name = request.args['file']

    try:
        data = Utils.get_charts_data(file_name)

        return {'status': True, 'data': data}
    except (Exception, ) as e:
        return {'status': False, 'reason': str(e)}