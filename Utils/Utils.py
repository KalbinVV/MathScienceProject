import os.path

import pandas as pd

from werkzeug.datastructures import FileStorage

from Configuration.Configuration import Configuration

import re


class Utils:
    @classmethod
    def save_file(cls, file: FileStorage):
        folder_path = os.path.join('.', Configuration.folder_path)

        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)

        file_name, file_type = cls.get_file_name_data(file.filename)

        if file_type != 'xlsx':
            raise Exception('Неверный формат файла!')

        file_path = os.path.join(folder_path, file.filename)

        file.save(file_path)

        print(f'File saved: {file_path}')

    @staticmethod
    def load_file(file_name: str) -> pd.DataFrame:
        file_path = os.path.join(Configuration.folder_path, file_name)

        return pd.read_excel(file_path)

    @staticmethod
    def convert_dataframe_to_dict(data_frame: pd.DataFrame) -> dict:
        converted_dictionary = dict()

        converted_dictionary['columns'] = data_frame.columns.values.tolist()

        for column in data_frame.columns:
            converted_dictionary[column] = data_frame[column].values.tolist()
            converted_dictionary['size'] = int(data_frame[column].count())

        return converted_dictionary

    # Return information about file name and file type
    # Input: sample file.docx
    # Output: tuple(sample file, docx)
    @staticmethod
    def get_file_name_data(file_name: str) -> tuple:
        search_result = re.search(r'^(?P<file_name>.*)\.(?P<file_type>\w+)$', file_name)

        return search_result.group('file_name'), search_result.group('file_type')

