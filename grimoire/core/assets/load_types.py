# PUT ALL TYPES HERE SO THAT THEY ARE LOADED


# IMPORTANT: DO NOT OPTIMIZE IMPORTS
def load_types():
    # WALLS
    from grimoire.buildings.walls.wall import Wall
    from grimoire.buildings.walls.wall_nbt import WallNBT
    from grimoire.buildings.walls.wall_blueprint import WallBlueprint

    _ = Wall, WallNBT, WallBlueprint

    # ROOFS
    from grimoire.buildings.roofs.roof import Roof
    from grimoire.buildings.roofs.roof_component import RoofComponent

    _ = Roof, RoofComponent

    # STYLES
    from grimoire.style.style import Style
    from grimoire.style.substyle import Substyle

    _ = Style, Substyle

    # ROOMS
    from grimoire.buildings.rooms.room import Room

    _ = Room

    # PALETTES
    from grimoire.palette.palette import Palette

    _ = Palette

    # BUILDING SHAPE
    from grimoire.buildings.building_shape import BuildingShape

    _ = BuildingShape

    # PAINT PALETTES
    from grimoire.districts.paint_palette import PaintPalette

    _ = PaintPalette

    # FORESTS
    from grimoire.terrain.forest import Forest

    _ = Forest

    # ASSET STRUCTURE
    from grimoire.core.structures.asset_structure import AssetStructure

    _ = AssetStructure
