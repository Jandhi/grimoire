from data.asset import Asset
from data.asset_validation_state import AssetValidationState
from glob import glob
from utils.strings import camel_to_snake_case
import json
from colored import fg, attr

from data.load_types import load_types
from data.link_assets import link_assets

# Loads all nbt assets from the assets folder
def load_assets(root_directory) -> None:
    load_types()

    names : list[str] = glob(root_directory + '/**/*.json', recursive=True) # glob allows us to get the subfolders too

    for name in names:
        with open(name, 'r') as file:
            path = name.replace('\\', '/')
            data = json.load(file)

            if 'type' not in data:
                print(f'{fg("red")}Error{attr(0)}: could not load {path}. No type given.')
                continue

            cls = Asset.get_construction_type(data['type'])

            if cls is None:
                print(f"Could not find class {data['type']}")
                continue

            data['type'] = cls.type_name
            
            obj, validation_state = cls.construct_unsafe(**data)
            validation_state : AssetValidationState

            if validation_state.is_invalid():
                print(f'{fg("red")}Error{attr(0)}: while loading {fg("light_blue")}{path}{attr(0)}. Object is missing the following fields: {validation_state.missing_args}. It will be ignored.')
                continue

            if len(validation_state.surplus_args) > 0:
                print(f'{fg("yellow")}Warning{attr(0)}: while loading {fg("light_blue")}{path}{attr(0)}. Object has non-annotated fields: {validation_state.surplus_args}')

    link_assets()