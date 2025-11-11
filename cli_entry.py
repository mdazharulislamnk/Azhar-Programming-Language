# cli_entry.py — stable bootstrap for frozen exe
import os, sys

# Determine base path (inside the frozen exe or source tree)
BASE = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__)

# Ensure the package root is on sys.path so `import azhar.*` works
if BASE not in sys.path:
    sys.path.insert(0, BASE)

from azhar.cli import main  # import the real entry
if __name__ == "__main__":
    raise SystemExit(main())
