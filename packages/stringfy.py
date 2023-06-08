from functools import wraps
import pandas as pd

def stringfyParams(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        args = tuple(convert_to_excel(arg) if not isinstance(arg, str) and is_valid_file(arg) else arg for arg in args)
        kwargs = {key: convert_to_excel(kwarg) if not isinstance(kwarg, str) and is_valid_file(kwarg) else kwarg
                  for key, kwarg in kwargs.items()}
        return func(*args, **kwargs)

    return wrapper

def is_valid_file(file_path):
    try:
        pd.ExcelFile(file_path)
        return True
    except Exception:
        return False

def convert_to_excel(file_path):
    if is_valid_file(file_path):
        return pd.ExcelFile(file_path)
    return file_path
