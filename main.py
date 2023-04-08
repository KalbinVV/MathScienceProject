import json

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
                           file_name=file_name)


@app.route('/get_table', methods=['GET'])
def get_table():
    file_name = request.args['file']
    table_type = request.args['type']

    try:
        data = Utils.convert_dataframe_to_dict({
            'source': Tables.get_source_table(file_name),
            'normalized': Tables.get_normalized_table(file_name),
            'statistic': Tables.get_statistic_table(file_name),
            'chi_square': Tables.get_chi_square_table(file_name),
            'correlation': Tables.get_correlation_table(file_name)
        }[table_type])

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
