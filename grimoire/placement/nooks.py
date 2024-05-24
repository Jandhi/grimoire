from typing import Any, Callable, Iterable

from gdpc.editor import Editor
from glm import ivec2

from grimoire.core.noise.rng import RNG
from grimoire.core.styling.materials.material import Material
from grimoire.core.utils.shapes import Shape2D

from ..core.maps import DevelopmentType, Map


class Nook:

    def __init__(
        self,
        styles: str | Iterable[str],
        terraformers: (
            Iterable[
                Callable[
                    [
                        Editor,
                        Shape2D,
                        Material | None,
                        dict[ivec2, set[DevelopmentType]],
                        dict[DevelopmentType, Material] | None,
                        Map,
                        RNG,
                    ],
                    Any,
                ]
            ]
            | None
        ) = None,
        surface: Material | None = None,
        edging: dict[set[DevelopmentType], Material] | None = None,
        decorators: (
            Iterable[
                Callable[
                    [
                        Editor,
                        Shape2D,
                        dict[ivec2, set[DevelopmentType]],
                        Map,
                        RNG,
                    ],
                    Any,
                ]
            ]
            | None
        ) = None,
    ) -> None:
        self.styles = styles
        self.terraformers = terraformers
        self.surface = surface
        self.edging = edging
        self.decorators = decorators

    def manifest(
        self,
        editor: Editor,
        area: Shape2D,
        edges: dict[ivec2, set[DevelopmentType]],
        city_map: Map,
        rng: RNG,
    ):
        # terraform the Nook
        if self.terraformers is not None:
            for terraformer in self.terraformers:
                terraformer(
                    editor, area, self.surface, edges, self.edging, city_map, rng
                )

        if self.decorators is not None:
            for decorator in self.decorators:
                decorator(editor, area, edges, city_map, rng)
