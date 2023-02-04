from data.asset import Asset, AssetError
from glob import glob
from utils.strings import camel_to_snake_case
import json

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
            
            try:
                obj = cls.construct(**data)
            except AssetError as error:
                
                print(f'Error while loading {path}. {error}')
            