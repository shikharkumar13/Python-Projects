"""This file runs when you type:  python -m wrapped ..."""

import sys

from wrapped.cli import main

sys.exit(main(sys.argv[1:]))
