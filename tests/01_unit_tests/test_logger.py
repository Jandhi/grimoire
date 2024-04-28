from unittest.mock import Mock

import pytest
from gdpc import Block, Editor
from gdpc.lookup import FOLIAGE, TREE_BLOCKS
from gdpc.vector_tools import Box
from gdpc.world_slice import WorldSlice

from grimoire.terrain.logger import erode

EDITOR_MOCK = Mock(spec=Editor)

WORLD_SLICE_MOCK = Mock(WorldSlice)
"""
Mock WorldSlice (4x255x4)

~: Water
C: Sugar cane
G: Grass
L: Leaves
S: Sand
W: Wood

WORLD_SURFACE
 ~~CG  64, 64, 67, 65
 ~~LL  64, 64, 70, 70
 ~LLL  64, 70, 70, 72
 GLLL  66, 70, 71, 72

OCEAN_FLOOR
 SSCG  62, 63, 67, 65
 SSLL  61, 62, 70, 70
 SLLL  63, 70, 70, 72
 GLLL  66, 70, 71, 72

MOTION_BLOCKING
 SSGG  62, 63, 64, 65
 SSLL  61, 62, 70, 70
 SLLL  63, 70, 70, 72
 GLLL  66, 70, 71, 72

MOTION_BLOCKING_NO_LEAVES
 SSGG  62, 63, 64, 65
 SSSG  61, 62, 63, 64
 SSSG  63, 63, 63, 64
 GGGW  66, 65, 64, 71
"""
WORLD_SLICE_MOCK.heightmaps = {
    "WORLD_SURFACE": [
        [64, 64, 67, 65],
        [64, 64, 70, 70],
        [64, 70, 70, 72],
        [66, 70, 71, 72],
    ],
    "OCEAN_FLOOR": [
        [62, 63, 67, 65],
        [61, 62, 70, 70],
        [63, 70, 70, 72],
        [66, 70, 71, 72],
    ],
    "MOTION_BLOCKING": [
        [62, 63, 64, 65],
        [61, 62, 70, 70],
        [63, 70, 70, 72],
        [66, 70, 71, 72],
    ],
    "MOTION_BLOCKING_NO_LEAVES": [
        [62, 63, 64, 65],
        [61, 62, 63, 64],
        [63, 63, 63, 64],
        [66, 65, 64, 71],
    ],
}
WORLD_SLICE_MOCK.yBegin
WORLD_SLICE_MOCK.box = Box(size=(4, 255, 2))
WORLD_SLICE_MOCK.getBlock.return_value  # TODO: Mock getBlock


@pytest.mark.parametrize(
    "world_slice, heightmap, to_replace, to_skip, stop_at, max_depth, expected_affected, test_id,",
    [
        # Happy path tests
        ## Removing whole trees
        (
            WORLD_SLICE_MOCK,
            "MOTION_BLOCKING",
            TREE_BLOCKS | FOLIAGE,
            "minecraft:air",
            None,
            None,
            Block("minecraft:air"),
            {
                (1, 2): 1,
                (1, 3): 1,
                (2, 1): 1,
                (2, 2): 1,
                (2, 3): 3,
                (3, 1): 1,
                (3, 2): 3,
                (3, 3): 7,
            },
            "happy_path_full_tree",
        ),
        ## Removing tree trunks
        (
            WORLD_SLICE_MOCK,
            "MOTION_BLOCKING_NO_LEAVES",
            TREE_BLOCKS,
            "minecraft:air",
            None,
            None,
            Block("minecraft:air"),
            {(3, 3): 6},
            "happy_path_full_tree",
        ),
        ## Removing water
        ## Exposing stone
        # Edge cases
        (
            WORLD_SLICE_MOCK,
            "WORLD_SURFACE",
            [Block("minecraft:dirt")],
            [Block("minecraft:sand"), Block("minecraft:gravel")],
            {(1, 1)},
            "edge_case_replace_with_sequence",
        ),
        (
            WORLD_SLICE_MOCK,
            "WORLD_SURFACE",
            [Block("minecraft:dirt")],
            Block("minecraft:air"),
            set(),
            "edge_case_no_replacement",
        ),
        # Error cases
        (
            WORLD_SLICE_MOCK,
            "INVALID_HEIGHTMAP",
            [Block("minecraft:dirt")],
            Block("minecraft:air"),
            ValueError,
            "error_invalid_heightmap",
        ),
    ],
)
def test_erode(
    world_slice,
    heightmap,
    to_replace,
    to_skip,
    stop_at,
    max_depth,
    expected_affected,
    test_id,
) -> None:
    """Unit tests for the `erode()` function

    Arguments that need testing:
        editor -- (Not required)
        world_slice -- different y-ranges (0, negative, positive)
        heightmap -- Check starting point; invalidity
        to_replace -- (Not required)
        to_skip -- None behaviour
        stop_at -- None behaviour
        max_depth -- Check correct depth and not out-of-bounds; non-positive val
        replace_with -- (Not required)
        expected_affected -- Set of affected coordinates OR exception values
        test_id -- Name of test
    """
    # Arrange

    # Act and Assert
    if isinstance(expected_affected, set):
        affected = erode(
            editor=EDITOR_MOCK,
            world_slice=WORLD_SLICE_MOCK,
            heightmap=heightmap,
            to_replace=to_replace,
            to_skip=to_skip,
            stop_at=stop_at,
            max_depth=max_depth,
            replace_with="minecraft:air",
        )
        assert affected == expected_affected, f"Test ID: {test_id}"
    else:
        with pytest.raises(expected_affected, match=".*not a valid heightmap.*"):
            erode(
                editor=EDITOR_MOCK,
                world_slice=WORLD_SLICE_MOCK,
                heightmap=heightmap,
                to_replace=to_replace,
                to_skip=to_skip,
                stop_at=stop_at,
                max_depth=max_depth,
                replace_with="minecraft:air",
            )
