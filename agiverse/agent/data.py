import os
import json
from datetime import datetime, timedelta

class DataTypes:
    MODEL_RESPONSE = 'model_response'
    SERVER_MESSAGE = 'server_message'
    SYSTEM_MESSAGE = 'system_message'

def save_data(data_dir, name, data_type, data):
    os.makedirs(data_dir, exist_ok=True)
    with open(f'{data_dir}/{name}.jsonl', 'a') as f:
        json.dump({
            'type': data_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        }, f)
        f.write('\n')

def load_data(data_dir, name, data_type=None, since=None, max_responses=None):
    with open(f'{data_dir}/{name}.jsonl', 'r') as f:
        data = [json.loads(line) for line in f if line.strip()]
    
    if data_type is not None:
        data = [d for d in data if d['type'] == data_type]
    
    if since is not None:
        if isinstance(since, (int, float)):
            since_dt = datetime.now() - timedelta(hours=since)
        elif isinstance(since, str):
            since_dt = datetime.fromisoformat(since)
        else:
            since_dt = since
        data = [d for d in data if datetime.fromisoformat(d['timestamp']) >= since_dt]
    
    if max_responses is not None:
        data = data[-max_responses:]

    return data