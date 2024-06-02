from gdpc import Block, Editor
from glm import ivec3

editor = Editor(buffering=True)
build_area = editor.getBuildArea()
editor.placeBlock(ivec3(-55, -60, 8), Block("stone"))
