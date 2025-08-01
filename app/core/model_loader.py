"""
This module handles loading of pre-trained CatBoost models for use in recommendations
or predictions. It supports loading different models depending on the execution environment
(local or LMS).

Functions:

- get_model_path() -> List[str]:
    Determines and returns the file paths for the test and control models.
    If the code is running in the LMS environment (`IS_LMS=1`), LMS-specific paths are used.
    Otherwise, default local paths are returned.

- load_models():
    Loads and returns two CatBoostClassifier models (test and control) from disk using the paths
    obtained from `get_model_path()`.

Returns:
    Tuple[CatBoostClassifier, CatBoostClassifier]: test model and control model.
"""

import os
from typing import List

from catboost import CatBoostClassifier


def get_model_path() -> List[str]:
    if os.environ.get("IS_LMS") == "1":
        MODEL_PATH_TEST = '/workdir/user_input/model_test'
        MODEL_PATH_CONTROL = '/workdir/user_input/model_control'
    else:
        MODEL_PATH_TEST = "models/best_catboost_model_16_7.cbm"
        MODEL_PATH_CONTROL = "models/best_catboost_model_16_7.cbm"
    return [MODEL_PATH_TEST, MODEL_PATH_CONTROL]


def load_models():
    model_path = get_model_path()
    model_test = CatBoostClassifier()
    model_control = CatBoostClassifier()
    model_test.load_model(model_path[0])
    model_control.load_model(model_path[1])
    return model_test, model_control
