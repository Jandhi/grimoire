from unittest.mock import Mock

import pytest
from gdpc import Block, Editor
from gdpc.world_slice import WorldSlice

from grimoire.terrain.logger import erode


@pytest.mark.parametrize(
    "world_slice, heightmap, to_replace, to_skip, stop_at, max_depth, expected_affected, test_id,",
    [
        # Happy path tests
        (
            "WORLD_SURFACE",
            [Block("minecraft:dirt")],
            Block("minecraft:air"),
            {(1, 1), (2, 2)},
            "happy_path_single_block",
        ),
        (
            "WORLD_SURFACE",
            [Block("minecraft:dirt"), Block("minecraft:grass")],
            Block("minecraft:air"),
            {(1, 1), (2, 2), (3, 3)},
            "happy_path_multiple_blocks",
        ),
        # Edge cases
        (
            "WORLD_SURFACE",
            [Block("minecraft:dirt")],
            [Block("minecraft:sand"), Block("minecraft:gravel")],
            {(1, 1)},
            "edge_case_replace_with_sequence",
        ),
        (
            "WORLD_SURFACE",
            [Block("minecraft:dirt")],
            Block("minecraft:air"),
            set(),
            "edge_case_no_replacement",
        ),
        # Error cases
        (
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
    """_summary_

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
    editor_mock = Mock(spec=Editor)
    world_slice_mock = Mock(spec=WorldSlice)
    world_slice_mock.heightmaps = {"WORLD_SURFACE": [[1, 2], [2, 3]]}
    world_slice_mock.box.size.x = range(2)
    world_slice_mock.box.size.z = range(2)
    world_slice_mock.getBlock.return_value.id = "minecraft:dirt"

    # Act and Assert
    if isinstance(expected_affected, set):
        affected = erode(
            editor=editor_mock,
            world_slice=world_slice_mock,
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
                editor=editor_mock,
                world_slice=world_slice_mock,
                heightmap=heightmap,
                to_replace=to_replace,
                to_skip=to_skip,
                stop_at=stop_at,
                max_depth=max_depth,
                replace_with="minecraft:air",
            )
