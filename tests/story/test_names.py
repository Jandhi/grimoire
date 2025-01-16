# Allows code to be run in root directory
import sys

from grimoire.core.generator.test import TestModule
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.noise.global_seed import GlobalSeed
from grimoire.story.names.name_generator import NamingSchema, NameGenerator

sys.path[0] = sys.path[0].removesuffix("\\tests\\story")

from grimoire.core.assets.asset_loader import load_assets
from grimoire.story.load_story_types import load_types


class TestNames(TestModule):
    def test(self):
        load_types()
        load_assets("tests\\story")
        schema: NamingSchema = NamingSchema.all()[0]

        self.log.info(schema.rules)

        name_generator = NameGenerator()
        name_generator.set_module_logger_settings(
            LoggerSettings(
                minimum_console_level=LoggingLevel.ERROR,
                minimum_file_level=LoggingLevel.ERROR,
            )
        )

        for index in range(10):
            GlobalSeed.randomize()
            name, args = name_generator.generate_name("name", schema)
            self.log.info(f"Name {index}: {name} with args {args}")


if __name__ == "__main__":
    TestNames().run()
