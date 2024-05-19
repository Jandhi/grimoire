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

    primary_stone = "primary_stone"
    secondary_stone = "secondary_stone"

    primary_wood = "primary_wood"
    secondary_wood = "secondary_wood"


class ResolutionPriority:
    order: list[MaterialRole]

    def get_next_in_line(self, role: MaterialRole) -> MaterialRole | None:
        pass


class Palette(Asset):
    resolution_priority: ResolutionPriority
    materials: dict[MaterialRole, Material]

    # Colors
    primary_color: MinecraftColor
    secondary_color: MinecraftColor

    def find_role(self, block: Block) -> MaterialRole | None:
        for role in self.resolution_priority.order:
            if self.materials[role].has_block(block):
                return role

        return None

    def find_block_id(
        self,
        form: BlockForm,
        parameters: MaterialParameters,
        role: MaterialRole,
    ) -> str | None:
        while True:
            material = self.materials[role]

            block_id = material.get_id(form, parameters)

            if block_id is not None:
                return block_id

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
