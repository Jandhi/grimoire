from palette.palette import Palette

def palette_swap(block_name : str, input_palette : Palette, output_palette : Palette):
    replacements = {
        getattr(input_palette, key) : getattr(output_palette, key) for key in input_palette.__dict__
    }
    
    for target, result in replacements.items():
        if target in block_name:
            # Don't mistake dark_oak for oak
            if target == 'oak' and 'dark_oak' in block_name:
                continue

            new_val = block_name.replace(target, result)

            # remove bricks plural for standalone bricks
            if target.endswith('brick') and block_name.endswith('bricks') and not result.endswith('brick'):
                new_val = new_val.removesuffix('s') 

            # No block ends in 'brick', they end in 'bricks' on their own
            if new_val.endswith('brick'):
                new_val = f'{new_val}s'

            return new_val

    return block_name