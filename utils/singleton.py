"""
@author: Kevin Xu
@license: (C) Copyright 2021-2025, Boston Scientific Corporation Limited.
@contact: xuf@bsci.com
@software: BSC_EME_TAF
@file: singleton.py
@time: 2023/3/25 20:34
@desc:
"""


class Singleton(type):
    _instances = {}

    def __call__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__call__(
                *args, **kwargs
            )
        return class_._instances[class_]
