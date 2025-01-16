# Allows code to be run in root directory
import sys
from enum import Enum, auto

from pydantic import BaseModel, Field

from grimoire.ai.ai_provider import AIProvider, load_key

sys.path[0] = sys.path[0].removesuffix("\\tests\\ai")


from grimoire.core.generator.test import TestModule
from grimoire.core.logger import LoggerSettings, LoggingLevel
from grimoire.core.noise.global_seed import GlobalSeed
from grimoire.story.names.name_generator import NamingSchema, NameGenerator


class SettlementSize(Enum):
    Small = auto()
    Medium = auto()
    Large = auto()


class Citizen(BaseModel):
    name: str
    profession: str


class SettlementData(BaseModel):
    size: SettlementSize
    name: str = Field(
        description="The name of the settlement, which should end in town"
    )
    description: str
    citizens: list[Citizen] = Field(
        description="The citizens of the settlement. There should be at least 3."
    )


class AITest(TestModule):
    def test(self):
        ai = AIProvider()
        town: SettlementData = ai.generate(
            context="You generate interesting towns",
            prompt="Generate an interesting town",
            format_type=SettlementData,
        )

        self.log.info(town.model_dump_json(indent=2))

        assert town is not None, "Town is None"
        assert town.name.lower().endswith("town"), "Town name does not end in town"
        assert town.size in SettlementSize, "Town size is not valid"
        assert len(town.citizens) >= 3, "Town has less than 3 citizens"


if __name__ == "__main__":
    AITest().run()
