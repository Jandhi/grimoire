import os
import json
from types import SimpleNamespace

def load_jsons(directory_path : str) -> list[dict]:
    names = filter(lambda name : name.endswith('.json'), os.listdir(directory_path))

    jsons = []

    for name in names:
        path = f'{directory_path}/{name}'
        with open(path, 'r') as file:
            data = json.load(file)
            jsons.append(data)

    return jsons

def load_jsons_as_objects(directory_path : str, cls : type) -> list[any]:
    objects = []

    for json in load_jsons(directory_path):
        obj : object = cls()

        for key, val in json.items():
            obj.__setattr__(key, val)

        objects.append(obj)
    
    return objects