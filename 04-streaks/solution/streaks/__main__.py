"""This file runs when you type:  python -m streaks ...

It's the front door of the package. It sets up logging, then hands
everything else over to cli.main().
"""

import logging
import sys

from streaks.cli import main
from streaks.storage import LOG_FILE

# Logging is set up here, and only here. Tests import the rest of the
# package directly, so they never write to streaks.log.
logging.basicConfig(
    filename=LOG_FILE,
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s: %(message)s",
)

sys.exit(main(sys.argv[1:]))
