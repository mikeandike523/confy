#!/usr/bin/python3

# just to be absolutely sure that confy will import its own custom utility scripts first
# It may not be necessary though, I always find python include paths to be tricky
import sys
import os
import shutil

CONFY_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0,CONFY_DIR)

# built in imports

# 3rd party imports
import click


# custom utility script imports
# custom utilities will be in <confy dir>/lib
# importing will look like `from lib.<something> import <some symbols>` or `import lib.<something> as <alias>`
from lib.system import (ensure_superuser,
                        read_list_from_file,
                        clear_all_simple_files,
                        run_ln_s,
                        run_chown_R,
                        run_chmod_R,
                        Runner
                        )



@click.group()
def cli():
    pass




@cli.command()
def sync():
    """
    Copy the files in your project to the correct places in /etc/nginx,
    set permissions, make appropriate symlinks, and restart ngin
    """

    ensure_superuser()

    sites = read_list_from_file(os.path.join(os.getcwd(),"sites.txt"))

    clear_all_simple_files("/etc/nginx/sites-available")
    clear_all_simple_files("/etc/nginx/sites-enabled")

    for site in sites:
        shutil.copy(
            os.path.join(os.getcwd(),site),
            os.path.join("/etc/nginx/sites-available",site)
        )
        run_ln_s(
            os.path.join("/etc/nginx/sites-available",site),
            os.path.join("/etc/nginx/sites-enabled",site)
        )

    run_chown_R("/etc/nginx/sites-available","www-data:www-data")
    run_chown_R("/etc/nginx/sites-enabled","www-data:www-data")
    run_chmod_R("/etc/nginx/sites-available","755")
    run_chmod_R("/etc/nginx/sites-enabled","755")

    os.makedirs("/etc/nginx/confy",exist_ok=True)


    if os.path.isdir(os.path.join(os.getcwd(),"res")):
        if os.path.isdir("/etc/nginx/confy/res"):
            shutil.rmtree("/etc/nginx/confy/res")
        shutil.copytree(os.path.join(os.getcwd(),"res"),"/etc/nginx/confy/res")


    run_chown_R("/etc/nginx/confy/res","root:root")
    run_chmod_R("/etc/nginx/confy/res","444")

    Runner("sudo").run(["systemctl", "restart", "nginx"])


if __name__ == "__main__":
    cli()

