import yaml
from yaml.loader import SafeLoader


class LanguageConfiguration:
    def __init__(self, file_name):
        with open(f'./Configuration/Language/{file_name}', 'r', encoding='utf8') as file:
            self.__data = yaml.load(file, Loader=SafeLoader)

    def __getitem__(self, item):
        return self.__data[item]
