import os
import json

def load_jsons(directory_path : str) -> list[dict]:
    names = filter(lambda name : name.endswith('.json'), os.listdir(directory_path))

    jsons = []

    for name in names:
        path = f'{directory_path}/{name}'
        with open(path, 'r') as file:
            data = json.load(file)
            jsons.append(data)

    return jsons