import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib

recommendations = pd.read_csv("ab_test/views.csv")
likes = pd.read_csv("ab_test/likes.csv")

# Очистка пересекающихся пользователей
multi_group_users = (
    recommendations.groupby('user_id', as_index=False)['exp_group']
    .nunique().query("exp_group > 1")
)
recommendations = recommendations[~recommendations.user_id.isin(multi_group_users.user_id)]

# Проверка SRM
from scipy.stats import chi2_contingency
observed = recommendations.groupby('exp_group').user_id.nunique().to_list()
total = sum(observed)
expected = [total / 2, total / 2]
chi2, p_srm, _, _ = chi2_contingency([observed, expected])

# Дополнительные метрики
users = recommendations.user_id.unique()
users_test = recommendations[recommendations['exp_group'] == 'test'].user_id.unique()
users_control = recommendations[recommendations['exp_group'] == 'control'].user_id.unique()

likes_filtered = likes[likes.user_id.isin(users)]

# Доля пользователей с лайками
users_likes_test = likes_filtered[likes_filtered.user_id.isin(users_test)].user_id.nunique()
users_likes_control = likes_filtered[likes_filtered.user_id.isin(users_control)].user_id.nunique()

share_test = users_likes_test / len(users_test)
share_control = users_likes_control / len(users_control)

# Z-тест для пропорций
successes = [users_likes_test, users_likes_control]
n_obs = [len(users_test), len(users_control)]
z_stat, p_share = proportions_ztest(count=successes, nobs=n_obs)

# Лайки на пользователя
likes_per_user_test = likes_filtered[likes_filtered.user_id.isin(users_test)].groupby('user_id')['post_id'].count()
likes_per_user_control = likes_filtered[likes_filtered.user_id.isin(users_control)].groupby('user_id')['post_id'].count()

mw_stat, p_mw = mannwhitneyu(likes_per_user_test, likes_per_user_control, alternative='two-sided')

# Hitrate по рекомендациям (в течение 1 часа после показа)
recommendations['recommendations'] = recommendations['recommendations'].apply(lambda x: list(map(int, x.strip('[]').split())))
recommendations['timestamp'] = pd.to_datetime(recommendations['timestamp'], unit='s')
recs_exploded = recommendations.explode('recommendations').rename(columns={'recommendations': 'post_id', 'timestamp': 'timestamp_view'})
likes['timestamp'] = pd.to_datetime(likes['timestamp'], unit='s')

views_likes = recs_exploded.merge(likes, on=['user_id', 'post_id'], how='left')
views_likes['time_before_like'] = views_likes['timestamp_y'] - views_likes['timestamp_view']
views_likes['is_like'] = ((views_likes['time_before_like'] >= pd.Timedelta(0)) & (views_likes['time_before_like'] < pd.Timedelta(hours=1))).astype(int)

views_likes['show_number'] = views_likes.groupby('user_id').cumcount()
exp_likes = views_likes.groupby(['user_id', 'exp_group', 'show_number'], as_index=False).agg(has_like=('is_like', 'max'))

# Bucket-тест
N_BUCKETS = 100

def user_to_bucket(user_id, n_buckets=N_BUCKETS, salt="my_salt"):
    s = f"{user_id}_{salt}"
    h = hashlib.md5(s.encode('utf-8')).digest()
    h_int = int.from_bytes(h[:4], byteorder='big')
    return h_int % n_buckets

exp_likes['bucket'] = exp_likes['user_id'].apply(lambda uid: user_to_bucket(uid))

bucket_stats = exp_likes.groupby(['exp_group', 'bucket'], as_index=False).agg(
    likes=('has_like', 'sum'),
    impressions=('has_like', 'count')
)
bucket_stats['hitrate'] = bucket_stats['likes'] / bucket_stats['impressions']

hitrate_test_avg = bucket_stats[bucket_stats.exp_group == 'test']['hitrate'].mean()
hitrate_control_avg = bucket_stats[bucket_stats.exp_group == 'control']['hitrate'].mean()
test_buckets = bucket_stats[bucket_stats.exp_group == 'test']['hitrate']
control_buckets = bucket_stats[bucket_stats.exp_group == 'control']['hitrate']
t_stat, p_hitrate = ttest_ind(test_buckets, control_buckets, equal_var=False)


# Вывод результатов
print("SRM p-value:", round(p_srm, 5))
print(f"Share of users with likes — Test: {share_test:.4f}, Control: {share_control:.4f}, p-value: {p_share:.5f}")
print(f"Likes per user — MW p-value: {p_mw:.5f}")
print(f"Hitrate buckets — Test: {test_buckets.mean():.4f}, Control: {control_buckets.mean():.4f}, p-value: {p_hitrate:.10f}")
