# pylint:disable=W0401
from pkg_resources import get_distribution, DistributionNotFound
from .handlers import *

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass
