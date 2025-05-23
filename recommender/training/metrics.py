import pandas as pd
from sklearn.metrics import roc_auc_score

# ROC AUC
def calculate_auc(model, X_test, y_test):
    y_pred = model.predict_proba(X_test)[:, 1]
    score = roc_auc_score(y_test, y_pred)
    return score

# HitRate@N
def calculate_hit_rate_by_user(model, X_test, y_test, top_n=5):
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    X_test = X_test.reset_index()
    y_test = y_test.reset_index(drop=True)

    results = pd.DataFrame({
        'user_id': X_test['user_id'],
        'y_true': y_test,
        'y_pred': y_pred_proba
    })

    hit_rate_by_user = (
        results.groupby('user_id')
        .apply(lambda group: (group.sort_values('y_pred', ascending=False).iloc[:top_n]['y_true'] == 1).any())
        .mean()
    )

    return hit_rate_by_user
