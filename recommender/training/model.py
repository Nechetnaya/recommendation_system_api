import gc
import json
from catboost import CatBoostClassifier, Pool

from recommender.training.metrics import calculate_auc, calculate_hit_rate_by_user


def train_and_save_model(train_df, cat_features):
    X = train_df.drop(columns=['target'])
    y = train_df['target']

    train_size = int(0.7 * len(X))
    val_size = int(0.15 * len(X))

    X_train = X[:train_size]
    y_train = y[:train_size]

    X_val = X[train_size:train_size + val_size]
    y_val = y[train_size:train_size + val_size]

    X_test = X[train_size + val_size:]
    y_test = y[train_size + val_size:]

    del X, y
    gc.collect()

    train_pool = Pool(X_train, y_train, cat_features=cat_features)
    eval_pool = Pool(X_val, y_val, cat_features=cat_features)

    model = CatBoostClassifier(
        depth=6,
        iterations=900,
        learning_rate=0.05,
        verbose=100,
        loss_function='Logloss',
        eval_metric='AUC',
        thread_count=2,
        scale_pos_weight=8,
        early_stopping_rounds=50,
        l2_leaf_reg=5,
        random_strength=2,
        bagging_temperature=0.5
    )

    model.fit(train_pool, eval_set=eval_pool)

    auc = calculate_auc(model, X_test, y_test)
    hitrate = calculate_hit_rate_by_user(model, X_test, y_test, top_n=5)

    print(f"Test AUC: {auc:.4f}")
    print(f"Test HitRate@5: {hitrate:.4f}")

    model.save_model("models/model.cbm", format="cbm")

    with open("models/metrics.json", 'w') as f:
        json.dump({"AUC": auc, "HitRate@5": hitrate}, f, indent=4)

    print("Model and metrics saved.")
