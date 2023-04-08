class FloatRange:
    def __init__(self, start, end):
        self.__start = start
        self.__end = end

    def __contains__(self, item):
        return self.__start <= item <= self.__end

    def __str__(self):
        return f'{self.__start} <= x <= {self.__end}'
