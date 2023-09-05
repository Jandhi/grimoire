# Allows code to be run in root directory
import sys
sys.path[0] = sys.path[0].removesuffix('\\logs\\tests')

from logs.logger import Logger, LoggingLevel

log = Logger()

log.settings.print_timestamp = True
log.settings.output_file = 'logs/tests/log.txt'
log.settings.minimum_console_level = LoggingLevel.ERROR

log.info('Test')
log.error('Test')