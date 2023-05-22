from gdpc.editor import Editor
from gdpc.vector_tools import ivec3
from structures.directions import north, east, west, south, get_ivec2, Direction, left, right, to_text, ivec2_to_dir, vector, cardinal, opposite, ivec3_to_dir

#uses set block to place entities (playerheads/armor stands)
def place_block(block: str, editor: Editor, point: ivec3, direction=None):
    actual_point = editor.transform.apply(point)
    #setting correct direction
    if direction == west:
        block = block[:11] + '[rotation=12]' + block[11:len(block)]
    elif direction == east:
        block = block[:11] + '[rotation=4]' + block[11:len(block)]
    elif direction == south:
        block = block[:11] + '[rotation=8]' + block[11:len(block)]
    command = f'setblock {actual_point.x} {actual_point.y} {actual_point.z} minecraft:{block} replace'
    editor.runCommand(command)