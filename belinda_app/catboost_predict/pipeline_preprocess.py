import pandas as pd
from ..catboost_predict.preprocessing import data_merge, clean_text, data_drop


def pipeline_preprocess(data: pd.DataFrame,
                        author_name: str,
                        album_name: str,
                        track_name: str) -> pd.DataFrame:
    """
    Пайплайн по предобработке данных
    :param data: датасет
    :param author_name: имя музыканта
    :param album_name: название альбома
    :param track_name: название трека
    :return: датасет
    """
    # data_merge
    author_name = author_name
    album_name = album_name
    track_name = track_name

    data = data_merge(data=data,
                      author_name=author_name,
                      album_name=album_name,
                      track_name=track_name,)

    # clean_text
    data["owner_name"] = data["owner_name"].apply(clean_text)
    data["description"] = data["description"].apply(clean_text)
    data["playlist_name"] = data["playlist_name"].apply(clean_text)
    data["author_name"] = data["author_name"].apply(clean_text)
    data["album_name"] = data["album_name"].apply(clean_text)
    data["track_name"] = data["track_name"].apply(clean_text)

    # data_drop
    #drop_columns = ["id"]
    #data = data_drop(data=data, drop_columns=drop_columns)

    return data
