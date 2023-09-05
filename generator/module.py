from logs.logger import Logger, LoggerSettings
from generator.settings import GeneratorSettings
from generator.benchmarking import Benchmark

class ModuleLogger(Logger):
    def __init__(self, settings: LoggerSettings | None = None) -> None:
        super().__init__(settings)

    def format():
        pass

class Module:
    name : str = None
    __logger : Logger = None

    @property
    def log(self) -> Logger:
        if not self.__logger:
            self.__logger = Logger(GeneratorSettings.logger_settings)

        return self.__logger
    
    '''
    Decorator used to determine the main generator function for the module
    Benchmarking will begin when this is called and end when it is finished
    '''
    class main:
        def __init__(self, func) -> None:
            self.func = func

        def __set_name__(self, owner : 'Module', name):
            # Owner is a type which inherits from Module, but this type annotation will do
            func = self.func

            def my_func(self, *args, **kwargs):
                Benchmark.time_function(
                    func=func, 
                    log=self.log.info, 
                    class_name=owner.get_name()
                )(self, *args, **kwargs)

            setattr(owner, name, my_func)

    @classmethod
    def get_name(cls) -> str:
        if cls.name:
            return cls.name
        
        return cls.__name__