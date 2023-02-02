import os
import json
from glob import glob
from structures.nbt_asset import NBTAsset

def load_jsons(directory_path : str) -> list[dict]:
    names = glob(directory_path + '/**/*.json', recursive=True) # glob allows us to get the subfolders too

    jsons = []

    for name in names:
        with open(name, 'r') as file:
            data = json.load(file)
            jsons.append(data)

    return jsons

def load_objects(directory_path : str, cls : type) -> list[any]:
    objects = []

    for json in load_jsons(directory_path):
        objects.append(construct_object(json, cls))
    
    return objects

def construct_object(json_data : dict, cls : type):
    obj : NBTAsset = cls()

    for key, val in json_data.items():
        obj.__setattr__(key, val)

    obj.on_construct()
    
    return obj