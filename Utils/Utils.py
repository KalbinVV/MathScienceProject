import os.path
from functools import lru_cache

import numpy as np
import pandas as pd
from pandas.core.dtypes.common import is_string_dtype
from scipy.interpolate import make_interp_spline

from werkzeug.datastructures import FileStorage

from Configuration.Configuration import Configuration

import re

from Utils.FloatRange import FloatRange


class Utils:
    @classmethod
    def save_file(cls, file: FileStorage) -> str:
        folder_path = os.path.join('.', Configuration.folder_path)

        if not os.path.isdir(folder_path):
            os.mkdir(folder_path)

        file_name, file_type = cls.get_file_name_data(file.filename)

        if file_type != 'xlsx':
            raise Exception('Неверный формат файла!')

        count_of_files = cls.get_count_of_files_in_directory(folder_path)

        final_file_name = f'{count_of_files}.data'

        file_path = os.path.join(folder_path, final_file_name)

        file.save(file_path)

        return final_file_name

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

    @staticmethod
    def get_count_of_files_in_directory(dir_path: str) -> int:
        count = 0

        for path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1

        return count

    # Return information about file name and file type
    # Input: sample file.docx
    # Output: tuple(sample file, docx)
    @staticmethod
    def get_file_name_data(file_name: str) -> tuple:
        search_result = re.search(r'^(?P<file_name>.*)\.(?P<file_type>\w+)$', file_name)

        return search_result.group('file_name'), search_result.group('file_type')

    @staticmethod
    @lru_cache
    def get_charts_data(file_name: str, amount_of_intervals: int = 5) -> list:
        from MathScience.Tables.Tables import Tables
        data_frame = Tables.get_normalized_table(file_name)

        intervals = []

        for column in data_frame.columns:
            if is_string_dtype(data_frame[column]):
                continue

            min_value = data_frame[column].min()
            max_value = data_frame[column].max()

            interval_step = (max_value - min_value) / amount_of_intervals

            amount_data = []
            for i in range(amount_of_intervals):
                float_range = FloatRange(i * interval_step, (i + 1) * interval_step)

                amount = 0
                for value in data_frame[column]:
                    if value in float_range:
                        amount += 1

                amount_data.append(amount)

            x = np.linspace(0.0, 1.0, num=amount_of_intervals)

            interpolation_spline = make_interp_spline(x, amount_data)

            interpolated_x = np.linspace(x.min(), x.max(), 100)
            interpolated_y = interpolation_spline(interpolated_x)

            intervals.append([column, data_frame[column].to_numpy().tolist(), interpolated_x.tolist(), interpolated_y.tolist()])

        return intervals
