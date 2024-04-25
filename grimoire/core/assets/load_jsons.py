import json
from glob import glob
from typing import Any


def load_jsons(directory_path: str) -> list[dict]:
    names = glob(f"{directory_path}/**/*.json", recursive=True)

    jsons = []

    for name in names:
        with open(name, "r") as file:
            data = json.load(file)
            jsons.append(data)

    return jsons


# FIXME: Unused function
def load_objects(directory_path: str, cls) -> list[Any]:
    objects = []

    for json in load_jsons(directory_path):
        obj = cls.construct(**json)

        if obj is not None:
            objects.append(obj)

    return objects
