"""
Global placeholders for models and datasets used in recommendation system.

Variables:
- model_test (CatBoostClassifier | None): Test group CatBoost model.
- model_control (CatBoostClassifier | None): Control group CatBoost model.
- users_data (pd.DataFrame | None): DataFrame with user features.
- posts_data (pd.DataFrame | None): DataFrame with post features.
- top_5_posts_list (list | None): Precomputed list of top 5 posts for default recommendations.
"""

model_test = None
model_control = None
users_data = None
posts_data = None
top_5_posts_list = None
