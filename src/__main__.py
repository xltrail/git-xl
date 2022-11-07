"""Call cli with `python -m gitxl ...`"""
import sys
from .cli import CommandParser

if __name__ == "__main__":
    command_parser = CommandParser(sys.argv[1:])
    command_parser.execute()
