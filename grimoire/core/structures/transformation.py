from gdpc.block import Block
from .legacy_directions import (
    X_PLUS,
    X_MINUS,
    Y_PLUS,
    Y_MINUS,
    Z_PLUS,
    Z_MINUS,
    from_text,
    to_text,
    RIGHT,
    DIRECTIONS,
)
from .structure import Structure
from .nbt.nbt_asset import NBTAsset
from gdpc.vector_tools import ivec3, rotate3D

# region Transformation dictionaries
x_mirror = {
    X_PLUS: X_MINUS,
    X_MINUS: X_PLUS,
    Y_PLUS: Y_PLUS,
    Y_MINUS: Y_MINUS,
    Z_PLUS: Z_PLUS,
    Z_MINUS: Z_MINUS,
}
y_mirror = {
    X_PLUS: X_PLUS,
    X_MINUS: X_MINUS,
    Y_PLUS: Y_MINUS,
    Y_MINUS: Y_PLUS,
    Z_PLUS: Z_PLUS,
    Z_MINUS: Z_MINUS,
}
z_mirror = {
    X_PLUS: X_PLUS,
    X_MINUS: X_MINUS,
    Y_PLUS: Y_PLUS,
    Y_MINUS: Y_MINUS,
    Z_PLUS: Z_MINUS,
    Z_MINUS: Z_PLUS,
}
mirror_dicts = (x_mirror, y_mirror, z_mirror)

diagonal_mirror = {
    X_PLUS: Z_PLUS,
    X_MINUS: Z_MINUS,
    Y_PLUS: Y_PLUS,
    Y_MINUS: Y_MINUS,
    Z_PLUS: X_PLUS,
    Z_MINUS: X_MINUS,
    "x": "z",
    "z": "x",
}
# endregion


# Class to house tranformations of landmarks, including mirroring and offsets
# Rotation is only supported by switching the x/z axis, in other words diagonal_mirror
class Transformation:
    def __init__(
        self,
        offset: ivec3 = None,
        rotations: int = 0,
        mirror: tuple[bool, bool, bool] = None,
        diagonal_mirror: bool = False,
    ) -> None:
        self.offset = offset or ivec3(0, 0, 0)
        self.mirror = mirror or (False, False, False)
        self.diagonal_mirror = diagonal_mirror
        self.rotations = rotations

    # Expects text to be in targets
    def apply_to_text(self, text: str) -> str:
        direction = from_text(text)

        # For each dimensinos
        for dim in range(3):
            if self.mirror[dim]:
                direction = mirror_dicts[dim][direction]

        if self.diagonal_mirror:
            direction = diagonal_mirror[direction]

        for i in range(self.rotations):
            direction = RIGHT[direction]

        return to_text(direction)

    def apply_to_palette(self, palette: list[Block]) -> list[Block]:
        return [self.apply_to_block(block) for block in palette]

    def apply_to_block(self, block: Block) -> Block:
        name = block.id
        properties = {}

        for prop_name, prop_value in block.states.items():
            direction_names = [to_text(direction) for direction in DIRECTIONS]

            if prop_name in direction_names:
                properties[self.apply_to_text(prop_name)] = prop_value
            elif prop_value in direction_names:
                properties[prop_name] = self.apply_to_text(prop_value)
            # For axes
            elif prop_value in ("x", "z") and (
                self.diagonal_mirror or self.rotations % 2 == 1
            ):
                properties[prop_name] = {"x": "z", "z": "x"}[prop_value]
            # For right and left
            elif prop_value in ("right", "left") and self.mirror[2]:
                properties[prop_name] = {"right": "left", "left": "right"}[prop_value]
            # Everything else
            else:
                properties[prop_name] = prop_value

        return Block(id=name, states=properties)

    def apply_to_point(
        self,
        point: ivec3,
        asset: NBTAsset,
    ) -> ivec3:

        point -= asset.origin

        if self.mirror[0]:  # x mirror
            point = ivec3(-1 * point.x, point.y, point.z)
        if self.mirror[2]:  # z mirror
            point = ivec3(point.x, point.y, -1 * point.z)

        if self.diagonal_mirror:
            point = ivec3(point.z, point.y, point.x)

        return rotate3D(point, self.rotations) + self.offset

    def apply_to_origin(self, point: ivec3) -> ivec3:
        origin = ivec3(*point)

        if self.mirror[0]:  # x mirror
            origin = ivec3(-1 * origin.x, origin.y, origin.z)
        if self.mirror[2]:  # z mirror
            origin = ivec3(origin.x, origin.y, -1 * origin.z)

        if self.diagonal_mirror:
            origin = ivec3(origin.z, origin.y, origin.x)

        return origin
