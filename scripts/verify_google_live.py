"""Convenience adapter; the installed CLI owns the exact verification workflow."""
import sys
from shopextract.cli import main


if __name__ == '__main__':
    main(['taxonomy', 'google', 'verify-live', *sys.argv[1:]])
