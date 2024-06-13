import inspect
from typing import TypeVar, Callable

from colored import Fore, Style
from glm import ivec3, ivec2

from .benchmarking import Benchmark
from .settings import GeneratorSettings
from ..logger import Logger, LoggerSettings, LoggingLevel
from ..noise.global_seed import GlobalSeed
from ..noise.rng import RNG
from ..utils.clone import clone
from ..utils.strings import camel_to_snake_case


class ModuleLogger(Logger):
    def __init__(self, settings: LoggerSettings, module: "GeneratorModule") -> None:
        super().__init__(settings)
        self.module = module

    def format(
        self, text: str, level: LoggingLevel, is_in_console: bool = False
    ) -> str:
        if not self.settings.print_classname:
            return super().format(text, level, is_in_console)

        name = (
            f"{Fore.green}{self.module.get_name()}{Style.reset}"
            if is_in_console
            else self.module.get_name()
        )
        return super().format(f"{name}: {text}", level, is_in_console)


T = TypeVar("T")

_modules: dict[str, type] = dict()


class GeneratorModule:
    name: str = None
    _main: Callable = None
    _logger: Logger = None
    rng: RNG

    def __init__(self, parent: "GeneratorModule"):
        self.parent = parent

    def __init_subclass__(cls, **kwargs):
        cls.name = cls.name or camel_to_snake_case(cls.__name__)
        _modules[cls.name] = cls

    def init_rng_from_world_seed(self):
        self.__setattr__("rng", RNG(GlobalSeed.get(), self.get_name()))

    def run(self, *args, **kwargs):
        self._main(*args, **kwargs)

    @property
    def log(self) -> Logger:
        if not self._logger:
            self._logger = ModuleLogger(
                settings=GeneratorSettings.logger_settings, module=self
            )

        return self._logger

    def set_module_logger_settings(self, logger_settings: LoggerSettings):
        self.log.settings = logger_settings

    """
    Decorator used to determine the main generator function for the module
    Benchmarking will begin when this is called and end when it is finished
    
    The main class must
    """

    class MainClass:
        def __init__(self, func: Callable):
            self.func = func

        # When main is bound to the owner, this allows for us to find the owners class
        def __set_name__(self, owner: "GeneratorModule", name):
            # Owner is actually a type which inherits from Module, but this type annotation will do
            func = self.func

            def my_func(self, *args, **kwargs):
                _callstack.append(self)

                self.init_rng_from_world_seed()

                val = Benchmark.timed(
                    func=func, log=self.log, class_name=owner.get_name()
                )(self, *args, **kwargs)

                _callstack.pop(-1)

                return val

            my_func.__annotations__ = func.__annotations__

            setattr(owner, name, my_func)
            owner._main = my_func

    @staticmethod
    def main(func: T) -> T:
        return GeneratorModule.MainClass(func)

    @classmethod
    def get_name(cls) -> str:
        return cls.name

    def raise_error(self, description: str):
        self.log.error(description)
        raise RuntimeError(description)


_callstack: list[GeneratorModule] = []


def find_module(name: str) -> type | None:
    if name not in _modules:
        return None

    return _modules[name]


def run_module(name: str, *args, **kwargs):
    module = find_module(name)

    if module is None:
        return False

    module.run(*args, **kwargs)
    return True


def top_module() -> GeneratorModule | None:
    return _callstack[-1] if len(_callstack) > 0 else None


class ModuleCall:
    def __init__(self, module: type, arguments: dict[str, any]):
        self.module = module
        self.arguments = arguments

    def run(self):
        return self.module(top_module()).run(**self.arguments)

    def clone(self):
        return ModuleCall(
            self.module,
            {name: clone(value) for (name, value) in self.arguments.items()},
        )
