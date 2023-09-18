import pandas as pd
import numpy as np
import re

from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

import joblib

import warnings
warnings.filterwarnings('ignore')


class Linereg:

    def __init__(self, follow: int, modelpath: str):
        """
        Создает все необходимые атрибуты для объекта Linereg
        :param follow: количество подписчиков
        :param modelpath: путь до модели
        """
        self.polyfeat = PolynomialFeatures(degree=3, include_bias=False)
        self.follow = follow
        self.modelpath = modelpath

    def __load(self) -> LinearRegression:
        """
        Загружает модель
        :return: LinearRegression
        """
        self.model = joblib.load(self.modelpath)
        return self.model

    def __poly(self) -> np.ndarray:
        """
        Создает полиномиальные признаки
        :return: np.ndarray
        """
        self.X_poly = self.polyfeat.fit_transform([[self.follow]])
        return self.X_poly

    def predict(self) -> np.ndarray:
        """
        Делает предсказание о среднем колличестве прослушиваний
        :return: np.ndarray
        """
        self.y_pred = self.__load().predict(self.__poly())
        return self.y_pred.round(0).astype('int64')
