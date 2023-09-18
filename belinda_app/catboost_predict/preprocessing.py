import pandas as pd
import re

import warnings
warnings.filterwarnings("ignore")


def data_merge(data: pd.DataFrame,
               author_name: str,
               album_name: str,
               track_name: str) -> pd.DataFrame:
    """
    Формирует датасет
    :param data:
    :param author_name: имя музыканта
    :param album_name: название альбома
    :param track_name: название трека
    :return: датасет
    """
    data.insert(0, "author_name", author_name)
    data.insert(1, "album_name", album_name)
    data.insert(2, "track_name", track_name)

    return data


def clean_text(data: pd.Series) -> pd.Series:
    """
    Чистит текст
    """
    data = data.lower()
    data = re.sub(r"[^\sa-zA-Z0-9@\[\]]"," ",data) # удаляет пунктцацию
    data = re.sub(r"\w*\d+\w*", "", data) # удаляет цифры
    data = re.sub(r"[^\w\s]", " ", data) # удаляет знаки
    data = re.sub("\s{2,}", " ", data) # удаляет ненужные пробелы

    return data


def data_drop(data: pd.DataFrame, drop_columns: list) -> pd.DataFrame:
    """
    Удаляет признаки
    :param data: датасет
    :param drop_columns: список с признаками
    :return: датасет
    """
    return data.drop(columns=drop_columns, axis=1)
