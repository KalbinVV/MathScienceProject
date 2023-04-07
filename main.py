import json

from flask import Flask, render_template, request

from Configuration.Configuration import Configuration
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
        return json.dumps({'status': False, 'reason': e})

    return json.dumps({'status': True, 'href': file.filename})


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

    return Utils.convert_dataframe_to_dict({
        'source': Utils.get_source_table(file_name),
        'normalized': Utils.get_normalized_table(file_name),
        'statistic': Utils.get_statistic_table(file_name),
        'chi_square': Utils.get_chi_square_table(file_name)
    }[table_type])


def main():
    app.run()


if __name__ == '__main__':
    main()
