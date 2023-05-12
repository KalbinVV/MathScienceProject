import signal
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import Flask, render_template, request

import requests
from Configuration.Configuration import Configuration
from Utils.Utils import Utils

app = Flask(__name__, static_folder='web/static', template_folder='web/templates')

app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MegaBytes


def index():
    language_configuration = Configuration.language

    return render_template('index.html',
                           title=language_configuration['title'],
                           subtitle=language_configuration['subtitle'],
                           footer=language_configuration['footer'])


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


# Timeout in ms
def create_anti_ddos_wrapper(timeout: int):
    dictionary_of_visited = dict()

    def wrapper(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            ip_address = request.remote_addr

            current_time = datetime.now(timezone.utc)

            if ip_address in dictionary_of_visited:
                previous_time = dictionary_of_visited[ip_address]

                if current_time <= previous_time + timedelta(milliseconds=timeout):
                    return Utils.generate_error_response('AntiDDOS handler')

            dictionary_of_visited[ip_address] = current_time

            return function(*args, **kwargs)

        return wrapped_function

    return wrapper


# Stop request if function work too long
# Don't work (Kill main process)
def create_timeout_wrapper(timeout: int):
    def wrapper(function):
        @wraps(function)
        def wrapped_function(*args, **kwargs):
            try:
                signal.alarm(timeout)
                result = function(*args, **kwargs)
                signal.alarm(0)

                return result
            except (Exception, ) as e:
                return Utils.generate_error_response('Timeout handler')

        return wrapped_function

    return wrapper


def main():
    # 0.5 s timeout
    anti_ddos_wrapper = create_anti_ddos_wrapper(timeout=500)

    # 2 s timeout
    timeout_wrapper = create_timeout_wrapper(timeout=2)

    app.add_url_rule('/', view_func=anti_ddos_wrapper(index), methods=['GET'])
    app.add_url_rule('/reports/<file_name>', view_func=anti_ddos_wrapper(report_view), methods=['GET'])

    app.add_url_rule('/upload_report', view_func=anti_ddos_wrapper(requests.upload_report), methods=['POST'])
    app.add_url_rule('/get_table', view_func=anti_ddos_wrapper(requests.get_table), methods=['GET'])
    app.add_url_rule('/get_intervals', view_func=anti_ddos_wrapper(requests.get_intervals), methods=['GET'])

    app.run()


if __name__ == '__main__':
    main()
