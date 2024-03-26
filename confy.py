#!/usr/bin/python3

# just to be absolutely sure that confy will import its own custom utility scripts first
import sys
import os

CONFY_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0,CONFY_DIR)

# built in imports

# 3rd party imports
import click


# custom utility script imports
# custom utilities will be in <confy dir>/lib
# importing will look like `from lib.<something> import <some symbols>` or `import lib.<something> as <alias>`

@click.group()
def cli():
    pass



if __name__ == "__main__":
    cli()

