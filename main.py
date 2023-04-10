from flask import Flask, render_template, request

from Configuration.Configuration import Configuration
from MathScience.Tables.Tables import Tables
from Utils.Utils import Utils

app = Flask(__name__, static_folder='web/static', template_folder='web/templates')


@app.route('/')
def index():
    language_configuration = Configuration.language

    return render_template('index.html',
                           title=language_configuration['title'],
                           subtitle=language_configuration['subtitle'],
                           footer=language_configuration['footer'])


@app.route('/upload_report', methods=['GET', 'POST'])
def init_report():
    file = request.files['file']

    try:
        Utils.save_file(file)
    except (Exception, ) as e:
        return {'status': False, 'reason': str(e)}

    return {'status': True, 'href': file.filename}


@app.route('/reports/<file_name>')
def report_view(file_name: str):
    language_configuration = Configuration.language

    return render_template('report_view.html',
                           title=language_configuration['title'],
                           subtitle=language_configuration['subtitle'],
                           footer=language_configuration['footer'],
                           file_name=file_name,
                           source_table_header=language_configuration['source_table']['header'],
                           normalized_table_header=language_configuration['normalized_table']['header'],
                           statistic_table_header=language_configuration['statistic_table']['header'],
                           pearson_table_header=language_configuration['pearson_table']['header'],
                           correlation_matrix_header=language_configuration['correlation_matrix']['header'],
                           show_table_button=language_configuration['ui']['show_table_button'],
                           show_charts_button=language_configuration['ui']['show_charts_button'],
                           charts_header=language_configuration['ui']['charts_header'],
                           chart_prefix=language_configuration['ui']['chart_prefix'])


@app.route('/get_table', methods=['GET'])
def get_table():
    file_name = request.args['file']
    table_type = request.args['type']

    try:
        data = Utils.convert_dataframe_to_dict({
            'source': Tables.get_source_table,
            'normalized': Tables.get_normalized_table,
            'statistic': Tables.get_statistic_table,
            'chi_square': Tables.get_chi_square_table,
            'correlation': Tables.get_correlation_table
        }[table_type](file_name))

        return {'status': True, 'data': data}
    except (Exception, ) as e:
        return {'status': False, 'reason': str(e)}


@app.route('/get_intervals', methods=['GET'])
def get_intervals():
    file_name = request.args['file']

    try:
        data = Utils.get_charts_data(file_name)

        return {'status': True, 'data': data}
    except (Exception, ) as e:
        return {'status': False, 'reason': str(e)}


def main():
    app.run()


if __name__ == '__main__':
    main()
