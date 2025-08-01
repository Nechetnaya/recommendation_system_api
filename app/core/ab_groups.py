"""
This module defines the logic for assigning users to experimental groups.

Function:
- get_exp_group: Deterministically assigns a user to either 'control' or 'test' group
  based on a hash of their user ID and a salt value.

Details:
- Uses MD5 hashing for consistent bucketing.
- Ensures ~50/50 distribution between control and test groups.
- The salt can be changed to manage different experiments.

Example:
>>> get_exp_group(123)
'test'
"""

import hashlib


def get_exp_group(user_id: int, salt: str = "experiment_1") -> str:
    key = f"{salt}_{user_id}"
    hash_val = hashlib.md5(key.encode()).hexdigest()
    num = int(hash_val[:8], 16) / 0xFFFFFFFF
    return "control" if num < 0.5 else "test"
