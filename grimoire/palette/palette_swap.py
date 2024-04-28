from grimoire.palette.palette import Palette

plurals = ["brick", "plank", "tile"]
woods = ["mangrove", "spruce", "oak", "dark_oak", "birch", "jungle", "acacia"]


def palette_swap(block_name: str, input_palette: Palette, output_palette: Palette):
    replacements = {
        getattr(input_palette, key): getattr(output_palette, key)
        for key in input_palette.fields
    }

    for target, result in replacements.items():
        if target in block_name:
            # Don't mistake dark_oak for oak
            if target == "oak" and "dark_oak" in block_name:
                continue

            new_val = block_name.replace(target, result)

            for plural in plurals:
                # remove plural for combo bricks
                if (
                    target.endswith(plural)
                    and block_name.endswith(f"{plural}s")
                    and not result.endswith(f"{plural}")
                ):
                    new_val = new_val.removesuffix("s")

                # No block ends in a plural without s
                if new_val.endswith(plural):
                    new_val = f"{new_val}s"

                # plank is not used in between words
                if "plank_" in new_val:
                    new_val = new_val.replace("plank_", "")

            return fix_block_name(new_val)

    return fix_block_name(block_name)


# This is used to make a block name consistent with the annoying inconsistencies minecraft has
def fix_block_name(name: str) -> str:
    for plural in plurals:
        if name.endswith(plural):
            name = f"{name}s"

    if "plank_" in name:
        name = name.replace("plank_", "")

    for plural in plurals:
        if f"{plural}s" in name and not name.endswith(f"{plural}s"):
            name = name.replace(f"{plural}s", plural)

    if "smooth_" in name and "wall" in name:
        name = name.replace("smooth_", "")

    if "wall" in name and any(wood in name for wood in woods):
        name = name.replace("wall", "fence")

    return name
