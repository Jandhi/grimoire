from data.asset import Asset
from data.asset_validation_state import AssetValidationState
from glob import glob
from utils.strings import camel_to_snake_case
import json
from colored import Style, Fore

from data.load_types import load_types
from data.link_assets import link_assets
from buildings.building_shape import permute_shapes
from os import walk

# Loads all nbt assets from the assets folder
def load_assets(root_directory) -> None:
    load_types()

    w = walk(root_directory)
    names = []

    for (dirpath, dirnmames, filenames) in w:
        for filename in filenames:
            if filename.endswith('.json'):
                pass
    for name in names:
        print(name)

        with open(name, 'r') as file:
            path = name.replace('\\', '/')
            data = json.load(file)

            if 'type' not in data:
                print(f'{Fore.red}Error{Style.reset}: could not load {path}. No type given.')
                continue

            cls = Asset.get_construction_type(data['type'])

            if cls is None:
                print(f"Could not find class {data['type']}")
                continue

            data['type'] = cls.type_name
            
            obj, validation_state = cls.construct_unsafe(**data)
            validation_state : AssetValidationState

            if validation_state.is_invalid():
                print(f'{Fore.red}Error{Style.reset}: while loading {Fore.light_blue}{path}{Style.reset}. Object is missing the following fields: {validation_state.missing_args}. It will be ignored.')
                continue

            if len(validation_state.surplus_args) > 0:
                print(f'{Fore.yellow}Warning{Style.reset}: while loading {Fore.light_blue}{path}{Style.reset}. Object has non-annotated fields: {validation_state.surplus_args}')

    link_assets()

    # Extra steps for special assets
    permute_shapes() # varies the building shapes into all rotations and mirrors