import pandas as pd
import re
import joblib

from catboost import CatBoostRanker, Pool

import warnings
warnings.filterwarnings("ignore")


def evaluate(data: pd.DataFrame) -> pd.DataFrame:
    """
    Делает предсказание
    :param: датасет
    :return: датасет с предсказанием
    """
    model = joblib.load("./belinda_app/catboost_predict/clf_final.joblib")

    cat_features = [0, 1, 2, 4, 5]
    text_features = [3]

    data_pool = Pool(data=data,
                     cat_features=cat_features,
                     text_features=text_features)

    data["predict"] = model.predict(data_pool)

    return data


def pred_playlist(data: pd.DataFrame, top: int) -> list:
    """
    Формирует список топ релевантных плейлистов
    :param data: датасет
    :param top: число топ релевантных плейлистов
    :return: список
    """
    data.sort_values("predict", ascending=False, inplace=True)
    data[["name", "predict"]].head(top)
    top_playlist_lst = data["name"].head(top).tolist()

    return top_playlist_lst
