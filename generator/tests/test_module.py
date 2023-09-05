# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\generator\\tests')

from generator.module import Module
from generator.benchmarking import Benchmark
import time

class TestModule(Module):
    name : str = 'Test'

    @Module.main
    def test(self):
        self.log.debug('test')
        time.sleep(1)

class TestModule2(Module):
    name : str = 'Test2'

    @Module.main
    def test(self):
        self.log.debug('test2')
        time.sleep(0.4)

TestModule().test()
TestModule2().test()
TestModule2().test()

Benchmark.print_results()