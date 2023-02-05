from data.asset import Asset
from data.asset_validation_state import AssetValidationState
from glob import glob
from utils.strings import camel_to_snake_case
import json
from colored import fg, attr

# Ensure you are loading all NBTAsset types here
from building_generation.walls.wall import Wall
from building_generation.roofs.roof import Roof
from building_generation.roofs.roof_component import RoofComponent

# Loads all nbt assets from the assets folder
def load_assets(root_directory) -> None:
    names : list[str] = glob(root_directory + '/**/*.json', recursive=True) # glob allows us to get the subfolders too

    for name in names:
        with open(name, 'r') as file:
            path = name.replace('\\', '/')
            data = json.load(file)

            if 'type' not in data:
                print(f'Could not load {path}. No type given.')
                continue

            cls = Asset.find_type(data['type'])
            
            obj, validation_state = cls.construct_unsafe(**data)
            validation_state : AssetValidationState

            if validation_state.is_invalid():
                print(f'{fg("red")}Error{attr(0)} while loading {fg("light_blue")}{path}{attr(0)}. Object is missing the following fields: {validation_state.missing_args}. It will be ignored.')
                continue

            print(f'{fg("yellow")}Warning{attr(0)} while loading {fg("light_blue")}{path}{attr(0)}. Object has non-annotated fields: {validation_state.surplus_args}')