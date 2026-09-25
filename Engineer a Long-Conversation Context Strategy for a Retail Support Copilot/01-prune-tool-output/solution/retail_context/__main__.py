import sys

from retail_context import __version__
from retail_context.run import main

if len(sys.argv) >= 2 and sys.argv[1] == "--version":
    print(__version__)
    sys.exit(0)

main()
