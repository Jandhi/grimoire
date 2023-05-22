from palette.palette import Palette

plurals = ['brick', 'plank']

def palette_swap(block_name : str, input_palette : Palette, output_palette : Palette):
    replacements = {
        getattr(input_palette, key) : getattr(output_palette, key) for key in input_palette.fields
    }
    
    for target, result in replacements.items():
        if target in block_name:
            # Don't mistake dark_oak for oak
            if target == 'oak' and 'dark_oak' in block_name:
                continue

            new_val = block_name.replace(target, result)

            for plural in plurals:
                # remove plural for combo bricks
                if target.endswith(plural) and block_name.endswith(f'{plural}s') and not result.endswith({plural}):
                    new_val = new_val.removesuffix('s') 

                # No block ends in a plural without s
                if new_val.endswith(plural):
                    new_val = f'{new_val}s'

            return new_val

    return block_name