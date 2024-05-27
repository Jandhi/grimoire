from enum import Enum

from gdpc import Block

from grimoire.core.assets.asset import Asset
from grimoire.core.styling.blockform import BlockForm
from grimoire.core.styling.colors import MinecraftColor
from grimoire.core.styling.materials.dithering import DitheringPattern
from grimoire.core.styling.materials.material import Material, MaterialParameters


class MaterialRole(Enum):
    primary_wall = "primary_wall"
    secondary_wall = "secondary_wall"

    primary_roof = "primary_roof"
    secondary_roof = "secondary_roof"

    primary_stone = "primary_stone"
    secondary_stone = "secondary_stone"

    primary_wood = "primary_wood"
    secondary_wood = "secondary_wood"

    pillar = "pillar"


class _ResolutionPriority:
    order: list[MaterialRole]
    next_in_line: dict[MaterialRole, MaterialRole]

    def __init__(
        self, order: list[MaterialRole], next_in_line: dict[MaterialRole, MaterialRole]
    ):
        self.order = order
        self.next_in_line = next_in_line

    def get_next_in_line(self, role: MaterialRole) -> MaterialRole | None:
        if role in self.next_in_line:
            return self.next_in_line[role]

        return None


class ResolutionPriority(Enum):
    stone = _ResolutionPriority(
        order=[
            MaterialRole.pillar,
            MaterialRole.primary_wall,
            MaterialRole.secondary_wall,
            MaterialRole.primary_roof,
            MaterialRole.secondary_roof,
            MaterialRole.primary_stone,
            MaterialRole.secondary_stone,
            MaterialRole.primary_wood,
            MaterialRole.secondary_wood,
        ],
        next_in_line={
            MaterialRole.primary_wall: MaterialRole.primary_stone,
            MaterialRole.secondary_wall: MaterialRole.secondary_stone,
            MaterialRole.primary_roof: MaterialRole.primary_stone,
            MaterialRole.secondary_roof: MaterialRole.secondary_stone,
            MaterialRole.primary_stone: MaterialRole.primary_wood,
            MaterialRole.secondary_stone: MaterialRole.secondary_wood,
            MaterialRole.primary_wood: MaterialRole.primary_stone,
            MaterialRole.secondary_wood: MaterialRole.secondary_stone,
            MaterialRole.pillar: MaterialRole.primary_stone,
        },
    )

    def order(self) -> list[MaterialRole]:
        return self.value.order

    def get_next_in_line(self, role: MaterialRole) -> MaterialRole | None:
        return self.value.get_next_in_line(role)


class Palette(Asset):
    resolution_priority: ResolutionPriority
    materials: dict[MaterialRole, Material]

    # Colors
    primary_color: MinecraftColor
    secondary_color: MinecraftColor

    def find_role(self, block: Block) -> MaterialRole | None:
        for role in self.resolution_priority.order():
            if role in self.materials and self.materials[role].has_block(block):
                return role

        return None

    def find_block_id(
        self,
        form: BlockForm,
        parameters: MaterialParameters,
        role: MaterialRole,
    ) -> str | None:
        checked_roles = set()

        while True:
            if role not in self.materials.keys():
                return None

            material = self.materials[role]

            block_id = material.get_id(form, parameters)

            if block_id is not None:
                return block_id

            # Already checked this role before, in cycle
            if role in checked_roles:
                return None
            checked_roles.add(role)

            # Block not found in this role, check next
            role = self.resolution_priority.get_next_in_line(role)

            # End of the line, block not swappable
            if role is None:
                return None


# In short:
#   - Find the role of the block in the input palette
#   - Find the form of the block
#   - Find the id of the block in the new palette of that same role and form
#   - If any of these fail, return the same block
def swap(
    block: Block,
    input_palette: Palette,
    output_palette: Palette,
    parameters: MaterialParameters,
) -> Block:
    role = input_palette.find_role(block)

    if role is None:
        return block

    form = BlockForm.get_form(block)

    new_id = output_palette.find_block_id(form, parameters, role)

    if new_id is None:
        return block

    return Block(id=new_id, states=block.states, data=block.data)
