from logs.logger import Logger, LoggerSettings, LoggingLevel
from generator.settings import GeneratorSettings
from generator.benchmarking import Benchmark
from colored import Fore, Style


class ModuleLogger(Logger):
    def __init__(self, settings: LoggerSettings, module : 'Module') -> None:
        super().__init__(settings)
        self.module = module

    def format(self, text: str, level: LoggingLevel, is_in_console: bool = False) -> str:
        if not self.settings.print_classname:
            return super().format(text, level, is_in_console)

        name = f'{Fore.green}{self.module.get_name()}{Style.reset}' if is_in_console else self.module.get_name()
        return super().format(f'{name}: {text}', level, is_in_console)

class Module:
    name : str = None
    __logger : Logger = None

    @property
    def log(self) -> Logger:
        if not self.__logger:
            self.__logger = ModuleLogger(GeneratorSettings.logger_settings, self)

        return self.__logger
    
    '''
    Decorator used to determine the main generator function for the module
    Benchmarking will begin when this is called and end when it is finished
    '''
    class main:
        def __init__(self, func) -> None:
            self.func = func

        # When main is bound to the owner, this allows for us to find the owners class
        def __set_name__(self, owner : 'Module', name):
            # Owner is actually a type which inherits from Module, but this type annotation will do
            func = self.func

            def my_func(self, *args, **kwargs):
                Benchmark.timed(
                    func=func, 
                    log=self.log, 
                    class_name=owner.get_name()
                )(self, *args, **kwargs)

            setattr(owner, name, my_func)

    @classmethod
    def get_name(cls) -> str:
        if cls.name:
            return cls.name
        
        return cls.__name__