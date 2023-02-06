from data.asset import Asset
from data.asset_validation_state import AssetValidationState
from glob import glob
from utils.strings import camel_to_snake_case
import json
from colored import fg, attr

# Loading in the NBT type files is important for the default substitution
from building_generation.walls.wall_nbt import WallNBT 
from building_generation.roofs.roof_nbt import RoofNBT

# Loads all nbt assets from the assets folder
def load_assets(root_directory) -> None:
    names : list[str] = glob(root_directory + '/**/*.json', recursive=True) # glob allows us to get the subfolders too

    for name in names:
        with open(name, 'r') as file:
            path = name.replace('\\', '/')
            data = json.load(file)

            if 'type' not in data:
                print(f'{fg("red")}Error{attr(0)}: could not load {path}. No type given.')
                continue

            cls = Asset.get_construction_type(data['type'])
            data['type'] = cls.type_name
            
            obj, validation_state = cls.construct_unsafe(**data)
            validation_state : AssetValidationState

            if validation_state.is_invalid():
                print(f'{fg("red")}Error{attr(0)}: while loading {fg("light_blue")}{path}{attr(0)}. Object is missing the following fields: {validation_state.missing_args}. It will be ignored.')
                continue

            if len(validation_state.surplus_args) > 0:
                print(f'{fg("yellow")}Warning{attr(0)}: while loading {fg("light_blue")}{path}{attr(0)}. Object has non-annotated fields: {validation_state.surplus_args}')