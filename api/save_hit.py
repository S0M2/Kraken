import requests
import json
import logging

def save_to_db(module_name, target, username, password):
    url = "http://127.0.0.1:8000/api/results"
    data = {
        "module": module_name,
        "target": target,
        "username": username,
        "password": password
    }
    try:
        requests.post(url, json=data, timeout=2)
    except Exception as e:
        logging.error(f"Failed to save hit to database: {e}")
