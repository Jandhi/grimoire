import json
import sys
from glob import glob

from colored import Fore, Style

from ...buildings.building_shape import permute_shapes
from ...core.generator.generator_module import GeneratorModule
from ...core.assets.asset import Asset
from ...core.assets.asset_linker import AssetLinker
from ...core.assets.asset_validation_state import AssetValidationState
from ...core.assets.load_types import load_types
from ..logger import LoggerSettings
# Loads all nbt assets from the assets folder


class AssetLoader(GeneratorModule):
    def __init__(self, parent: GeneratorModule):
        super().__init__(parent)

    @GeneratorModule.main
    def load_assets(self, root_directory):
        self.log.info("Loading Types")
        load_types()

        names: list[str] = glob(
            f"{sys.path[0]}/{root_directory}/**/*.json", recursive=True
        )

        for name in self.log.progress(names, "Loading Assets"):
            with open(name, "r") as file:
                path = name.replace("\\", "/")
                data = json.load(file)

                if "type" not in data:
                    self.log.error(f"Could not load {path}. No type given.")
                    continue

                cls = Asset.get_construction_type(data["type"])

                if cls is None:
                    self.log.error(
                        f'Error in file {name}. Could not find class {data["type"]}'
                    )
                    continue

                data["type"] = cls.type_name

                obj, validation_state = cls.construct_unsafe(**data)
                validation_state: AssetValidationState

                if validation_state.is_invalid():
                    self.log.error(
                        f"{Fore.red}Error{Style.reset}: while loading {Fore.light_blue}{path}{Style.reset}. "
                        f"Object is missing the following fields: {validation_state.missing_args}. It will be ignored."
                    )
                    continue

                if len(validation_state.surplus_args) > 0:
                    self.log.warning(
                        f"while loading {Fore.light_blue}{path}{Style.reset}. Object has non-annotated fields: {validation_state.surplus_args}"
                    )

        linker = AssetLinker(self)
        linker.log.settings = self.log.settings
        linker.link_assets()

        # Extra steps for special assets
        permute_shapes()  # varies the building shapes into all rotations and mirrors


def load_assets(
    root_directory,
    logging_settings: LoggerSettings | None = None,
    parent_module: GeneratorModule | None = None,
) -> None:
    loader = AssetLoader(parent_module)
    if logging_settings is not None:
        loader.set_module_logger_settings(logging_settings)
    loader.load_assets(root_directory)
