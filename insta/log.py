import logging


logger = logging.getLogger('insta')
logger.setLevel(logging.INFO)

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter(
    fmt='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
))
logger.addHandler(_handler)


# Verbosity is an integer for the number of levels to increase (negative
# for decrease).
def adjust_logging_level(verbosity):
    current_level = logger.getEffectiveLevel()
    level = current_level - 10 * verbosity
    # Limit to the [logging.DEBUG, logging.CRITICAL] range
    level = min(max(level, logging.DEBUG), logging.CRITICAL)
    logger.setLevel(level)


def debug_mode():
    return logger.isEnabledFor(logging.DEBUG)
