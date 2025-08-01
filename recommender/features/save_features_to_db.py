"""
Feature extraction and persistence module.

This script generates user and post features using the corresponding
feature engineering functions and saves them to a PostgreSQL database.

Functions:
- save_features_to_db(df, table_name): saves a DataFrame to a SQL table.
- main(): generates features and writes them to 'user_features' and 'post_features' tables.

Run this script directly to update feature tables in the database.
"""

from app.db.database import engine
from recommender.features.feature_engineering import make_user_features, make_post_features

def save_features_to_db(df, table_name):
    df.to_sql(table_name, con=engine, schema="public", if_exists="replace", index=False)
    print(f"Features saved to table '{table_name}' ({len(df)} rows).")



def main():
    user_features = make_user_features()
    post_features = make_post_features()

    save_features_to_db(user_features, "user_features")
    save_features_to_db(post_features, "post_features")

if __name__ == "__main__":
    main()
