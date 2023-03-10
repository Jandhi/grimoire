# PUT ALL TYPES HERE SO THAT THEY ARE LOADED

def load_types():
    # WALLS
    from building_generation.walls.wall import Wall
    from building_generation.walls.wall_nbt import WallNBT 
    from building_generation.walls.wall_blueprint import WallBlueprint 

    # ROOFS
    from building_generation.roofs.roof import Roof
    from building_generation.roofs.roof_component import RoofComponent

    # STYLES
    from style.style import Style
    from style.substyle import Substyle

    # ROOMS
    from building_generation.rooms.room import Room

    # PALETTES
    from palette.palette import Palette