import argparse
import sys

from . import log
from .log import logger
from .version import __version__


# ArgumentParser wrapper class with common args predefined.
class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        add = self.add_argument
        add('-q', '--quiet', action='count', default=0,
            help='decrease verbosity (-v takes precedence)')
        add('-v', '--verbose', action='count', default=0,
            help='increase verbosity')
        add('-V', '--version', action='version', version=__version__)


# args is an argparse.Namespace returned by ArgumentParser().parse_args().
def adjust_verbosity(args):
    log.adjust_logging_level(args.verbose if args.verbose else -args.quiet)


# Run function in a sandbox with automated exception handling.
def sandbox(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        logger.error(f'{type(e).__qualname__}: {e}')
        if log.debug_mode():
            raise
        else:
            sys.exit(1)
