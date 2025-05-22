import os
from catboost import CatBoostClassifier

def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально. Немного магии
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH

def load_models():
    model_path = get_model_path("src/best_model_14_05")
    model = CatBoostClassifier()
    model.load_model(model_path)
    return model

CAT_FEATURES = ['topic', 'country', 'exp_group', 'age_group']
