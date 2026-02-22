import os

def check_file_exists(file_path):
    return os.path.isfile(file_path)

def load_file_lines(file_path):
    if check_file_exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]
    return []
