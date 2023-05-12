import pandas as pd


def get_sample_size(x: pd.DataFrame) -> float:
    import statistics
    return (2 * 2 * statistics.variance(x) * 100) / (
            2 * 2 * statistics.variance(x) + (
            2 * (((statistics.variance(x)) / 15 * (1 - 15 / 100)) ** 0.5)) ** 2 * 100)
