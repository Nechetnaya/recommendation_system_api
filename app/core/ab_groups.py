import hashlib


def get_exp_group(user_id: int, salt: str = "experiment_1") -> str:
    key = f"{salt}_{user_id}"
    hash_val = hashlib.md5(key.encode()).hexdigest()
    num = int(hash_val[:8], 16) / 0xFFFFFFFF
    return "control" if num < 0.5 else "test"
