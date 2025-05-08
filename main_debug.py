from factorionline.factorionline import Factorionline
import subprocess
import sys

from rich import print
from rich.text import Text

from factorionline import Log

logger = Log()
name = 'main_debug' # For log

def run_pytest():
    result = subprocess.run(['pytest'], capture_output=True, text=True)
    if result.returncode != 0:
        logger.info(result.stdout, name, style='bold white')
        logger.critical('Tests Fails.', name)
        sys.exit(1)
    logger.info('Tests passed.', name, style='bold green')

if __name__ == '__main__':
    run_pytest()
    try:
        app = Factorionline(logger)
        app.run()
    except KeyboardInterrupt:
        logger.warning('KeyInterrupt. Stopping app.', name)
        app.stop()
    except Exception as e:
        app.stop()
        raise e