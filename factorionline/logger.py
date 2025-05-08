import rich
import inspect
import logging

from rich.logging import RichHandler
from rich.text import Text
from rich.console import Console
from rich.traceback import install
from datetime import datetime
from dataclasses import dataclass
from collections import namedtuple

# Instalar el manejador de excepciones de Rich para mostrar trazas bonitas
install(show_locals=True)

# Configurar el logger con RichHandler
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        show_time=True,
        show_path=True,
        markup=True,
        omit_repeated_times=False,
        tracebacks_extra_lines=2
    )]
)

@dataclass
class LogEventContainer:
    parent:str
    text:str
    


class LogEvent:
    INFO = 0
    DEBUG = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4
    def __init__(self, sender:str, level:str, text:str, parent:LogEventContainer=None):
        self.time = datetime.now()
        self.sender = sender
        self.level = level
        self.text = text
        self.parent = parent



class Log:
    COLORS = [
        'blue',
        'green',
        'yellow',
        'red',
        'white on red'
    ]
    def __init__(self, debug=True):
        self.console = Console()
        self.console.clear()
        self.logger = logging.getLogger('Logger')
        self._debug = debug


    def _log (self, level:int, text:str, parent:any=None, style:str='') -> None:
        if not parent:
            parent = '[bold white]UNKNOWN [/bold white]'.ljust(40)
        else:
            parent = f'[bold white]{parent}[/bold white]'.ljust(40)
        if not style:
            style = f'{self.COLORS[level]}'
        text = f'{parent}[{style}]{text}[/{style}]'
        match (level):
            case LogEvent.INFO:
                self.logger.info(text)
            case LogEvent.DEBUG:
                self.logger.debug(text)
            case LogEvent.WARNING:
                self.logger.warning(text)
            case LogEvent.ERROR:
                self.logger.error(text)
            case LogEvent.CRITICAL:
                self.logger.critical(text)


    def info (self, text:str, parent:any=None, style:str=None) -> None:
        if self._debug:
            self._log(LogEvent.INFO, text, parent, style)

    def debug (self, text:str, parent:any=None, style:str=None) -> None:
        if self._debug:
            self._log(LogEvent.DEBUG, text, parent)

    def warning (self, text:str, parent:any=None, style:str=None) -> None:
        if self._debug:
            self._log(LogEvent.WARNING, text, parent, style)
    
    def error (self, text:str, parent:any=None, style:str=None) -> None:
        if self._debug:
            self._log(LogEvent.ERROR, text, parent, style)
    
    def critical (self, text:str, parent:any=None, style:str=None) -> None:
        if self._debug:
            self._log(LogEvent.CRITICAL, text, parent, style)