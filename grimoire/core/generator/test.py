import abc
from abc import ABC

from gdpc import Editor, Rect, WorldSlice

from grimoire.core.generator.generator_module import GeneratorModule
from grimoire.core.maps import Map


def run_test(cls):
    mod: TestModule = cls()
    mod.run_test()
    return cls


class TestModule(GeneratorModule):
    catch_errors: bool = False

    def __init__(self, parent: GeneratorModule = None):
        super().__init__(parent)

    def __init__(self):
        super().__init__(None)

    @abc.abstractmethod
    def test(self):
        pass

    @GeneratorModule.main
    def run_test(self):
        if self.catch_errors:
            try:
                self.test()
            except Exception as e:
                self.log.error(f"Test {self.get_name()} failed: {e}")
        else:
            self.test()


class EditingTestModule(TestModule, ABC):
    editor: Editor
    build_rect: Rect
    world_slice: WorldSlice
    build_map: Map

    def load_world(self):
        self.editor = Editor(buffering=True, caching=True)
        area = self.editor.getBuildArea()
        self.editor.transform = (area.begin.x, 0, area.begin.z)

        self.log.info("Loading world slice...")

        self.build_rect = area.toRect()
        self.world_slice = self.editor.loadWorldSlice(self.build_rect)

        self.log.info("World slice loaded!")

        self.build_map = Map(self.world_slice)
